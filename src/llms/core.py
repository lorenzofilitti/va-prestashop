import logging
from typing import Dict
from src.llms.base_llm import BaseLLM, LlmSettings

import requests
from requests import Response
from tenacity import retry, wait_fixed, stop_after_attempt

class Core(BaseLLM):
    def __init__(self, settings: LlmSettings):
        super().__init__(settings)
        self.system_prompt = self.construct_prompts()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def generate_answer(self, prompt: str) -> Dict:
        endpoint = self._endpoint
        body = {
            "model": self.settings.model,
            "system": self.system_prompt,
            "prompt": prompt,
            "stream": False,
            "format": self.settings.format,
            "options": self.settings.options,
        }
        if self.settings.format:
            body["stream"] = False
        else:
            body.pop("format")
        try:
            response: Response = requests.post(endpoint, json=body)
            print(f"Status code: {response.status_code}")
            print(f"Response text: {response.text}")

            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Failed to generate answer: {e}. Retrying in 2 seconds.")
            raise


    def construct_prompts(self) -> str:
        return "You are evil Dante Alighieri. You only speak 1300 b.C Italian."



if __name__ == "__main__":
    settings = LlmSettings(
        model="llama3.2",
        stream=False,
    )
    llm = Core(settings)
    name = llm.name
    sy, us = llm.construct_prompts()
    print(llm.generate_answer(sy, us))



