import torch
from torch.utils.data import Dataset
import json

class SpaceTrainerDataset(Dataset):
    def __init__(self, text_file_path, telemetry_file_path, sequence_length=32):
        self.sequence_length = sequence_length
        
        # 1. Load your game script text
        with open(text_file_path, 'r', encoding='utf-8') as f:
            self.raw_text = f.read()
            
        # Build character vocabulary
        self.chars = sorted(list(set(self.raw_text)))
        self.vocab_size = len(self.chars)
        self.char_to_id = {ch: i for i, ch in enumerate(self.chars)}
        self.id_to_char = {i: ch for i, ch in enumerate(self.chars)}
        
        # Convert text to integer IDs
        self.encoded_text = [self.char_to_id[ch] for ch in self.raw_text]
        
        # 2. Load your NASA telemetry numbers
        with open(telemetry_file_path, 'r') as f:
            self.raw_telemetry = json.load(f)
            
        # Scaling factors for your 9 meters so all numbers stay cleanly between -1 and 1
        # [O2, Water, Food, Power, Shield, Suit, Thermal, Mass, Fuel]
        self.max_values = [1.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 5000.0, 1500.0]
        
        # Ensure text and numbers have the exact same length
        self.total_steps = min(len(self.encoded_text), len(self.raw_telemetry)) - self.sequence_length - 1

    def __len__(self):
        return self.total_steps

    def __getitem__(self, idx):
        # Slice text input and target (next character)
        x_text = torch.tensor(self.encoded_text[idx : idx + self.sequence_length], dtype=torch.long)
        y_text = torch.tensor(self.encoded_text[idx + 1 : idx + self.sequence_length + 1], dtype=torch.long)
        
        # Slice and normalize numerical input and target (next meter step)
        raw_x_num = self.raw_telemetry[idx : idx + self.sequence_length]
        raw_y_num = self.raw_telemetry[idx + 1 : idx + self.sequence_length + 1]
        
        norm_x_num = [[val / max_v for val, max_v in zip(step, self.max_values)] for step in raw_x_num]
        norm_y_num = [[val / max_v for val, max_v in zip(step, self.max_values)] for step in raw_y_num]
        
        x_numerical = torch.tensor(norm_x_num, dtype=torch.float32)
        y_numerical = torch.tensor(norm_y_num, dtype=torch.float32)
        
        return x_text, x_numerical, y_text, y_numerical
