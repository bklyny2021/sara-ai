#!/usr/bin/env python3
"""
SARA WEATHER - online weather tool (free, no API key).
Uses Open-Meteo (free, no key) + IP-based geolocation.
Works wherever Boo is - detects location automatically.
"""
import json
import urllib.request
import urllib.parse

def get_location():
    """Get approximate location from IP (free, no key)"""
    try:
        req = urllib.request.Request("http://ip-api.com/json/", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
        if data.get("status") == "success":
            return {
                "city": data.get("city", "Unknown"),
                "region": data.get("regionName", ""),
                "country": data.get("country", ""),
                "lat": data.get("lat"),
                "lon": data.get("lon"),
            }
    except Exception as e:
        return None
    return None

def get_weather(lat=None, lon=None, city=None):
    """Get current weather from Open-Meteo (free, no key).
    Defaults to Boo's location (Knightdale, NC) so it's always right.
    Reports in Fahrenheit (US)."""
    # Boo's real location (Knightdale, NC) - use this by default so weather is always correct
    if lat is None or lon is None:
        lat, lon = 35.7877, -78.4806  # Knightdale, NC
        city = city or "Knightdale, NC"
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m&temperature_unit=fahrenheit&wind_speed_unit=mph&timezone=auto"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
        current = data.get("current", {})
        temp = current.get("temperature_2m")
        feels = current.get("apparent_temperature")
        humidity = current.get("relative_humidity_2m")
        precip = current.get("precipitation")
        wind = current.get("wind_speed_10m")
        code = current.get("weather_code")
        
        desc = weather_code_desc(code)
        place = city or "Knightdale, NC"
        
        return (f"🌤️ Current weather in {place}:\n"
                f"   Temperature: {temp}°F ({feels}°F feels like)\n"
                f"   Conditions: {desc}\n"
                f"   Humidity: {humidity}%\n"
                f"   Precipitation: {precip} mm\n"
                f"   Wind: {wind} mph")
    except Exception as e:
        return f"❌ Weather error: {e}"

def weather_code_desc(code):
    """Convert WMO weather code to description"""
    codes = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Light rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Light snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Light showers", 81: "Moderate showers", 82: "Violent showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Thunderstorm with heavy hail",
    }
    return codes.get(code, f"Code {code}")

if __name__ == "__main__":
    print(get_weather())
