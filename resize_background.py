import os 
from PIL import Image

INPUT ="big_photo.jpg"
OUTPUT = "assets/background.jpg"

os.makedirs("assets", exist_ok=True)

img = Image.open(INPUT)
img.thumbnail((1920, 1080))
img.convert("RGB").save(OUTPUT, quality=75, optimize=True)

print("Saved", OUTPUT, "-", round(os.path.getsize(OUTPUT) / 1024), "KB")
