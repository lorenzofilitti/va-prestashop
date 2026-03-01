from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # localhost
    localhost_endpoint: str

    # openai
    openai_api_key: str
    openai_default_model: str

    # redis
    api_account_key: str
    user_key: str
    host: str
    port: int
    username: str
    password: str

    # config
    graph_config_path: str
    provider: str