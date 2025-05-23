import os
import json
import numpy as np
import folium  # type: ignore
import branca.colormap as cm  # type: ignore
import plotly.graph_objs as go

from datetime import datetime
from scipy.interpolate import griddata

# === Шлях до вхідного файлу ===
input_file_path = "E:\\Cord_parser\\input_data\\data.txt"

# === Підготовка папки для результатів ===
base_dir = "E:\\Cord_parser\\Result"
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
folder_path = os.path.join(base_dir, timestamp)
os.makedirs(folder_path, exist_ok=True)

# === Збір даних ===
folium_points = []
plotly_points = []
seen_coords = set()

print(f"Читання з файлу: {input_file_path}")

with open(input_file_path, "r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            lat = data["lat"]
            lon = data["lng"]
            alt = data["altitude"]
            prox = data.get("proximity", 0)
            sats = data.get("sats", 0)
            error_flags = data.get("errorFlags", 1)
            dist = data.get("distance", 0)

            # Для 2D мапи
            coord = (lat, lon)
            if coord not in seen_coords:
                folium_points.append({"lat": lat, "lon": lon, "alt": alt})
                seen_coords.add(coord)

            # Для 3D рельєфу
            if error_flags == 0 and sats >= 4:
                corrected_alt = alt  # або alt - dist / 100 для корекції
                plotly_points.append((lon, lat, corrected_alt))

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Помилка: {e}")
            continue

# === Перевірка наявності точок ===
if not folium_points and not plotly_points:
    print("❌ Немає валідних даних для побудови.")
    exit()

# === Зберігаємо точки для folium у JSON ===
json_path = os.path.join(folder_path, "points.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(folium_points, f, ensure_ascii=False, indent=4)
print(f"✅ Точки збережено у {json_path}")

# === Побудова 2D-карти (Folium) ===
if folium_points:
    altitudes = [p["alt"] for p in folium_points]
    min_alt, max_alt = min(altitudes), max(altitudes)

    colormap = cm.LinearColormap(['green', 'red'], vmin=min_alt, vmax=max_alt)
    m = folium.Map(location=[folium_points[0]["lat"], folium_points[0]["lon"]], zoom_start=17)

    for p in folium_points:
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

    map_path = os.path.join(folder_path, "map.html")
    m.save(map_path)
    print(f"✅ 2D-карта збережена як {map_path}")
else:
    print("⚠️ Немає точок для побудови 2D-карти.")

# === Побудова 3D рельєфу (Plotly) ===
if plotly_points:
    lons, lats, alts = zip(*plotly_points)

    grid_x, grid_y = np.mgrid[
        min(lons):max(lons):300j,
        min(lats):max(lats):300j
    ]
    grid_z = griddata((lons, lats), alts, (grid_x, grid_y), method='cubic')

    z_min = np.nanmin(grid_z)
    z_max = np.nanmax(grid_z)
    z_range = [z_min - 20, z_max + 20]

    surface = go.Surface(
        z=grid_z,
        x=grid_x,
        y=grid_y,
        colorscale='Viridis',
        colorbar=dict(title='Висота, м (коригована)'),
    )

    fig = go.Figure(data=[surface])
    fig.update_layout(
        title="3D Рельєф місцевості",
        scene=dict(
            xaxis_title='Довгота',
            yaxis_title='Широта',
            zaxis_title='Висота, м',
            zaxis=dict(range=z_range),
            camera=dict(eye=dict(x=1.5, y=1.5, z=0.6)),
        ),
        margin=dict(l=0, r=0, t=40, b=0),
    )

    terrain_path = os.path.join(folder_path, "terrain_3d.html")
    fig.write_html(terrain_path)
    print(f"✅ 3D рельєф збережено як {terrain_path}")
    fig.show()
else:
    print("⚠️ Немає точок для побудови 3D рельєфу.")
