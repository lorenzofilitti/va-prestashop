import logging
from abc import ABC, abstractmethod
from typing import Optional, Literal, Any, Callable, List

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
from langchain_openai.chat_models import ChatOpenAI
from tenacity import retry, stop_after_attempt, wait_fixed
from langchain_ollama.chat_models import ChatOllama
from yaml import safe_load

from config.project_config import Settings


class AgentState(BaseModel):
    # Conversation
    user_query: Optional[str] = None
    conversation_history: list[dict] = Field(default_factory=list)

    search_query: Optional[str] = None

    # Flow control
    route: Optional[str] = None
    instruction: Optional[str] = None
    cart_confirmed: bool = False
    cart_populated: bool = False

    final_answer: str = None

class LLMSettings(BaseModel):
    model: Optional[str] = "llama3.2"
    temperature: Optional[float] = Field(
        default=0.0,
        description="LLM temperature",
    )
    format: Optional[Any] = Field(
        default=None,
        description="LLM response schema"
    )


class BaseLLM(ABC):
    def __init__(
            self,
            name: str,
            llm_settings: LLMSettings = LLMSettings(),
            provider: Literal["ollama", "openai"] = "ollama"
    ):
        self._env_settings = Settings()
        self._llm_settings = llm_settings
        self._graph_config = safe_load(open(self._env_settings.graph_config_path))
        self.provider = provider

        self._localhost_endpoint = self._env_settings.localhost_endpoint
        self._openai_api_key = self._env_settings.openai_api_key

        self.name = name
        self._llm = self._instantiate_openai_agent() if provider == "openai" else self._instantiate_ollama_agent()
        self._system_prompt, self._content_prompt = self.construct_prompts()


    @abstractmethod
    def construct_prompts(self, *args, **kwargs) -> tuple[str, str]:
        pass

    @property
    def dependent_nodes(self) -> List[str]:
        nodes = [e["to"] for e in self._graph_config["graph_architecture"]["edges"] if e["from"] == self.name]
        return nodes

    def invoke(self, prompt: str, tools: List[Callable] = None) -> Any:
        return self._invoke(prompt, tools)

    def _instantiate_openai_agent(self):
        llm = ChatOpenAI(
            model=self._llm_settings.model,
            temperature=self._llm_settings.temperature,
        )
        if self._llm_settings.format is not None:
            return llm.with_structured_output(self._llm_settings.format)

        return llm

    def _instantiate_ollama_agent(self):
        llm = ChatOllama(
            model=self._llm_settings.model,
            temperature=self._llm_settings.temperature,
        )
        if self._llm_settings.format is not None:
            return llm.with_structured_output(self._llm_settings.format)

        return llm

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def _invoke(
            self,
            prompt: str,
            tools: List[Callable],
    ) -> AIMessage:
        messages = [
            SystemMessage(content=self._system_prompt),
            HumanMessage(content=prompt),
        ]
        try:
            if tools:
                llm_w_tools = self._llm.bind_tools(tools)
                response = llm_w_tools.invoke(messages)
            else:
                response = self._llm.invoke(prompt)

        except Exception as e:
            logging.error(f"Failed to invoke {self.provider} agent: {e}")
            raise

        return response