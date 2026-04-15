from typing import Any, Optional

from .image_classifier import ImageClassifier

# Sentinel returned by segment_skin_lesion when imports/deps fail (distinct from model "no mask").
SKIN_LESION_DEPS_MISSING = "__SKIN_LESION_DEPS_MISSING__"


class ImageAnalysisAgent:
    """
    Agent responsible for processing image uploads and classifying them as medical or non-medical, and determining their type.
    """

    def __init__(self, config):
        # Only import ImageClassifier at module load. Chest/skin/brain modules pull in torch/torchvision;
        # defer those imports until those code paths run so vision-only classify_image() works without torchvision.
        self.image_classifier = ImageClassifier(
            vision_model=config.medical_cv.llm,
            enable_brain_mri=config.medical_cv.enable_brain_tumor_agent,
        )
        self._chest_xray_agent: Optional[Any] = None
        self._chest_xray_model_path = config.medical_cv.chest_xray_model_path
        self._enable_brain_tumor = config.medical_cv.enable_brain_tumor_agent
        self._brain_tumor_model_path = config.medical_cv.brain_tumor_model_path
        self._brain_tumor_agent: Optional[Any] = None
        self._skin_lesion_agent: Optional[Any] = None
        self._skin_lesion_model_path = config.medical_cv.skin_lesion_model_path
        self.skin_lesion_segmentation_output_path = config.medical_cv.skin_lesion_segmentation_output_path

    def _get_chest_xray_agent(self) -> Any:
        if self._chest_xray_agent is None:
            from .chest_xray_agent.covid_chest_xray_inference import ChestXRayClassification

            self._chest_xray_agent = ChestXRayClassification(model_path=self._chest_xray_model_path)
        return self._chest_xray_agent

    def _get_skin_lesion_agent(self) -> Any:
        if self._skin_lesion_agent is None:
            from .skin_lesion_agent.skin_lesion_inference import SkinLesionSegmentation

            self._skin_lesion_agent = SkinLesionSegmentation(model_path=self._skin_lesion_model_path)
        return self._skin_lesion_agent

    # classify image
    def analyze_image(self, image_path: str) -> dict:
        """Classifies images as medical or non-medical and determines their type."""
        return self.image_classifier.classify_image(image_path)

    # chest x-ray agent
    def classify_chest_xray(self, image_path: str) -> Optional[str]:
        try:
            return self._get_chest_xray_agent().predict(image_path)
        except (ModuleNotFoundError, ImportError) as e:
            print(f"[ImageAnalysisAgent] Chest X-ray unavailable (missing dependency): {e}")
            return None

    def classify_brain_tumor(self, image_path: str):
        if not self._enable_brain_tumor:
            return None
        if self._brain_tumor_agent is None:
            from .brain_tumor_agent.brain_tumor_inference import BrainTumorClassification

            self._brain_tumor_agent = BrainTumorClassification(self._brain_tumor_model_path)
        return self._brain_tumor_agent.predict(image_path)

    # skin lesion agent
    def segment_skin_lesion(self, image_path: str) -> Optional[str]:
        try:
            return self._get_skin_lesion_agent().predict(image_path, self.skin_lesion_segmentation_output_path)
        except (ModuleNotFoundError, ImportError) as e:
            print(f"[ImageAnalysisAgent] Skin lesion segmentation unavailable (missing dependency): {e}")
            return SKIN_LESION_DEPS_MISSING
