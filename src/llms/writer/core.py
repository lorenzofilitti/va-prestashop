import json
from string import Template

from llms.base_llm import BaseLLM, AgentState, LLMSettings
from llms.writer.prompt import WriterPrompt


class Writer(BaseLLM):
    def __init__(self):
        super().__init__(
            name="Writer", llm_settings=LLMSettings(), provider="ollama"
        )

    def construct_prompts(self, *args, **kwargs) -> tuple[str, str]:
        prompt = WriterPrompt()
        return prompt.get_system_prompt(), prompt.get_content_prompt()

    def run(self, state: AgentState):
        final_prompt = Template(self._content_prompt).substitute(
            user_query=state.user_query,
            instruction=state.instruction,
            conversation_history=state.conversation_history,
        )

        response = self.invoke(final_prompt)
        final_answer = response.get("response")

        # state
        state.user_query = state.user_query
        state.conversation_history = state.conversation_history
        state.route = state.route
        state.instruction = state.instruction
        state.final_answer = final_answer
        return state