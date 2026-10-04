import torch
import cv2
import norfair
from ultralytics import YOLO

print("=" * 50)
print(" ENVIRONMENT & FRAMEWORK VERIFICATION")
print("=" * 50)
print(f"PyTorch Version:   {torch.__version__}")
print(f"CUDA Available:    {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU Device:        {torch.cuda.get_device_name(0)}")
print(f"OpenCV Version:    {cv2.__version__}")
print(f"Norfair Version:   {norfair.__version__}")
print(f"Norfair Tracker:   READY (Zero-training 2D Kalman tracking)")
print("=" * 50)
print("Everything is properly configured and ready to run!")