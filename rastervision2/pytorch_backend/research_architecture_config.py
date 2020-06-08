from typing import List, Optional

from rastervision2.core.backend import BackendConfig
from rastervision2.pipeline.config import register_config, Field
from rastervision2.pytorch_backend.pytorch_learner_backend_config import \
    PyTorchLearnerBackendConfig
from rastervision2.pytorch_backend.pytorch_semantic_segmentation import \
    PyTorchSemanticSegmentation
from rastervision2.pytorch_backend.research_architecture_backend import \
    ResearchArchitectureBackend
from rastervision2.pytorch_learner.semantic_segmentation_learner_config import (
    SemanticSegmentationDataConfig, SemanticSegmentationLearnerConfig,
    SemanticSegmentationModelConfig)
from rastervision2.pytorch_learner.learner_config import (
    SolverConfig, ModelConfig, default_augmentors, augmentors as
    augmentor_list)


@register_config('research_architecture')
class ResearchArchitectureConfig(BackendConfig):
    model: Optional[ModelConfig]
    architecture: str
    channels: int
    solver: SolverConfig
    augmentors: List[str] = Field(
        default_augmentors,
        description=(
            'Names of augmentors to use for training batches. '
            'Choices include: ' + str(augmentor_list)))

    def get_learner_config(self, pipeline):
        data = SemanticSegmentationDataConfig()
        data.uri = pipeline.chip_uri
        data.class_names = pipeline.dataset.class_config.names
        data.class_colors = pipeline.dataset.class_config.colors
        data.img_sz = pipeline.train_chip_sz
        data.augmentors = self.augmentors

        learner = SemanticSegmentationLearnerConfig(
            data=data,
            model=self.model,
            solver=self.solver,
            test_mode=False,
            output_uri=pipeline.train_uri,
            log_tensorboard=False,
            run_tensorboard=False)
        learner.update()
        return learner

    def build(self, pipeline, tmp_dir):
        learner = self.get_learner_config(pipeline)
        return PyTorchSemanticSegmentation(pipeline, learner, tmp_dir)

    def get_bundle_filenames(self) -> List[str]:
        raise NotImplementedError()

    def update(self, pipeline: Optional['RVPipeline'] = None):  # noqa
        pass
