✅ Step-by-Step: CRAFT Text Detection + Tesseract OCR (Local Python Setup)
🧱 1. Prerequisites
Install dependencies:

bash
Copy
Edit
pip install opencv-python numpy torch torchvision matplotlib pytesseract
Clone the CRAFT repository:

bash
Copy
Edit
git clone https://github.com/clovaai/CRAFT-pytorch.git
cd CRAFT-pytorch
Download the CRAFT model and place it in the repo directory:
craft_mlt_25k.pth (Download)

🧠 2. Run Detection + OCR
Here's a sample script (craft_ocr_pipeline.py) you can use:

python
Copy
Edit
import cv2
import torch
import pytesseract
import numpy as np
from craft import CRAFT
from craft_utils import getDetBoxes
from imgproc import resize_aspect_ratio, normalizeMeanVariance
from collections import OrderedDict

# Load model
def load_craft_model(model_path, device):
    net = CRAFT()
    net.load_state_dict(copy_state_dict(torch.load(model_path, map_location=device)))
    net.to(device)
    net.eval()
    return net

# Run detection
def detect_text(image_path, model, device):
    image = cv2.imread(image_path)
    img_resized, target_ratio, size_heatmap = resize_aspect_ratio(image, 1280, interpolation=cv2.INTER_LINEAR)
    ratio_h = ratio_w = 1 / target_ratio
    x = normalizeMeanVariance(img_resized)
    x = torch.from_numpy(x).permute(2, 0, 1).unsqueeze(0).float().to(device)

    with torch.no_grad():
        y, _ = model(x)
    score_text = y[0, :, :, 0].cpu().data.numpy()
    boxes, _ = getDetBoxes(score_text, 0.7, 0.4, 0.4, False)
    boxes = boxes * (1 / ratio_w)
    return boxes, image

# Run OCR on boxes
def run_ocr(image, boxes):
    results = []
    for box in boxes:
        pts = box.astype(np.int32).reshape((-1, 1, 2))
        x, y, w, h = cv2.boundingRect(pts)
        crop = image[y:y+h, x:x+w]
        text = pytesseract.image_to_string(crop, config="--psm 6")
        results.append(text.strip())
    return results

# Helper for loading weights
def copy_state_dict(state_dict):
    if list(state_dict.keys())[0].startswith("module"):
        new_state_dict = OrderedDict()
        for k, v in state_dict.items():
            name = k[7:]
            new_state_dict[name] = v
        return new_state_dict
    else:
        return state_dict

# Main
if __name__ == "__main__":
    image_path = "ANNA_DVD_SLEEVE.png"  # Your image path
    model_path = "craft_mlt_25k.pth"
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    model = load_craft_model(model_path, device)
    boxes, image = detect_text(image_path, model, device)
    texts = run_ocr(image, boxes)

    print("Recognized Text:")
    for t in texts:
        if t:
            print("-", t)
🧪 Results & Tips
This script will detect text boxes using CRAFT and then apply OCR using Tesseract.

You can improve results with better image preprocessing (denoising, sharpening, etc.).

For faster pipeline development, wrap the output into structured metadata (title, cast, synopsis, etc.).

Would you like me to help adapt this script to export results into CSV or JSON format for your DVD collection? 







You said:
Yes adapt it to export the results to both csv and json format so I can see which works best for my use case.


ChatGPT said:
Great! Here's how to adapt the script so that the recognized text is saved to both CSV and JSON formats.

✅ Modified: craft_ocr_pipeline.py with CSV & JSON Export
Add this to the bottom of the previous script, replacing the print("Recognized Text:")... part:

python
Copy
Edit
import csv
import json
import os

# Output file paths
base_name = os.path.splitext(os.path.basename(image_path))[0]
csv_path = f"{base_name}_ocr_output.csv"
json_path = f"{base_name}_ocr_output.json"

# Save to CSV
with open(csv_path, mode="w", newline='', encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Line Number", "Text"])
    for i, text in enumerate(texts, start=1):
        writer.writerow([i, text])

# Save to JSON
json_data = [{"line": i+1, "text": text} for i, text in enumerate(texts)]
with open(json_path, "w", encoding="utf-8") as json_file:
    json.dump(json_data, json_file, indent=4, ensure_ascii=False)

# Optional: Print a preview
print("\nSample OCR Output (First 5 Lines):")
for line in json_data[:5]:
    print(f"{line['line']}: {line['text']}")
🗂️ Output Files
ANNA_DVD_SLEEVE_ocr_output.csv: Spreadsheet-friendly format.

ANNA_DVD_SLEEVE_ocr_output.json: Structured and good for programmatic use.

📌 Pro Tips
You can combine these outputs with manual labeling (like tags for "Title", "Synopsis", etc.).

Use psm tuning in Tesseract (--psm 4, --psm 6, etc.) to experiment with layout-specific accuracy.

Let me know if you'd like this adapted for batch processing of all images in a folder.