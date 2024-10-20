from typing import List, Any

import openai
import asyncio

from sapperrag.llm.base import BaseLLM


class ChatOpenAI(BaseLLM):
    def __init__(self, openai_key: str, base_url: str):
        self.api_key = openai_key
        self.client = openai.OpenAI(api_key=openai_key, base_url=base_url)

    async def async_init(self):
        self.client = openai.AsyncOpenAI(api_key=self.api_key)

    async def process_message(self, messages: List[dict]):
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                ),
                timeout=360  # Timeout in seconds
            )
            return response
        except asyncio.TimeoutError:
            print("Request timed out")
        except Exception as e:
            print(f"An error occurred: {e}")

    def generate(self, messages: List[dict], response_format: str = "text", streaming: bool = False,  **kwargs: Any) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_format={"type": response_format}
        )
        return response.choices[0].message.content

    async def agenerate(self, messages: List[dict], streaming: bool = False, **kwargs: Any) -> str:
        response = await self.process_message(messages)
        return response.choices[0].message.content
