import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Optional

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from .objects import Function
from .providers import Provider


class LLMJsonAdapter(object):

    def __init__(
        self,
        provider_name: str,
        max_retry_count: int = 3,
        logger: Optional[logging.Logger] = None,
        language: str = 'en',
        attributes: Dict = None,
    ):
        self._max_retry_count = max_retry_count
        self._logger = logger
        self._attributes = attributes
        self._language = language
        self._provider: Provider = self.get_provider(provider_name)

    def get_provider(self, provider_name: str) -> Provider:
        if provider_name.lower() == 'google':
            from .providers.google import Provider as GoogleProvider
            return GoogleProvider(logger=self._logger,
                                  attributes=self._attributes)
        elif provider_name.lower() == 'openai':
            from .providers.openai import Provider as OpenAIProvider
            return OpenAIProvider(logger=self._logger,
                                  attributes=self._attributes)
        else:
            raise Exception(f'Unknown provider: {provider_name}')

    @staticmethod
    def validate_jsonschema(json_schema: dict) -> bool:
        meta_schema_path = Path(
            __file__).parent / 'schemas' / '2020-12.schema.json'
        meta_schema = json.loads(meta_schema_path.read_text())
        try:
            validate(instance=json_schema, schema=meta_schema)
            return True
        except ValidationError as e:
            return False

    async def generate_async(self,
                             prompt: str,
                             function: Function,
                             language: str = "en",
                             act_as: Optional[str] = None) -> dict:
        if not self.validate_jsonschema(function.parameters):
            raise Exception('Invalid JSON schema')

        return await self._provider.generate(prompt, function, language,
                                             act_as)

    def generate(self,
                 prompt: str,
                 function: Function,
                 language: str = "en",
                 act_as: Optional[str] = None) -> dict:
        return asyncio.run(
            self.generate_async(prompt, function, language, act_as))
