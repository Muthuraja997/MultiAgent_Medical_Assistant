"""
Brain MRI tumor-type classification.

Expects a DenseNet121 checkpoint compatible with 4-class MRI slice classification
(common public datasets: glioma / meningioma / pituitary / no tumor).

Place weights at the path in MedicalCVConfig.brain_tumor_model_path
(default: .../brain_tumor_agent/models/brain_tumor_segmentation.pth).

Optional: set env BRAIN_TUMOR_GDRIVE_ID to a Google Drive file id; weights are
downloaded once via gdown (same pattern as skin lesion).
"""

from __future__ import annotations

import logging
import os
from typing import List, Optional

import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image

logger = logging.getLogger(__name__)

# Index order must match the classifier head used when the checkpoint was trained.
CLASS_NAMES: List[str] = ["glioma", "meningioma", "pituitary", "notumor"]


class BrainTumorClassification:
    """DenseNet121 4-class brain MRI classification."""

    def __init__(self, model_path: str, device: Optional[torch.device] = None):
        self.model_path = model_path
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.class_names = list(CLASS_NAMES)
        self.model: Optional[nn.Module] = None

        self.mean_nums = [0.485, 0.456, 0.406]
        self.std_nums = [0.229, 0.224, 0.225]
        self.transform = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=self.mean_nums, std=self.std_nums),
            ]
        )

        self._maybe_download_weights()
        if os.path.isfile(self.model_path):
            self._load_model()
        else:
            logger.warning(
                "Brain tumor weights not found at %s. BRAIN_TUMOR_AGENT will return a setup message until "
                "you add a compatible DenseNet121 4-class state dict (.pth).",
                self.model_path,
            )

    def _maybe_download_weights(self) -> None:
        gid = os.getenv("BRAIN_TUMOR_GDRIVE_ID", "").strip()
        if not gid or os.path.isfile(self.model_path):
            return
        try:
            from agents.image_analysis_agent.skin_lesion_agent.model_download import (
                download_model_checkpoint,
            )

            download_model_checkpoint(gid, self.model_path)
        except Exception as e:
            logger.error("Optional brain tumor weight download failed: %s", e)

    def _build_model(self) -> nn.Module:
        model = models.densenet121(weights=None)
        num_ftrs = model.classifier.in_features
        model.classifier = nn.Linear(num_ftrs, len(self.class_names))
        return model

    def _load_model(self) -> None:
        try:
            self.model = self._build_model()
            try:
                raw = torch.load(self.model_path, map_location=self.device, weights_only=False)
            except TypeError:
                raw = torch.load(self.model_path, map_location=self.device)
            if isinstance(raw, dict) and "state_dict" in raw:
                state = raw["state_dict"]
            elif isinstance(raw, dict) and "model" in raw and isinstance(raw["model"], dict):
                state = raw["model"]
            else:
                state = raw
            if isinstance(state, dict):
                state = {
                    k.replace("module.", "").replace("model.", ""): v
                    for k, v in state.items()
                }
            missing, unexpected = self.model.load_state_dict(state, strict=False)
            if missing:
                logger.warning("Brain tumor checkpoint missing keys (first 5): %s", list(missing)[:5])
            if unexpected:
                logger.warning("Brain tumor checkpoint unexpected keys (first 5): %s", list(unexpected)[:5])
            self.model.to(self.device)
            self.model.eval()
            logger.info("Brain tumor classifier loaded from %s", self.model_path)
        except Exception as e:
            logger.error("Failed to load brain tumor weights: %s", e)
            self.model = None

    def predict(self, img_path: str) -> Optional[str]:
        """
        Returns one of CLASS_NAMES, or None if weights missing / inference failed.
        """
        if self.model is None:
            return None
        try:
            image = Image.open(img_path).convert("RGB")
            tensor = self.transform(image).unsqueeze(0).to(self.device)
            with torch.no_grad():
                logits = self.model(tensor)
                pred_idx = int(torch.argmax(logits, dim=1).item())
            label = self.class_names[pred_idx]
            logger.info("Brain MRI predicted class: %s", label)
            return label
        except Exception as e:
            logger.exception("Brain tumor inference error: %s", e)
            return None
