import yaml
from pydantic import BaseModel


class RouterConfig(BaseModel):
    model: str
    temperature: float


class ChatConfig(BaseModel):
    model: str
    temperature: float
    max_conversation: int


class EmbeddingsConfig(BaseModel):
    model: str
    dimensions: int


class OpenAIConfig(BaseModel):
    embeddings: EmbeddingsConfig
    chat: ChatConfig
    router: RouterConfig


class Config(BaseModel):
    openai: OpenAIConfig


def load_config_from_yaml(yaml_file_path: str) -> Config:
    with open(yaml_file_path, "r") as file:
        yaml_content = yaml.safe_load(file)
    return Config(**yaml_content)
