import cv2
import numpy as np
from PIL import Image, ImageDraw


def cv_to_pil(image):
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))


def pil_to_cv(image):
    return cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)


def add_box_mask(image, box=None, mask=None):
    if mask is not None:
        overlay = Image.new('RGB', image.size, (255, 0, 0))
        image = Image.composite(overlay, image, mask)
    if box is not None:
        draw = ImageDraw.Draw(image)
        draw.rectangle(box, outline='red', width=5)
    return image
