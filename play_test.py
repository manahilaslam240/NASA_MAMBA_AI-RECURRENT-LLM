import torch
from train import MultimodalMamba
from space_dataloader import SpaceTrainerDataset

# 1. Load the vocabulary and scaling factors from your dataset
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
dataset = SpaceTrainerDataset("game_script.txt", "nasa_telemetry.json", sequence_length=32)

# 2. Load your newly trained Mamba brain!
model = MultimodalMamba(vocab_size=dataset.vocab_size, d_model=64, n_layer=2).to(device)
model.load_state_dict(torch.load("astronaut_mamba_brain.pth", map_location=device))
model.eval()

# 3. Simulate a live game moment: High radiation / Cold Mars night
# [O2, Water, Food, Power, Shield, Suit, Thermal, Mass, Fuel]
test_meters = [0.96, 88.0, 91.0, 72.0, 65.0, 93.0, -78.5, 4750.0, 1300.0]
starting_text = "ARIA: "

# Normalize meters and convert text to token IDs
norm_meters = [val / max_v for val, max_v in zip(test_meters, dataset.max_values)]
tokens = [dataset.char_to_id.get(ch, 0) for ch in starting_text]

x_text = torch.tensor([tokens], dtype=torch.long).to(device)
x_num = torch.tensor([[norm_meters] * len(tokens)], dtype=torch.float32).to(device)

print("Feeding Mars telemetry into Mamba...")
generated_text = starting_text

# 4. Generate 60 characters of live response + predicted meter updates
with torch.no_grad():
    for _ in range(60):
        pred_text, pred_meters = model(x_text, x_num)
        
        next_char_id = torch.argmax(pred_text[0, -1, :]).item()
        generated_text += dataset.id_to_char[next_char_id]
        
        # Slide the window forward
        next_token = torch.tensor([[next_char_id]], dtype=torch.long).to(device)
        x_text = torch.cat([x_text[:, -31:], next_token], dim=1)
        x_num = torch.cat([x_num[:, -31:, :], pred_meters[:, -1:, :]], dim=1)

    # Convert final predicted numbers back to real game values
    final_raw_meters = pred_meters[0, -1, :].cpu().tolist()
    updated_meters = [round(val * max_v, 2) for val, max_v in zip(final_raw_meters, dataset.max_values)]

print("\n--- LIVE AI OUTPUT ---")
print("Generated Dialogue:", generated_text)
print("Updated 9 Meters:  ", updated_meters)
