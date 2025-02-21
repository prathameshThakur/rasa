from __future__ import annotations
import typing
from pathlib import Path
from typing import Any, Dict, List, Optional, Text

import dataclasses

from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
import rasa.nlu.utils._mitie_utils
from rasa.shared.exceptions import InvalidConfigException

if typing.TYPE_CHECKING:
    import mitie

# TODO: This is a workaround around until we have all components migrated to
# `GraphComponent`.
MitieNLP = rasa.nlu.utils._mitie_utils.MitieNLP


@dataclasses.dataclass
class MitieModel:
    """Wraps `MitieNLPGraphComponent` output to make it fingerprintable."""

    import mitie

    word_feature_extractor: mitie.total_word_feature_extractor
    model_path: Path

    def fingerprint(self) -> Text:
        """Fingerprints the model path.

        Use a static fingerprint as we assume this only changes if the file path
        changes and want to avoid investigating the model in greater detail for now.

        Returns:
            Fingerprint for model.
        """
        return str(self.model_path)


class MitieNLPGraphComponent(GraphComponent):
    """Component which provides the common configuration and loaded model to others.

    This is used to avoid loading the Mitie model multiple times. Instead the Mitie
    model is only loaded once and then shared by depending components.
    """

    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        """Returns default config (see parent class for full docstring)."""
        return {
            # name of the language model to load - this contains
            # the MITIE feature extractor
            "model": Path("data", "total_word_feature_extractor.dat")
        }

    def __init__(
        self,
        path_to_model_file: Path,
        extractor: Optional["mitie.total_word_feature_extractor"] = None,
    ) -> None:
        """Constructs a new language model from the MITIE framework."""
        self._path_to_model_file = path_to_model_file
        self._extractor = extractor

    @classmethod
    def required_packages(cls) -> List[Text]:
        """Lists required dependencies (see parent class for full docstring)."""
        return ["mitie"]

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> MitieNLPGraphComponent:
        """Creates component (see parent class for full docstring)."""
        import mitie

        model_file = config.get("model")
        if not model_file or not Path(model_file).is_file():
            raise InvalidConfigException(
                "The MITIE component 'MitieNLP' needs "
                "the configuration value for 'model'."
                "Please take a look at the "
                "documentation in the pipeline section "
                "to get more info about this "
                "parameter."
            )
        extractor = mitie.total_word_feature_extractor(str(model_file))

        return cls(Path(model_file), extractor)

    def provide(self) -> MitieModel:
        """Provides loaded `MitieModel` and path during training and inference."""
        return MitieModel(
            word_feature_extractor=self._extractor, model_path=self._path_to_model_file
        )
