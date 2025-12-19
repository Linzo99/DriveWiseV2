from typing import Dict, Any
from pydantic_ai import Agent, RunContext
from dataclasses import dataclass

@dataclass
class AgentDeps:
    system_promt: str
    args: Dict[str, Any]


# Configure your LLM provider here
# Examples:
# - Groq: "groq:openai/gpt-oss-120b" (default)
# - OpenAI: "openai:gpt-4" or "openai:gpt-3.5-turbo"
# - Anthropic: "anthropic:claude-3-opus-20240229"
# - Google: "google:gemini-pro"
# - Mistral: "mistral:mistral-large-latest"
# See https://ai.pydantic.dev/models/ for all available models
agent = Agent(
    "groq:openai/gpt-oss-120b",
    deps_type=AgentDeps
)


@agent.system_prompt
async def format_prompt(ctx:RunContext[AgentDeps]):
    return ctx.deps.system_promt.format(**ctx.deps.args)
