from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
from train import MultimodalMamba
from space_dataloader import SpaceTrainerDataset

app = FastAPI()

# Allow your teammate's frontend & backend to connect without browser blocks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Load your trained Mamba model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
dataset = SpaceTrainerDataset("game_script.txt", "nasa_telemetry.json", sequence_length=32)

model = MultimodalMamba(vocab_size=dataset.vocab_size, d_model=64, n_layer=2).to(device)
model.load_state_dict(torch.load("astronaut_mamba_brain.pth", map_location=device))
model.eval()

# 2. Match your teammate's exact JSON structure
class TelemetryData(BaseModel):
    oxygenLevel: float
    suitPower: float
    speed: float

class NasaHazardData(BaseModel):
    type: str
    severity: str
    location: str

class TeammateGameRequest(BaseModel):
    level: int
    telemetry: TelemetryData
    nasaHazard: NasaHazardData

# Welcome route so opening the base link never shows "404 Not Found"
@app.get("/")
def home():
    return {
        "status": "ARIA Mamba AI is Online!",
        "test_page": "Add /docs to this URL to test visually",
        "api_endpoint": "/predict_turn"
    }

@app.post("/predict_turn")
def predict_game_turn(data: TeammateGameRequest):
    # 3. Translate teammate's 3 numbers + hazard into your LLM's 9 meters + text prompt
    o2_normalized = data.telemetry.oxygenLevel / 100.0
    suit_power = data.telemetry.suitPower
    
    nine_meters = [
        o2_normalized, 
        90.0,                 # Water baseline
        92.0,                 # Food baseline
        suit_power,           # Power
        75.0 if data.nasaHazard.severity.startswith(("M", "X")) else 95.0, # Shield
        suit_power,           # Suit integrity
        -60.0,                # Thermal baseline
        4800.0,               # Mass baseline
        max(100.0, 1400.0 - data.telemetry.speed) # Fuel
    ]
    
    prompt_text = (
        f"ARIA: Level {data.level} at {data.nasaHazard.location}. "
        f"Hazard {data.nasaHazard.type} severity {data.nasaHazard.severity}. "
    )
    
    norm_meters = [val / max_v for val, max_v in zip(nine_meters, dataset.max_values)]
    tokens = [dataset.char_to_id.get(ch, 0) for ch in prompt_text[-32:]]
    if not tokens:
        tokens = [0]
    
    x_text = torch.tensor([tokens], dtype=torch.long).to(device)
    x_num = torch.tensor([[norm_meters] * len(tokens)], dtype=torch.float32).to(device)
    
    # Generate up to 110 characters and trim incomplete trailing words
    generated_chars = []
    with torch.no_grad():
        for _ in range(110):
            pred_text, pred_meters = model(x_text, x_num)
            next_char_id = torch.argmax(pred_text[0, -1, :]).item()
            generated_chars.append(dataset.id_to_char[next_char_id])
            
            next_token = torch.tensor([[next_char_id]], dtype=torch.long).to(device)
            x_text = torch.cat([x_text[:, -31:], next_token], dim=1)
            x_num = torch.cat([x_num[:, -31:, :], pred_meters[:, -1:, :]], dim=1)

    full_text = "".join(generated_chars)
    if "." in full_text:
        clean_dialogue = full_text.rsplit(".", 1)[0] + "."
    else:
        clean_dialogue = full_text

    raw_next = pred_meters[0, -1, :].cpu().tolist()
    updated_9 = [round(val * max_v, 2) for val, max_v in zip(raw_next, dataset.max_values)]

    # 4. Return clean dialogue and updated telemetry matching teammate's format
    return {
        "ariaDialogue": clean_dialogue,
        "updatedTelemetry": {
            "oxygenLevel": round(updated_9[0] * 100, 1),
            "suitPower": updated_9[3],
            "speed": data.telemetry.speed
        },
        "allNineMeters": updated_9
    }
