import os
import json
import numpy as np
from datetime import datetime
from scipy.interpolate import griddata
import plotly.graph_objs as go

# === Шлях до вхідного файлу ===
input_file_path = "E:\\Cord_parser\\input_data\\data.txt"

# === Збір координат та корекція висоти ===
points = []
with open(input_file_path, "r", encoding="utf-8") as file:
    for line in file:
        try:
            data = json.loads(line.strip())
            if data.get("errorFlags", 1) == 0 and data.get("sats", 0) >= 4:
                lon = data["lng"]
                lat = data["lat"]
                alt = data["altitude"]
                dist = data["distance"]
                corrected_alt = alt #  -  dist / 100  # Корекція висоти
                points.append((lon, lat, corrected_alt))
        except (json.JSONDecodeError, KeyError):
            continue

if not points:
    print("❌ Немає валідних точок.")
    exit()

# === Розпакування даних ===
lons, lats, alts = zip(*points)

# === Створення координатної сітки ===
grid_x, grid_y = np.mgrid[
    min(lons):max(lons):300j,
    min(lats):max(lats):300j
]

# === Інтерполяція висот ===
grid_z = griddata((lons, lats), alts, (grid_x, grid_y), method='cubic')

# Визначення розширеного діапазону по осі Z для відображення
z_min = np.nanmin(grid_z)
z_max = np.nanmax(grid_z)
z_range = [z_min - 20, z_max + 20]

# === Побудова 3D поверхні ===
surface = go.Surface(
    z=grid_z,
    x=grid_x,
    y=grid_y,
    colorscale='Viridis',
    colorbar=dict(title='Висота, м (коригована)'),
)

fig = go.Figure(data=[surface])

fig.update_layout(
    title="3D Рельєф місцевості (коригований altitude - distance)",
    scene=dict(
        xaxis_title='Довгота',
        yaxis_title='Широта',
        zaxis_title='Висота, м',
        zaxis=dict(range=z_range),
        camera=dict(eye=dict(x=1.5, y=1.5, z=0.6)),
    ),
    margin=dict(l=0, r=0, t=40, b=0),
)

# === Збереження в HTML ===
output_dir = "E:\\Cord_parser\\Result"
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
os.makedirs(output_dir, exist_ok=True)
html_path = os.path.join(output_dir, f"terrain_3d_corrected_{timestamp}.html")
fig.write_html(html_path)

print(f"✅ 3D рельєф (коригований) збережено як {html_path}")
fig.show()
