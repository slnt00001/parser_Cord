import os
import json
import folium  # type: ignore
import branca.colormap as cm  # type: ignore

from datetime import datetime

# === Замість COM-порту: шлях до вхідного файлу з даними ===
input_file_path = "E:\\Cord_parser\\input_data\\data.txt"

# === Збір точок ===
points = []
seen_coords = set()

print(f"Читання з файлу: {input_file_path}")

with open(input_file_path, "r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()
        if not line:
            continue

        print("Отримано:", repr(line))

        try:
            data = json.loads(line)
            lat = data["lat"]
            lon = data["lng"]
            alt = data["altitude"]
            prox = data.get("proximity", 0)


            coord = (lat, lon)
            if coord in seen_coords:
                print(f"Точка ({lat}, {lon}) вже є, пропускаємо")
            else:
                print(f"Lat: {lat}, Lon: {lon}, Alt: {alt}, Prox: {prox}")
                points.append({"lat": lat, "lon": lon, "alt": alt})
                seen_coords.add(coord)

        except json.JSONDecodeError as e:
            print("JSON помилка:", e)

# === Перевірка та генерація ===
if not points:
    print("Немає зібраних точок.")
    exit()

# Створюємо папку з поточним часом
base_dir = "E:\\Cord_parser\\Result"
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
folder_path = os.path.join(base_dir, timestamp)
os.makedirs(folder_path, exist_ok=True)

# Шляхи до файлів
json_path = os.path.join(folder_path, "points.json")
map_path = os.path.join(folder_path, "map.html")

# Зберігаємо точки у JSON-файл
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(points, f, ensure_ascii=False, indent=4)
print(f"Точки збережено у {json_path}")

# Побудова карти
altitudes = [p["alt"] for p in points]
min_alt, max_alt = min(altitudes), max(altitudes)

colormap = cm.LinearColormap(['white', 'black'], vmin=min_alt, vmax=max_alt)

m = folium.Map(location=[points[0]["lat"], points[0]["lon"]], zoom_start=17)

for p in points:
    color = colormap(p["alt"])
    folium.Circle(
        location=[p["lat"], p["lon"]],
        radius=0.1,
        popup=f"Alt: {p['alt']} м",
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.8
    ).add_to(m)

colormap.caption = "Висота (м)"
colormap.add_to(m)

# Зберігаємо карту
m.save(map_path)
print(f"Карта збережена як {map_path}")
