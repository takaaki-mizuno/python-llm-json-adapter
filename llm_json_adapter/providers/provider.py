import logging
from typing import Any, Dict, Optional

from ..objects import Response
from .languages import languages


class Provider(object):
    _required_attributes = {}

    def __init__(self,
                 logger: Optional[logging.Logger] = None,
                 attributes: Optional[Dict] = None):
        self._logger = logger
        self._attributes = attributes
        self.check_attributes()

    def check_attributes(self):
        if self._attributes is None:
            raise ValueError("Attributes not set")
        for attribute in self._required_attributes.keys():
            if attribute not in self._attributes:
                if self._required_attributes[attribute] is None:
                    raise ValueError(f"Attribute {attribute} not set")
                self._attributes[attribute] = self._required_attributes[
                    attribute]

    def get_attribute(self, name: str, default_value: Any) -> Any:
        if self._attributes is None:
            return default_value
        if name not in self._attributes:
            return default_value
        return self._attributes[name]

    @staticmethod
    def set_language(language: Optional[str]):
        if language is None:
            return None
        if language not in languages:
            raise ValueError(f"Language {language} not supported")
        return languages[language]

    async def generate(self,
                       prompt: str,
                       function: Response,
                       language: str = "en",
                       act_as: Optional[str] = None) -> Optional[Dict]:
        raise NotImplementedError()
