import json
import logging
import re
from typing import Dict, Optional

import google.generativeai as genai
from google.generativeai.generative_models import GenerativeModel

from ...exceptions import RetryableError
from ...objects import Response
from ..languages import languages
from ..provider import Provider as BaseProvider


class Provider(BaseProvider):
    _required_attributes = {
        'api_key': None,
        'model': 'gemini-pro',
    }

    def __init__(self,
                 logger: Optional[logging.Logger] = None,
                 attributes: Optional[Dict] = None):
        super().__init__(logger=logger, attributes=attributes)
        self._client = self.get_client()

    def get_client(self) -> GenerativeModel:
        genai.configure(
            api_key=self.get_attribute('api_key', default_value=None))
        model = genai.GenerativeModel(
            model_name=self.get_attribute('model', default_value=None))
        return model

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
            f"And use Json format as the response format which defined as following: \n\n"
            f"\n{json_format}\n\n")

        generated_prompt += "and response json data should be wrapped by the markdown code block\n\n"
        return generated_prompt

    @staticmethod
    def extract_json_block(text: str) -> Optional[Dict]:
        pattern = r'```(.*?)\n(.*?)```'
        code_blocks = re.findall(pattern, text, re.DOTALL)
        if len(code_blocks) == 0:
            return None
        json_data = code_blocks[0][1]
        return json.loads(json_data)

    async def generate(self,
                       prompt: str,
                       function: Response,
                       language: str = "en",
                       act_as: Optional[str] = None) -> Optional[Dict]:

        generated_prompt = self.generate_prompt(
            prompt=prompt,
            function=function,
            language=language,
            act_as=act_as,
        )

        try:
            response = self._client.generate_content(generated_prompt)
        except Exception as e:
            raise RetryableError(f"Google API exception: {e}")

        result = self.extract_json_block(response.text)
        if not isinstance(result, dict):
            raise RetryableError('Failed to extract json block')

        return result
