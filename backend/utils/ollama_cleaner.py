import re
from typing import Any, List, Optional
from langchain_core.messages import BaseMessage
from langchain_core.callbacks import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
from langchain_core.outputs import ChatResult
from langchain_ollama import ChatOllama

class CleanChatOllama(ChatOllama):
    def _clean_content(self, content: str) -> str:\
        return re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        result = super()._generate(messages, stop, run_manager, **kwargs)
        if result.generations:
            result.generations[0].message.content = self._clean_content(
                result.generations[0].message.content
            )
        return result
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        result = await super()._agenerate(messages, stop, run_manager, **kwargs)

        if result.generations:
            result.generations[0].message.content = self._clean_content(
                result.generations[0].message.content
            )
        return result