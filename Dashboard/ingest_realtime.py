import os
import json
import requests
import datetime

# Hanoi center coordinates
HANOI_LAT = 21.0285
HANOI_LON = 105.8542

# Baseline district areas (to compute concretization rates dynamically)
DISTRICT_BASELINES = {
    "Ba Dinh": {"urban": 6.66, "total": 11.46, "base_aqi_factor": 1.12},
    "Hoan Kiem": {"urban": 3.56, "total": 5.93, "base_aqi_factor": 1.15},
    "Tay Ho": {"urban": 8.81, "total": 27.72, "base_aqi_factor": 0.95},
    "Long Bien": {"urban": 22.96, "total": 56.90, "base_aqi_factor": 1.02},
    "Cau Giay": {"urban": 9.11, "total": 15.91, "base_aqi_factor": 1.20},
    "Dong Da": {"urban": 7.12, "total": 9.15, "base_aqi_factor": 1.18},
    "Hai Ba Trung": {"urban": 8.40, "total": 12.87, "base_aqi_factor": 1.14},
    "Hoang Mai": {"urban": 18.36, "total": 37.98, "base_aqi_factor": 1.13},
    "Thanh Xuan": {"urban": 5.58, "total": 8.35, "base_aqi_factor": 1.16},
    "Soc Son": {"urban": 52.54, "total": 304.05, "base_aqi_factor": 0.72},
    "Dong Anh": {"urban": 49.47, "total": 190.46, "base_aqi_factor": 0.98},
    "Gia Lam": {"urban": 30.16, "total": 118.39, "base_aqi_factor": 0.95},
    "Tu Liem": {"urban": 28.72, "total": 74.72, "base_aqi_factor": 1.06},
    "Thanh Tri": {"urban": 26.08, "total": 70.44, "base_aqi_factor": 1.04},
    "Me Linh": {"urban": 27.26, "total": 143.60, "base_aqi_factor": 0.88},
    "Ha Dong": {"urban": 17.22, "total": 34.17, "base_aqi_factor": 1.08},
    "Son Tay": {"urban": 20.05, "total": 122.74, "base_aqi_factor": 0.80},
    "Ba Vi": {"urban": 43.12, "total": 419.17, "base_aqi_factor": 0.60},
    "Phuc Tho": {"urban": 21.85, "total": 118.51, "base_aqi_factor": 0.74},
    "Dan Phuong": {"urban": 18.45, "total": 72.79, "base_aqi_factor": 0.78},
    "Hoai Duc": {"urban": 28.33, "total": 83.94, "base_aqi_factor": 0.96},
    "Quoc Oai": {"urban": 25.84, "total": 151.25, "base_aqi_factor": 0.76},
    "Thach That": {"urban": 29.87, "total": 172.83, "base_aqi_factor": 0.82},
    "Chuong My": {"urban": 42.78, "total": 229.30, "base_aqi_factor": 0.78},
    "Thanh Oai": {"urban": 27.20, "total": 125.96, "base_aqi_factor": 0.84},
    "Thuong Tin": {"urban": 35.10, "total": 139.87, "base_aqi_factor": 0.88},
    "Phu Xuyen": {"urban": 28.12, "total": 180.15, "base_aqi_factor": 0.82},
    "Ung Hoa": {"urban": 25.00, "total": 179.12, "base_aqi_factor": 0.74},
    "My Duc": {"urban": 25.47, "total": 235.32, "base_aqi_factor": 0.66}
}

def fetch_aqi():
    token = os.getenv("WAQI_API_TOKEN")
    if not token:
        print("WAQI_API_TOKEN not found. Using fallback mock API data.")
        return 115 # typical Hanoi average
    
    try:
        url = f"https://api.waqi.info/feed/geo:{HANOI_LAT};{HANOI_LON}/?token={token}"
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("status") == "ok":
            aqi = data["data"]["aqi"]
            print(f"Successfully fetched live AQI: {aqi}")
            return aqi
    except Exception as e:
        print(f"Error fetching AQI: {e}. Using fallback mock data.")
    return 115

def fetch_weather():
    try:
        # Fetch current air temp, soil temp (LST proxy), and rainfall
        url = f"https://api.open-meteo.com/v1/forecast?latitude={HANOI_LAT}&longitude={HANOI_LON}&current=temperature_2m,soil_temperature_0cm,rain&forecast_days=1"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        current = data.get("current", {})
        temp = current.get("temperature_2m", 32.0)
        soil_temp = current.get("soil_temperature_0cm", 34.0)
        rain = current.get("rain", 0.0)
        
        print(f"Successfully fetched weather: Temp={temp}°C, SoilTemp={soil_temp}°C, Rain={rain}mm")
        return {
            "air_temp": temp,
            "soil_temp": soil_temp,
            "rain": rain
        }
    except Exception as e:
        print(f"Error fetching weather: {e}. Using fallback mock data.")
        return {
            "air_temp": 32.0,
            "soil_temp": 34.0,
            "rain": 0.0
        }

def main():
    base_aqi = fetch_aqi()
    weather = fetch_weather()
    
    current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    # Generate district-specific metrics using models
    districts_realtime = {}
    for name, info in DISTRICT_BASELINES.items():
        concrete_rate = (info["urban"] / info["total"]) * 100
        
        # 1. District AQI Model
        district_aqi = int(base_aqi * info["base_aqi_factor"])
        
        # 2. District LST Model (UHI effect: LST increases with concrete cover)
        # LST = base soil temp + UHI scale factor based on concrete rate
        lst_offset = (concrete_rate / 100.0) * 8.0  # concrete areas are up to 8°C hotter than rural areas
        district_lst = round(weather["soil_temp"] + lst_offset - 2.0, 1)
        
        # 3. Dynamic Rain-induced Flood Points warning
        # Base flood points scale with concrete rate. If active rain is falling, we increase it!
        base_floods = int(concrete_rate / 6.0) # e.g. 90% concrete -> 15 points
        if weather["rain"] > 10.0:
            active_floods = base_floods * 2  # heavy rain doubles flood points
        elif weather["rain"] > 1.0:
            active_floods = int(base_floods * 1.4)
        else:
            active_floods = base_floods
            
        districts_realtime[name] = {
            "aqi": max(10, district_aqi),
            "lst": district_lst,
            "flood_points": max(1, active_floods)
        }
        
    payload = {
        "last_updated": current_time,
        "metro": {
            "aqi": base_aqi,
            "lst": round(weather["soil_temp"], 1),
            "air_temp": weather["air_temp"],
            "rain_mm": weather["rain"]
        },
        "districts": districts_realtime
    }
    
    # Save file
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    file_path = os.path.join(data_dir, "realtime_metrics.json")
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully updated realtime data at {file_path}")

if __name__ == "__main__":
    main()
