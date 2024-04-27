import json
import logging
from typing import Dict, List, Optional, Union

import boto3
from botocore.client import BaseClient

from ...exceptions import RetryableError
from ...objects import Response
from ...utilities import JsonUtility
from ..provider import Provider as BaseProvider


class Provider(BaseProvider):
    _required_attributes = {
        'access_key_id': None,
        'secret_access_key': None,
        'region': "us-east-1",
        'model': 'anthropic.claude-3-haiku-20240307-v1:0',
        'max_tokens': 1024,
    }

    def __init__(self,
                 logger: Optional[logging.Logger] = None,
                 attributes: Optional[Dict] = None):
        super().__init__(logger=logger, attributes=attributes)
        self._client = self.get_client()

    def get_client(self) -> BaseClient:
        return boto3.client(
            service_name="bedrock-runtime",
            aws_access_key_id=self.get_attribute('access_key_id',
                                                 default_value=None),
            aws_secret_access_key=self.get_attribute('secret_access_key',
                                                     default_value=None),
            region_name=self.get_attribute('region',
                                           default_value="us-east-1"),
        )

    def get_models(self) -> List[str]:
        result = []
        client = boto3.client(
            service_name="bedrock",
            aws_access_key_id=self.get_attribute('access_key_id',
                                                 default_value=None),
            aws_secret_access_key=self.get_attribute('secret_access_key',
                                                     default_value=None),
            region_name=self.get_attribute('region',
                                           default_value="us-east-1"),
        )
        response = client.list_foundation_models()
        for summary in response["modelSummaries"]:
            result.append(summary["modelId"])

        return result

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

        model_name = self.get_attribute(
            'model', default_value="anthropic.claude-3-haiku-20240307-v1:0")

        self.debug_log(f"Generated Prompt: {generated_prompt}")
        self.debug_log(f"Model ID: {model_name}")

        structured_body = self.generate_body_structure(model=model_name,
                                                       prompt=generated_prompt)

        self.debug_log(f"Structured Body: {structured_body}")

        response = self._client.invoke_model(modelId=model_name,
                                             body=json.dumps(structured_body))
        response_body = json.loads(response.get("body").read())

        self.debug_log(f"Response Body: {response_body}")

        result = self.extract_content(model=model_name,
                                      response_body=response_body)

        self.debug_log(f"Extracted Content: {result}")

        result = JsonUtility.extract_json_block(text=result)
        if not isinstance(result, dict):
            raise RetryableError('Failed to extract json block')

        return result

    # Parameters Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters.html
    def generate_body_structure(
            self, model: str, prompt: Union[List[Dict[str, str]],
                                            str]) -> dict:
        provider = model.split(".")[0]
        if provider == "anthropic":
            prompts = []
            system_messages = []
            for message in prompt:
                if message.get("role") == "user" or message.get(
                        "role") == "assistant":
                    prompts.append(message)
                if message.get("role") == "system":
                    system_messages.append(message.get("content"))

            return {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.get_attribute('max_tokens',
                                                 default_value=1024),
                "system": "\n".join(system_messages),
                "messages": prompts,
            }
        elif provider == "meta":
            prompt = self.convert_to_llama_presentation(messages=prompt)
            return {
                "prompt":
                prompt,
                "temperature":
                0.5,
                "top_p":
                0.9,
                "max_gen_len":
                self.get_attribute('max_tokens', default_value=1024),
            }
        else:
            return {}

    # Parameters Ref: https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters.html
    @staticmethod
    def extract_content(model: str, response_body: dict) -> str:
        provider = model.split(".")[0]
        if provider == "anthropic":
            content = response_body.get("content")
            texts = []
            for message in content:
                if message.get("type") == "text":
                    texts.append(message.get("text"))
            return "\n".join(texts)
        elif provider == "meta":
            return response_body.get("generation")
        else:
            return ""
