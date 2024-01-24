import json
import logging
from typing import Dict, Optional

from openai import AsyncOpenAI

from ...exceptions import RetryableError
from ...objects import Response
from ..languages import languages
from ..provider import Provider as BaseProvider


class Provider(BaseProvider):
    _required_attributes = {
        'api_key': None,
        'model': 'gpt-3.5-turbo-1106',
        'temperature': 0.67,
        'presence_penalty': 0.0,
        'frequency_penalty': 0.0,
    }

    def __init__(self,
                 logger: Optional[logging.Logger] = None,
                 attributes: Optional[Dict] = None):
        super().__init__(logger=logger, attributes=attributes)
        self._client = self.get_client()

    def get_client(self) -> AsyncOpenAI:
        return AsyncOpenAI(
            api_key=self.get_attribute('api_key', default_value=None))

    async def generate(self,
                       prompt: str,
                       function: Response,
                       language: str = "en",
                       act_as: Optional[str] = None) -> Optional[Dict]:

        messages = []

        if act_as is not None:
            messages.append({
                "role": "system",
                "content": f"You are {act_as}.",
            })
        full_language = self.set_language(language)
        if full_language is not None:
            full_language = languages[language]
            messages.append({
                "role": "system",
                "content": f"Please reply in {full_language}.",
            })
        messages.append({
            "role": "user",
            "content": prompt,
        })

        try:
            response = await self._client.chat.completions.create(
                temperature=self.get_attribute('temperature', 0.67),
                messages=messages,
                tools=[{
                    "type": "function",
                    "function": function.model_dump(),
                }],
                tool_choice={
                    "type": "function",
                    "function": {
                        "name": function.name,
                    },
                },
                presence_penalty=self.get_attribute('presence_penalty', 0.0),
                frequency_penalty=self.get_attribute('frequency_penalty', 0.0),
                model=self.get_attribute('model', 'gpt-3.5-turbo-1106'),
            )
        except Exception as e:
            raise RetryableError(f"OpenAI API exception: {e}")

        for choice in response.choices:
            if (choice.message is not None
                    and choice.message.tool_calls is not None
                    and len(choice.message.tool_calls) > 0):
                function_responses = choice.message.tool_calls
                for function_response in function_responses:
                    if function_response.function is not None:
                        arguments = function_response.function.arguments
                        return json.loads(arguments)

        raise RetryableError('Failed to extract json block')
