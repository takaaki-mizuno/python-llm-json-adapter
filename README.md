# LLM JSON Adapter

## What is it ?

When using LLMs from the system, you often expect to get output results in JSON: OpenAPI's GPT API has a mechanism called Function Calling, which can return JSON, but Google's Gemini does not seem to have that functionality.

Therefore, I have created a wrapper library to switch LLMs and get results in JSON. What this library can do is as follows.

- Allows you to define the results you want to get in JSON Schema
- Switch between LLMs (currently supports OpenAI's GPT and Google's Gemini).
- Retry a specified number of times if the JSON retrieval fails

## How to use

Use the following code to get the results in JSON.

| Parameter | Description |
| --- | --- |
| provider_name | The name of the LLM provider to use. Currently, only "google" and "openai" are supported. |
| max_retry_count | The number of times to retry if the JSON retrieval fails. |
| attributes | The attributes to pass to the LLM provider. |

### Attributes

| Parameter | Description |
| --- | --- |
| api_key | The API key to use. |


```python
from llm_json_adapter import LLMJsonAdapter, Response

adapter = LLMJsonAdapter(provider_name="google", max_retry_count=3, attributes={
    "api_key": "Your API Key"
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


