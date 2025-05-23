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
