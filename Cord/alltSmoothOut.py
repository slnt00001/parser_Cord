import json

def smooth_altitudes(points, window=3):
    altitudes = [p['altitude'] for p in points]
    smoothed = []
    n = len(altitudes)
    for i in range(n):
        start = max(0, i - window//2)
        end = min(n, i + window//2 + 1)
        window_values = altitudes[start:end]
        avg = sum(window_values) / len(window_values)
        smoothed.append(avg)
    return smoothed

def limit_slope(altitudes, max_diff=2):
    limited = [altitudes[0]]
    for i in range(1, len(altitudes)):
        diff = altitudes[i] - limited[-1]
        if abs(diff) > max_diff:
            diff = max_diff if diff > 0 else -max_diff
        limited.append(limited[-1] + diff)
    return limited

def normalize_altitudes(altitudes, new_min=312, new_max=318):
    old_min = min(altitudes)
    old_max = max(altitudes)
    if old_max == old_min:
        # Всі значення однакові, просто повертаємо new_min
        return [new_min] * len(altitudes)
    normalized = []
    for a in altitudes:
        # Лінійне масштабування в новий діапазон
        norm = (a - old_min) / (old_max - old_min) * (new_max - new_min) + new_min
        normalized.append(norm)
    return normalized

# --- Основний код ---

with open('E:\\Cord_parser\\input_data\\data.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

points = []
for line in lines:
    try:
        point = json.loads(line)
        points.append(point)
    except json.JSONDecodeError:
        pass

if not points:
    print("Немає даних для обробки.")
    exit()

smoothed_altitudes = smooth_altitudes(points, window=5)
limited_altitudes = limit_slope(smoothed_altitudes, max_diff=2)
normalized_altitudes = normalize_altitudes(limited_altitudes, new_min=312, new_max=318)

with open('E:\\Cord_parser\\input_data\\dataSmouthOut.txt', 'w', encoding='utf-8') as f_out:
    for point, alt in zip(points, normalized_altitudes):
        point['altitude'] = alt
        f_out.write(json.dumps(point, ensure_ascii=False) + '\n')

print(f"Оброблено {len(points)} точок, записано в output.txt")
