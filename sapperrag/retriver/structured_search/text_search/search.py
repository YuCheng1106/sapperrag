import json
import time
import asyncio
from typing import Any

import pandas as pd

from ....llm.base import BaseLLM
from ....retriver.context_builder.builders import TextContextBuilder
from ....retriver.structured_search.base import BaseSearch
from ....retriver.structured_search.text_search.system_prompt import TEXT_SEARCH_SYSTEM_PROMPT


class TextSearch(BaseSearch):
    """Search orchestration for local search mode."""

    def __init__(
            self,
            context_builder: TextContextBuilder,
            llm: BaseLLM,
            system_prompt: str = TEXT_SEARCH_SYSTEM_PROMPT,
    ):
        super().__init__(context_builder=context_builder, llm=llm)
        self.system_prompt = system_prompt
        self.context_data = dict[str, dict]()
        self.context_text = ""

    def search(self, query: str, **kwargs: Any):
        """Build local search context that fits a single context window and generate answer for the user question."""
        start_time = time.time()

        # 生成搜索上下文
        context_text, context_data = self.context_builder.build_context(query, **kwargs)
        # 执行搜索操作
        self.context_text = context_text
        self.context_data = {key: value.to_dict() for key, value in context_data.items()}

        # print(context_text)
        search_prompt = self.system_prompt.format(
            context_data=context_text, response_type="plain"
        )
        search_messages = [
            {"role": "system", "content": search_prompt},
            {"role": "user", "content": query},
        ]

        results = self.llm.generate(search_messages)
        return results

    async def asearch(self, query: str, **kwargs: Any):
        """Build local search context that fits a single context window and generate answer for the user query."""
        loop = asyncio.get_event_loop()
        # 生成搜索上下文
        context = self.context_builder.build_context(query, **kwargs)
        # 使用异步执行器执行搜索操作
        results = await loop.run_in_executor(None, self._perform_search, context, query)
        return results

    def _perform_search(self, context: Any, query: str):
        """执行实际的搜索操作."""
        # 模拟搜索操作
        print(f"Performing search for query: '{query}' with context: {context}")
        time.sleep(1)  # 模拟搜索延迟
        return [{"result": f"Result for '{query}'"}]
