import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import AdamW
from model import ModelArgs, ResidualBlock
from space_dataloader import SpaceTrainerDataset

# 1. Define our Multimodal Mamba Architecture
class MultimodalMamba(nn.Module):
    def __init__(self, vocab_size, d_model=64, n_layer=2):
        super().__init__()
        self.args = ModelArgs(d_model=d_model, n_layer=n_layer, vocab_size=vocab_size)
        
        # Translators for Text and 9 NASA Meters
        self.text_embedding = nn.Embedding(vocab_size, d_model)
        self.numerical_projection = nn.Linear(9, d_model)
        
        # Core Mamba Recurrent Blocks from johnma2006/mamba-minimal
        self.layers = nn.ModuleList([ResidualBlock(self.args) for _ in range(n_layer)])
        self.norm_f = nn.RMSNorm(d_model)
        
        # Dual Output Heads: Predicts next dialogue character AND next 9 meter values
        self.text_head = nn.Linear(d_model, vocab_size, bias=False)
        self.meter_head = nn.Linear(d_model, 9)

    def forward(self, text_tokens, nasa_meters):
        # Convert both inputs into matching [Batch, Seq_Len, d_model] vectors
        text_vecs = self.text_embedding(text_tokens)
        num_vecs = self.numerical_projection(nasa_meters)
        
        # Fuse them together safely without clashing
        x = text_vecs + num_vecs
        
        # Run through Mamba's recurrent selective scan blocks
        for layer in self.layers:
            x = layer(x)
        x = self.norm_f(x)
        
        # Output both predictions
        pred_text = self.text_head(x)
        pred_meters = self.meter_head(x)
        return pred_text, pred_meters


if __name__ == "__main__":
    # 2. Setup Training
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")

    dataset = SpaceTrainerDataset("game_script.txt", "nasa_telemetry.json", sequence_length=32)
    dataloader = DataLoader(dataset, batch_size=64, shuffle=True)

    model = MultimodalMamba(vocab_size=dataset.vocab_size, d_model=64, n_layer=2).to(device)
    optimizer = AdamW(model.parameters(), lr=1e-3)

    criterion_text = nn.CrossEntropyLoss()
    criterion_numbers = nn.MSELoss()

    # 3. Run Training Loop
    print("Starting Multimodal Mamba Training...")
    model.train()

    for batch_idx, (x_text, x_num, y_text, y_num) in enumerate(dataloader):
        if batch_idx >= 300:
            break
        x_text, x_num = x_text.to(device), x_num.to(device)
        y_text, y_num = y_text.to(device), y_num.to(device)
        
        optimizer.zero_grad()
        pred_text, pred_meters = model(x_text, x_num)
        
        loss_t = criterion_text(pred_text.view(-1, dataset.vocab_size), y_text.view(-1))
        loss_n = criterion_numbers(pred_meters, y_num)
        total_loss = loss_t + (10.0 * loss_n)
        
        total_loss.backward()
        optimizer.step()
        
        if batch_idx % 50 == 0:
            print(f"Batch {batch_idx}/{len(dataloader)} | Total Loss: {total_loss.item():.4f}")

    # 4. Save the trained brain!
    torch.save(model.state_dict(), "astronaut_mamba_brain.pth")
    print("Training complete! Saved model weights to astronaut_mamba_brain.pth")
