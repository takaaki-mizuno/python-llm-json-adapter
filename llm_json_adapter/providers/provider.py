import json
import logging
from typing import Any, Dict, List, Optional

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

    def generate_prompt(self,
                        prompt: str,
                        function: Response,
                        language: str = "en",
                        act_as: Optional[str] = None) -> str:
        generated_prompt = prompt + "\n\n"

        if act_as is not None:
            generated_prompt += f"Please answer as {act_as}.\n\n"

        full_language = self.set_language(language)
        if full_language is not None:
            full_language = languages[language]
            generated_prompt += f"Response should be in {full_language}.\n\n"

        json_format = json.dumps(function.parameters)
        generated_prompt += (
            f"And follow the following Json schema as the response format: \n\n"
            f"\n{json_format}\n\n")

        generated_prompt += (
            "- Response should be a single valid JSON data\n"
            "- Response should be wrapped by the markdown code block\n"
            "- Output only the json response\n"
            "- No need to output the format itself\n\n")

        return generated_prompt

    def debug_log(self, message: str):
        if self._logger is not None:
            self._logger.debug(message)

    def generate_chat_prompt(
            self,
            prompt: str,
            function: Response,
            language: str = "en",
            act_as: Optional[str] = None) -> list[dict[str, str]]:

        full_language = self.set_language(language)
        json_format = json.dumps(function.parameters)

        messages = [{
            "role": "user",
            "content": prompt,
        }, {
            "role":
            "system",
            "content":
            f"You are {act_as}. Response should be in {full_language}.",
        }, {
            "role":
            "system",
            "content":
            f"use the following Json schema as the response format\n"
            f"```{json_format}```\n\n"
            "- Response should be a single valid JSON data\n"
            "- Response should be wrapped by the markdown code block\n"
            "- Output only the json response\n"
            "- No need to output the format itself\n\n",
        }]

        return messages

    def convert_to_llama_presentation(self, messages: List[Dict[str,
                                                                str]]) -> str:
        result = "<|begin_of_text|>"
        for message in messages:
            role = message.get("role")
            content = message.get("content")
            result = result + f"<|start_header_id|>{role}<|end_header_id|>\n{content}<|eot_id|>"
        return result

    async def generate(self,
                       prompt: str,
                       function: Response,
                       language: str = "en",
                       act_as: Optional[str] = None) -> Optional[Dict]:
        raise NotImplementedError()
