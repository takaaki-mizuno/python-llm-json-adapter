from pathlib import Path

import toml

from llm_json_adapter import __version__, LLMJsonAdapter


def test_version():
    file = Path(__file__).parent.parent.joinpath("pyproject.toml")
    data = toml.loads(file.read_text(encoding="utf-8"))

    if "tool" in data and "poetry" in data["tool"] and "version" in data["tool"]["poetry"]:
        project_version = data["tool"]["poetry"]["version"]
        assert __version__ == project_version


def test_create_openai_instance():
    adapter = LLMJsonAdapter(provider_name="openai", max_retry_count=3, attributes={
        "api_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    })
    assert adapter is not None

