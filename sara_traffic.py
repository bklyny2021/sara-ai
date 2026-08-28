#!/usr/bin/env python3
"""SARA TRAFFIC & MAPS - drive time/distance between two places, plus a route map link.
Uses free OpenRouteService/OSRM-style APIs (no API key) so it works offline-ish.
Returns the drive time + a clickable OpenStreetMap route link, like Ada's maps widget."""
import json
import urllib.request
import urllib.parse

# Nominatim geocoder (free, no key) -> lat/lon
NOMINATIM = "https://nominatim.openstreetmap.org/search"
# OSRM routing (free, no key) -> time/distance
OSRM = "https://router.project-osrm.org/route/v1/driving/"

def _geocode(place):
    """Turn a place name into (lat, lon). Returns None if not found."""
    q = urllib.parse.quote(place)
    url = f"{NOMINATIM}?q={q}&format=json&limit=1"
    req = urllib.request.Request(url, headers={"User-Agent": "sara-agent/1.0"})
    with urllib.request.urlopen(req, timeout=12) as r:
        data = json.load(r)
    if data:
        return float(data[0]["lat"]), float(data[0]["lon"])
    return None

def drive_time(origin, destination):
    """Return drive time + distance + a route map link between two places."""
    o = _geocode(origin)
    d = _geocode(destination)
    if not o or not d:
        return f"Couldn't locate one of those places ('{origin}' / '{destination}')."
    # OSRM: lon,lat order
    coords = f"{o[1]},{o[0]};{d[1]},{d[0]}"
    url = f"{OSRM}/{coords}?overview=full&geometries=geojson"
    req = urllib.request.Request(url, headers={"User-Agent": "sara-agent/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.load(r)
    route = data.get("routes", [])
    if not route:
        return "No route found between those two places."
    r0 = route[0]
    secs = r0.get("duration", 0)
    meters = r0.get("distance", 0)
    mins = int(secs // 60)
    km = meters / 1000
    # Build a route map link (OpenStreetMap) - view of the route
    map_url = f"https://www.openstreetmap.org/directions?from={o[0]}%2C{o[1]}&to={d[0]}%2C{d[1]}"
    return (
        f"🚗 {origin} → {destination}\n"
        f"⏱ Drive time: about {mins} min ({secs/60:.1f})\n"
        f"📍 Distance: {km:.1f} km ({meters/1609:.1f} miles)\n"
        f"🗺 Route map: {map_url}"
    )

if __name__ == "__main__":
    import sys
    o = sys.argv[1] if len(sys.argv) > 1 else "Atlanta, GA"
    d = sys.argv[2] if len(sys.argv) > 2 else "Statesboro, GA"
    print(drive_time(o, d))
