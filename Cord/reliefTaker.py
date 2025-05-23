import math
import requests
import json
import random
from collections import OrderedDict
from shapely.geometry import Point, Polygon


polygon_coords = [
    (49.837281417094495, 24.012578924757676),  # верхній лівий
    (49.83785350388194, 24.013998149938672),  # верхній правий
    (49.83733989738779, 24.01491670401415),  # нижній правий
    (49.83666101310618, 24.01407699578206), # нижній лівий
]


# Створення полігону
park_polygon = Polygon(polygon_coords)

def meters_to_lat(m):
    return m / 111320

def meters_to_lng(m, lat):
    return m / (111320 * math.cos(math.radians(lat)))

step_m = 7.5
avg_lat = sum(p[0] for p in polygon_coords) / len(polygon_coords)
lat_step = meters_to_lat(step_m)
lng_step = meters_to_lng(step_m, avg_lat)

min_lat = min(p[0] for p in polygon_coords)
max_lat = max(p[0] for p in polygon_coords)
min_lng = min(p[1] for p in polygon_coords)
max_lng = max(p[1] for p in polygon_coords)

points_inside = []
lat = min_lat
while lat <= max_lat:
    lng = min_lng
    while lng <= max_lng:
        pt = Point(lat, lng)
        if park_polygon.contains(pt):
            points_inside.append((lat, lng))
        lng += lng_step
    lat += lat_step

print(f"Знайдено точок всередині парку: {len(points_inside)}")

def get_elevations(points):
    elevations = []
    batch_size = 100
    url = "https://api.opentopodata.org/v1/srtm90m"

    for i in range(0, len(points), batch_size):
        batch = points[i:i+batch_size]
        locations = "|".join(f"{lat},{lng}" for lat, lng in batch)
        params = {
            "locations": locations
        }
        try:
            r = requests.get(url, params=params)
            if r.status_code == 200:
                data = r.json()
                elevations.extend([result['elevation'] for result in data['results']])
            else:
                print(f"Помилка запиту: {r.status_code}")
                elevations.extend([None] * len(batch))
        except Exception as e:
            print(f"Помилка при запиті: {e}")
            elevations.extend([None] * len(batch))
    return elevations

elevations = get_elevations(points_inside)

data = []
for (lat, lng), alt in zip(points_inside, elevations):
    distance_val = round(random.uniform(36, 38), 2)
    point_dict = OrderedDict([
        ("distance", distance_val),
        ("altitude", alt if alt is not None else 0),
        ("lat", lat),
        ("lng", lng),
        ("sats", 5),
        ("errorFlags", 0),
    ])
    data.append(point_dict)

with open("E:\\Cord_parser\\input_data\\data.txt", "w", encoding="utf-8") as f:
    for point in data:
        f.write(json.dumps(point, ensure_ascii=False) + "\n")

print("Файл data.txt з точками успішно збережено.")
