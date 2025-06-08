# api/model.py

import torch
import torch.nn as nn
from torchvision.models import resnet50, ResNet50_Weights

class DeepfakeDetector(nn.Module):
    def __init__(self):
        super(DeepfakeDetector, self).__init__()
        self.resnet = resnet50(weights=None) 
        
        num_ftrs = self.resnet.fc.in_features
        self.resnet.fc = nn.Identity()
        
        self.classifier = nn.Sequential(
            nn.Linear(num_ftrs, 512),
            nn.ReLU(),
            nn.BatchNorm1d(512),
            nn.Dropout(0.3),
            nn.Linear(512, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        features = self.resnet(x)
        output = self.classifier(features)
        return output