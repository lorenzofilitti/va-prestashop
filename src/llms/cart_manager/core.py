from string import Template
from typing import List

from pydantic import BaseModel

from llms.base_llm import BaseLLM, AgentState, LLMSettings
from llms.cart_manager.prompt import CartManagerPrompt
from prestashop.utils import Product


class CartManagerResponse(BaseModel):
    products: List[Product]

class CartManager(BaseLLM):
    def __init__(self):
        super().__init__(
            name="CartManager",
            llm_settings=LLMSettings(
                format=CartManagerResponse
            ),
            provider="ollama"
        )

    def construct_prompts(self, *args, **kwargs) -> tuple[str, str]:
        prompt = CartManagerPrompt()
        return prompt.get_system_prompt(), prompt.get_content_prompt()

    def run(self, state: AgentState):
        final_prompt = Template(self._content_prompt).substitute(
            user_query=state.user_query,
            conversation_history=state.conversation_history,
        )

        response = self.invoke(final_prompt)
        products = response.products

        # state
        state.user_query = state.user_query
        state.conversation_history = state.conversation_history
        state.route = state.route
        state.instruction = state.instruction

        return state