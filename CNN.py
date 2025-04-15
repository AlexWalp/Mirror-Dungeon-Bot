import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms, models
import torch.nn.functional as F
import os

class PadToWidth:
    def __init__(self, width):
        self.target_width = width

    def __call__(self, img):
        w, h = img.size
        if w >= self.target_width:
            return img
        pad_left = (self.target_width - w) // 2
        pad_right = self.target_width - w - pad_left
        return transforms.functional.pad(img, (pad_left, 0, pad_right, 0), fill=0)  # left, top, right, bottom

# Updated transform
transform = transforms.Compose([
    PadToWidth(60),
    transforms.Resize((50, 10)),   # You might want to reverse this if aspect ratio matters
    transforms.ToTensor(),
])

dataset = datasets.ImageFolder(root='dataset_CNN_skill', transform=transform)
train_size = int(0.8 * len(dataset))
val_size = len(dataset) - train_size

train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32)

class BetterCNN(nn.Module):
    def __init__(self):
        super().__init__()

        def conv_block(in_c, out_c):
            return nn.Sequential(
                nn.Conv2d(in_c, out_c, kernel_size=3, padding=1),
                nn.BatchNorm2d(out_c),
                nn.ReLU(inplace=True),
                nn.Conv2d(out_c, out_c, kernel_size=3, padding=1),
                nn.BatchNorm2d(out_c),
                nn.ReLU(inplace=True)
            )

        self.layer1 = conv_block(3, 32)
        self.pool1 = nn.MaxPool2d(2)  # → (32, 25, 5)

        self.layer2 = conv_block(32, 64)
        self.pool2 = nn.MaxPool2d(2)  # → (64, 12, 2)

        self.layer3 = conv_block(64, 128)
        self.pool3 = nn.AdaptiveAvgPool2d((1, 1))  # → (128, 1, 1)

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        x = self.pool1(self.layer1(x))
        x = self.pool2(self.layer2(x))
        x = self.pool3(self.layer3(x))
        return self.classifier(x)
    
def evaluate(model, dataloader, loss_fn, device):
    model.eval()
    correct = 0
    total = 0
    total_loss = 0
    with torch.no_grad():
        for imgs, labels in dataloader:
            imgs, labels = imgs.to(device), labels.to(device).float().unsqueeze(1)
            preds = model(imgs)
            loss = loss_fn(preds, labels)
            total_loss += loss.item()
            correct += ((preds > 0.5) == labels).sum().item()
            total += labels.size(0)
    acc = correct / total
    return total_loss / len(dataloader), acc

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = BetterCNN().to(device)

criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

for epoch in range(18):
    model.train()
    train_loss = 0
    correct = 0
    total = 0

    for imgs, labels in train_loader:
        imgs = imgs.to(device)
        labels = labels.to(device).float().unsqueeze(1)

        preds = model(imgs)
        loss = criterion(preds, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        train_loss += loss.item()
        correct += ((preds > 0.5) == labels).sum().item()
        total += labels.size(0)

    train_acc = correct / total

    val_loss, val_acc = evaluate(model, val_loader, criterion, device)
    print(f"[Epoch {epoch+1}] Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f}")

import onnx
model = model.to("cpu")
model.eval()

dummy_input = torch.randn(1, 3, 50, 10).to("cpu")  # explicitly on CPU

torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
    opset_version=11
)