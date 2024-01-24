import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Optional

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from .exceptions import ExceededMaxRetryCountError, RetryableError
from .objects import Response
from .providers import Provider


class LLMJsonAdapter(object):

    def __init__(
        self,
        provider_name: str,
        attributes: Dict = None,
        language: str = 'en',
        max_retry_count: int = 3,
        logger: Optional[logging.Logger] = None,
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
                             function: Response,
                             language: Optional[str] = "en",
                             act_as: Optional[str] = None) -> Dict:
        if not self.validate_jsonschema(function.parameters):
            raise Exception('Invalid JSON schema')

        if language is None:
            language = self._language

        retry_count = 0
        latest_message = ""
        while retry_count < self._max_retry_count:
            retry_count += 1
            try:
                return await self._provider.generate(prompt, function,
                                                     language, act_as)
            except RetryableError as e:
                if self._logger is not None:
                    self._logger.error(f'Failed to generate response: {e}')
                    latest_message = str(e)
                continue

        if self._logger is not None:
            self._logger.error(
                f'Exceeded max retry count: {self._max_retry_count} Latest exception is: {latest_message}'
            )

        raise ExceededMaxRetryCountError(
            f'Exceeded max retry count: {self._max_retry_count} Latest exception is: {latest_message}'
        )

    def generate(self,
                 prompt: str,
                 function: Response,
                 language: Optional[str] = None,
                 act_as: Optional[str] = None) -> Dict:
        return asyncio.run(
            self.generate_async(prompt, function, language, act_as))
