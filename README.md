# LLM JSON Adapter

## What is it ?

When using LLMs from the system, you often expect to get output results in JSON: OpenAPI's GPT API has a mechanism called Function Calling, which can return JSON, but Google's Gemini does not seem to have that functionality.

Therefore, I have created a wrapper library to switch LLMs and get results in JSON. What this library can do is as follows.

- Allows you to define the results you want to get in JSON Schema
- Switch between LLMs (currently supports OpenAI's GPT, Google's Gemini, Ollama and Bedrock for Llama and Anthropic Claude).
- Retry a specified number of times if the JSON retrieval fails

## How to use

Use the following code to get the results in JSON.

| Parameter       | Description                                                                               |
|-----------------|-------------------------------------------------------------------------------------------|
| provider_name   | The name of the LLM provider to use. Currently, only "google" and "openai" are supported. |
| max_retry_count | The number of times to retry if the JSON retrieval fails.                                 |
| attributes      | The attributes to pass to the LLM provider.                                               |



### OpenAI

#### Libraries

You need to install `openai`.

#### Attributes

| Parameter         | Description                        |
|-------------------|------------------------------------|
| api_key           | The API key to use.                |
| model             | Model name. Default: gpt-3.5-turbo |
| temperature       | Default: 0.67                      |
| presence_penalty  | Default: 0                         |
| frequency_penalty | Default: 0                         |

#### Example

```python
from llm_json_adapter import LLMJsonAdapter, Response

adapter = LLMJsonAdapter(provider_name="openai", max_retry_count=3, attributes={
    "api_key": "Your API Key",
    "model": "text-davinci-003",
})
result = adapter.generate(
    prompt="prompt",
    language="en",
    act_as="Professional Software Service Business Analyst",
    function=Response(
        name="response name",
        description="response description",
        parameters={
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                            },
                            "description": {
                                "type": "string",
                            },
                        },
                        "required": ["title", "description"],
                    },
                },
            },
            "required": ["data"]
        },
    )
)
```

### Gemini

#### Libraries

You need to install `google-generativeai`.

#### Attributes

| Parameter | Description                                |
|-----------|--------------------------------------------|
| api_key   | The API key to use.                        |
| model     | Model name( Default: gemini-1.5-pro-latest |

#### Example

```python
from llm_json_adapter import LLMJsonAdapter, Response

adapter = LLMJsonAdapter(provider_name="google", max_retry_count=3, attributes={
    "api_key": "Your API Key",
    "model": "gemini-1.5-pro-latest",
})
result = adapter.generate(
    prompt="prompt",
    language="en",
    act_as="Professional Software Service Business Analyst",
    function=Response(
        name="response name",
        description="response description",
        parameters={
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                            },
                            "description": {
                                "type": "string",
                            },
                        },
                        "required": ["title", "description"],
                    },
                },
            },
            "required": ["data"]
        },
    )
)
```

### Ollama

You need to prepare the Ollama server. ( https://ollama.com/ )

#### Libraries

You need to install `ollama`.

#### Attributes

| Parameter | Description                     |
|-----------|---------------------------------|
| url       | http://localhost:11434          |
| model     | Model name ( Default: llama3 ). |

#### Example

```python
from llm_json_adapter import LLMJsonAdapter, Response

adapter = LLMJsonAdapter(provider_name="ollama", max_retry_count=3, attributes={
    "url": "http://localhost:11434",
    "model": "llama3",
})
result = adapter.generate(
    prompt="prompt",
    language="en",
    act_as="Professional Software Service Business Analyst",
    function=Response(
        name="response name",
        description="response description",
        parameters={
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                            },
                            "description": {
                                "type": "string",
                            },
                        },
                        "required": ["title", "description"],
                    },
                },
            },
            "required": ["data"]
        },
    )
)
```

### Bedrock

You need to setup the AWS Bedrock( https://aws.amazon.com/bedrock/ )

#### Libraries

You need to install `boto3`.

#### Attributes


| Parameter         | Description                                     |
|-------------------|-------------------------------------------------|
| access_key_id     | The access key id to use.                       |
| secret_access_key | The secret access key to use.                   |
| region            | Region. Default: us-east-1                      |
| model             | Default: anthropic.claude-3-haiku-20240307-v1:0 |
| max_tokens        | Default: 1024                                   |

#### Example

```python
from llm_json_adapter import LLMJsonAdapter, Response

adapter = LLMJsonAdapter(provider_name="bedrock", max_retry_count=3, attributes={
    "access_key_id": "<YOUR AWS ACCESS KEY>",
    "secret_access_key": "<YOUR AWS SECRET ACCESS KEY>",
    "region": "us-east-1",
    "model": "anthropic.claude-3-haiku-20240307-v1:0",
    "max_tokens": 1024,
})
result = adapter.generate(
    prompt="prompt",
    language="en",
    act_as="Professional Software Service Business Analyst",
    function=Response(
        name="response name",
        description="response description",
        parameters={
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                            },
                            "description": {
                                "type": "string",
                            },
                        },
                        "required": ["title", "description"],
                    },
                },
            },
            "required": ["data"]
        },
    )
)
```


