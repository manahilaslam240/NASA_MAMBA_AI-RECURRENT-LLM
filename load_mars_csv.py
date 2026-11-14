import csv
import json
import random

real_telemetry_logs = []
script_lines = []

# Reads your newly moved mars-weather.csv file directly!
with open("mars-weather.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for i, row_data in enumerate(reader):
        try:
            min_temp = float(row_data.get("min_temp", -75.0))
            max_temp = float(row_data.get("max_temp", -10.0))
            pressure = float(row_data.get("pressure", 730.0))
        except (ValueError, TypeError):
            continue

        # Map real Mars measurements to your 9 game meters
        # [O2, Water, Food, Power, Shield, Suit, Thermal, Mass, Fuel]
        o2_val = round(random.uniform(0.95, 0.99), 3)
        water_val = round(max(10.0, 95.0 - (i * 0.04)), 2)
        food_val = round(max(10.0, 98.0 - (i * 0.03)), 2)
        power_val = round(random.uniform(80.0, 98.0), 1)
        shield_val = 95.0 if pressure > 720 else 82.0
        suit_val = 92.0 if min_temp < -80 else 98.5
        mass_val = round(max(2000.0, 4800.0 - (i * 0.5)), 1)
        fuel_val = round(max(100.0, 1400.0 - (i * 0.6)), 1)

        meter_row = [o2_val, water_val, food_val, power_val, shield_val, suit_val, min_temp, mass_val, fuel_val]
        line = f"ARIA: Sol {i+1} Mars REMS log. Min temp {min_temp}C, Pressure {pressure} Pa. Suit integrity {suit_val}%.\n"

        for _ in range(len(line)):
            real_telemetry_logs.append(meter_row)
        script_lines.append(line)

with open("game_script.txt", "w", encoding="utf-8") as f:
    f.write("".join(script_lines))

with open("nasa_telemetry.json", "w", encoding="utf-8") as f:
    json.dump(real_telemetry_logs, f)

print(f"Success! Loaded {len(real_telemetry_logs)} real Mars weather steps!")
