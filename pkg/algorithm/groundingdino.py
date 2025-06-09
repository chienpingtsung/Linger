import torch
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection

from pkg.utils.config import cfg
from pkg.utils.dlframework import get_device


class GroundingDINO:
    def __init__(self):
        self.device = get_device(cfg.force_cpu)
        self.processor = AutoProcessor.from_pretrained(cfg.model)
        self.model = AutoModelForZeroShotObjectDetection.from_pretrained(cfg.model).to(self.device)

    def __call__(self, image, text):
        iputs = self.processor(images=image, text=text, return_tensors='pt').to(self.device)
        with torch.no_grad():
            oputs = self.model(**iputs)
        return self.processor.post_process_grounded_object_detection(oputs,
                                                                     iputs.input_ids,
                                                                     box_threshold=cfg.box_threshold,
                                                                     text_threshold=cfg.text_threshold,
                                                                     target_sizes=[image.size[::-1]])
