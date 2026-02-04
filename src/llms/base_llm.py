import os
from uuid import uuid4
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Optional, Literal

from pydantic import BaseModel
from ollama import Options

class LlmSettings(BaseModel):
    model: str
    format: Optional[str] = None
    stream: Optional[bool] = False
    options: Optional[Options] = None


class BaseLLM(ABC):
    def __init__(self, settings: LlmSettings):
        self.name = self.__str__()
        self.settings = settings

        self._llm_prompt = self.construct_prompts()
        self._endpoint = "http://localhost:11434/api/generate"

    @abstractmethod
    def generate_answer(self, system_prompt: str, prompt: str) -> str:
        pass

    @abstractmethod
    def construct_prompts(self, *args, **kwargs) -> tuple[str, str]:
        pass

