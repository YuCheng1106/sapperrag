from dotenv import load_dotenv
import os

from sapperrag.llm.oai import ChatOpenAI
from copyboost.macro_revise.revisor_generate import RevisorGenerate

load_dotenv("../.env")
openai_key = os.getenv("OPENAI_KEY")
base_url = os.getenv("OPENAI_BASE_URL")


if not openai_key:
    raise ValueError("OPENAI_KEY not found in environment variables.")


chatgpt = ChatOpenAI(openai_key, base_url)
revisor_generator = RevisorGenerate(chatgpt)

revisor_generator.learn('../input')





