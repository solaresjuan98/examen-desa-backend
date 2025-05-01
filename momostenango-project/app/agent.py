from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.models.openai import OpenAIChat

agent = Agent(
    model=OpenRouter(
        id="qwen/qwen2.5-vl-32b-instruct:free"
    )
)

