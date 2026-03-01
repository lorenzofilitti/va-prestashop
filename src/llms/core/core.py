from string import Template

from pydantic import BaseModel, Field
from langchain.tools import tool

from src.llms.base_llm import BaseLLM, AgentState, LLMSettings
from llms.core.prompt import CorePrompt


class CoreAgentResponse(BaseModel):
    reasoning: str = Field(description="Your decisional process")
    route: str = Field(description="The node to route the flow")
    instruction: str = Field(description="Instruction to provide to your nodes")

class Core(BaseLLM):
    def __init__(self):
        llm_settings = LLMSettings(
            format=CoreAgentResponse
        )
        super().__init__(name="Core", llm_settings=llm_settings, provider="ollama")

    def construct_prompts(self) -> tuple[str, str]:
        prompt = CorePrompt(
            dependent_nodes=self.dependent_nodes
        )
        return prompt.get_system_prompt(), prompt.get_content_prompt()

    @staticmethod
    @tool
    def consult_db(product_name: str):
        """
        test
        :param product_name:
        :return:
        """
        pass

    def run(self, state: AgentState):
        final_prompt = Template(self._content_prompt).substitute(
            user_query=state.user_query,
            conversation_history=state.conversation_history,
        )

        response = self.invoke(final_prompt)
        route = response.route
        instruction = response.instruction

        # state
        state.user_query = state.user_query
        state.conversation_history = state.conversation_history
        state.route = route
        state.instruction = instruction

        return state


