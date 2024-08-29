import torch
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection

from lib.util.config import config
from lib.util.frameworks import get_device


class GroundingDINO:
    def __init__(self):
        self.device = get_device(config.force_cpu)
        self.processor = AutoProcessor.from_pretrained(config.model)
        self.model = AutoModelForZeroShotObjectDetection.from_pretrained(config.model).to(self.device)

    def __call__(self, image, text):
        iputs = self.processor(images=image, text=text, return_tensors='pt').to(self.device)
        with torch.no_grad():
            oputs = self.model(**iputs)
        results = self.processor.post_process_grounded_object_detection(oputs,
                                                                        iputs.input_ids,
                                                                        box_threshold=config.box_threshold,
                                                                        text_threshold=config.text_threshold,
                                                                        target_sizes=[image.size[::-1]])
        return results
