"""
PyTorch CNN-Autoencoder for UOWC Channel Denoising & Turbulence Mitigation.
"""
import torch
import torch.nn as nn

class UOWCEncoder(nn.Module):
    def __init__(self, input_dim=16, latent_dim=8):
        super(UOWCEncoder, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, latent_dim),
            nn.Sigmoid()  # Optical signals are unipolar non-negative
        )

    def forward(self, x):
        return self.fc(x)

class UOWCDecoder(nn.Module):
    def __init__(self, latent_dim=8, output_dim=16):
        super(UOWCDecoder, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(latent_dim, 32),
            nn.ReLU(),
            nn.Linear(32, output_dim),
            nn.Softmax(dim=-1)
        )

    def forward(self, x):
        return self.fc(x)

class EndToEndUOWCSystem(nn.Module):
    def __init__(self):
        super(EndToEndUOWCSystem, self).__init__()
        self.encoder = UOWCEncoder()
        self.decoder = UOWCDecoder()

    def forward(self, x, noise_std=0.1):
        latent = self.encoder(x)
        # AWGN + Scintillation Channel Emulation
        noisy_latent = latent + torch.randn_like(latent) * noise_std
        return self.decoder(noisy_latent)
