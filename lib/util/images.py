import cv2
import numpy as np
from PIL import Image


def cv_to_pil(image):
    return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))


def pil_to_cv(image):
    return cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
