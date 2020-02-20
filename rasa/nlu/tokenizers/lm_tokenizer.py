from typing import Text, List, Any, Dict

from rasa.nlu.tokenizers.tokenizer import Token, Tokenizer
from rasa.nlu.utils.hugging_face.hf_transformers import HFTransformersNLP
from rasa.nlu.training_data import Message

from rasa.nlu.constants import (
    TOKENS_NAMES,
    LANGUAGE_MODEL_DOCS,
    DENSE_FEATURIZABLE_ATTRIBUTES,
    MESSAGE_ATTRIBUTES,
    TOKENS,
)


class LanguageModelTokenizer(Tokenizer):
    """Tokenizer using transformer based language models.

        Uses the output of HFTransformersNLP component to set the tokens
        for dense featurizable attributes of each message object.
    """

    provides = [TOKENS_NAMES[attribute] for attribute in MESSAGE_ATTRIBUTES]

    requires = [
        LANGUAGE_MODEL_DOCS[attribute] for attribute in DENSE_FEATURIZABLE_ATTRIBUTES
    ]

    required_components = [HFTransformersNLP.name]

    defaults = {
        # Flag to check whether to split intents
        "intent_tokenization_flag": False,
        # Symbol on which intent should be split
        "intent_split_symbol": "_",
    }

    def get_doc(self, message: Message, attribute: Text) -> Dict[Text, Any]:
        return message.get(LANGUAGE_MODEL_DOCS[attribute])

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        doc = self.get_doc(message, attribute)

        return doc[TOKENS]
