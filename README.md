# 🚀 ARIA: Multimodal Mamba Recurrent LLM for Junior Astronaut Mission Trainer

**NASA Space Apps Challenge 2026 | Build a Junior Astronaut Mission Trainer**

## Overview
**ARIA** (Autonomous Recurrent Intelligence Assistant) is a custom **Multimodal State Space Model (Mamba)** built from scratch in PyTorch. Unlike standard text-only chatbots, ARIA simultaneously ingests narrative mission dialogue alongside **9 continuous spacecraft life-support and environmental telemetry meters** (`O2`, `Water`, `Food`, `Power`, `Shield`, `Suit Integrity`, `Thermal`, `Mass`, and `Fuel`).

Using Mamba's selective scan recurrent memory, the model tracks cause-and-effect across long spaceflight missions—generating real-time, interactive trade-off decisions for trainee astronauts while predicting physics-grounded updates to spacecraft telemetry.

---

## Key Features
* **Multimodal Fusion Architecture:** Aligns discrete text tokens (`nn.Embedding`) with normalized continuous NASA sensor vectors (`nn.Linear`) inside a unified `d_model` latent space without dimensional clashing.
* **Recurrent Long-Horizon Memory:** Built on the Mamba State Space architecture (`mamba-minimal`), allowing the AI to retain mission history and cumulative resource strain with constant memory overhead.
* **Dual Output Prediction Heads:** Simultaneously predicts next-token dialogue (`CrossEntropyLoss`) and next-step spacecraft resource trajectories (`MSELoss`).
* **Interactive Decision Trade-Offs:** Prompts players with realistic mission choices (e.g., boosting magnetic shields vs. power drain, or activating suit heaters vs. oxygen consumption).
* **REST API Microservice:** Served via **FastAPI** (`/predict_turn`) for seamless integration with game engines and web frontends.

---

## NASA Data Sources Used
This model is grounded in authentic NASA space weather, radiation dosimetry, and planetary telemetry datasets:
1. **NASA DONKI Space Weather API:** Coronal Mass Ejections (`CME`), Solar Flares (`FLR`), Geomagnetic Storms (`GST`), and `WSA+Enlil` solar wind simulations.
2. **NASA OSDR RadLab Telemetry:** Real spacecraft radiation dosimetry (`ISS DosTel`, `ISS REM`, and `TriTel` absorbed dose rates).
3. **NASA Mars Trek & Curiosity REMS:** Martian surface elevation (`MOLA`), mineralogy (`TES Plagioclase`), `Hale Crater CTX` terrain layers, and Sol temperature/pressure logs.

---

## Repository Structure

| File | Description |
| :--- | :--- |
| `model.py` | Core Mamba State Space selective scan and `ResidualBlock` architecture. |
| `space_dataloader.py` | Multimodal dataset pipeline handling character tokenization and 9-meter feature scaling. |
| `train.py` | Dual-loss (`CrossEntropy + MSE`) training loop producing `astronaut_mamba_brain.pth`. |
| `train_three_nasa.py` | Multi-source NASA CSV ingestion and interactive scenario generator. |
| `game_backend_api.py` | Production FastAPI server exposing `/predict_turn` with CORS support. |
| `astronaut_mamba_brain.pth` | Pre-trained PyTorch model weights. |

---

## API Usage (`POST /predict_turn`)

### Sample Request
```json
{
  "level": 2,
  "telemetry": {
    "oxygenLevel": 85,
    "suitPower": 70,
    "speed": 100
  },
  "nasaHazard": {
    "type": "solar_flare",
    "severity": "M2.4",
    "location": "Deep Space Transit"
  }
}
```

### Sample Response
```json
{
  "ariaDialogue": "ARIA: DONKI Solar Flare (FLR) detected! Boost magnetic shields now? Warning: Suit power will drop from 70.0% to 56.0%.",
  "updatedTelemetry": {
    "oxygenLevel": 84.2,
    "suitPower": 68.5,
    "speed": 100
  },
  "allNineMeters": [0.84, 90.0, 92.0, 68.5, 72.4, 68.5, -60.0, 4800.0, 1300.0]
}
```
