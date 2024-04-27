import logging
from typing import Dict, Optional

import ollama
from ollama import Client

from ...exceptions import RetryableError
from ...objects import Response
from ...utilities import JsonUtility

from ..provider import Provider as BaseProvider


class Provider(BaseProvider):
    _required_attributes = {
        'url': "http://localhost:11434",
        'model': 'llama3',
    }

    def __init__(self,
                 logger: Optional[logging.Logger] = None,
                 attributes: Optional[Dict] = None):
        super().__init__(logger=logger, attributes=attributes)
        self._client = self.get_client()

    def get_client(self) -> Client:
        return ollama.Client(host=self.get_attribute(
            'url', default_value="http://localhost:11434"), )

    async def generate(self,
                       prompt: str,
                       function: Response,
                       language: str = "en",
                       act_as: Optional[str] = None) -> Optional[Dict]:
        generated_prompt = self.generate_chat_prompt(
            prompt=prompt,
            function=function,
            language=language,
            act_as=act_as,
        )
        self.debug_log(f"Generated Prompt: {generated_prompt}")
        result = self._client.chat(
            model=self.get_attribute('model', default_value="llama3"),
            messages=generated_prompt,
            stream=False,
        )

        self.debug_log(f"Generated Result: {result}")

        result = JsonUtility.extract_json_block(
            text=result['message']['content'])
        if not isinstance(result, dict):
            raise RetryableError('Failed to extract json block')

        return result
