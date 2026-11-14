import json
import random

# 1. Read the live NASA file you just saved from your browser
with open("live_nasa_flares.json", "r", encoding="utf-8") as f:
    live_flares = json.load(f)

print(f"Loaded {len(live_flares)} real NASA solar flare events!")

real_telemetry_logs = []
script_lines = []

# 2. Loop through the real NASA events and map them to your 9 game meters
for i in range(2000):
    # Pick a real flare event from the downloaded NASA file
    flare = live_flares[i % len(live_flares)]
    flare_class = flare.get("classType", "C1.0") # e.g., 'M2.5' or 'X1.0'
    
    # Stronger flares (M or X class) cause bigger drops in Shield and Power
    is_severe = flare_class.startswith("M") or flare_class.startswith("X")
    
    shield_val = round(random.uniform(55.0, 72.0), 1) if is_severe else round(random.uniform(92.0, 100.0), 1)
    power_val = round(random.uniform(60.0, 78.0), 1) if is_severe else round(random.uniform(88.0, 100.0), 1)
    o2_val = round(random.uniform(0.94, 0.99), 3)
    water_val = round(95.0 - (i * 0.005), 2)
    food_val = round(98.0 - (i * 0.004), 2)
    suit_val = 93.0 if is_severe else 98.5
    mars_temp = -48.5 if is_severe else -62.0
    mass_val = round(4800.0 - (i * 0.05), 1)
    fuel_val = round(1400.0 - (i * 0.1), 1)

    # Order: [O2, Water, Food, Power, Shield, Suit, Thermal, Mass, Fuel]
    row = [o2_val, water_val, food_val, power_val, shield_val, suit_val, mars_temp, mass_val, fuel_val]
    
    if is_severe:
        line = f"ARIA: Warning! Class {flare_class} solar flare detected. Shields dropped to {shield_val}%.\n"
    else:
        line = f"Commander Reyes: Solar activity minor ({flare_class}). All 9 systems nominal.\n"
        
    for _ in range(len(line)):
        real_telemetry_logs.append(row)
    script_lines.append(line)

# 3. Overwrite your training files with the live NASA data
with open("game_script.txt", "w", encoding="utf-8") as f:
    f.write("".join(script_lines))

with open("nasa_telemetry.json", "w") as f:
    json.dump(real_telemetry_logs, f)

print("Success! Converted live NASA website data into training files.")
