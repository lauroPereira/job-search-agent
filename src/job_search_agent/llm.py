"""Model provider interface. The only module that imports langchain_openai.

The rest of the project receives a BaseChatModel and an Embeddings, which also allows the
simulated model of the tests and of the evaluation.

`ScriptedChatModel` is the simulated model of the tests and of the evaluation: it returns scripted
messages (with `tool_calls` and `usage_metadata`), without network.

`python -m job_search_agent.llm --smoke` makes one minimal real call to each configured model
(needs OPENAI_API_KEY in .env; never run in CI).
"""

import argparse
import os
import sys
from typing import Any

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import Field

from job_search_agent.config import CHAT_ROLES, Config, ConfigError, load_config


def chat_model(role: str, config: Config) -> BaseChatModel:
    """Chat model of a role ("router" or "agent"), always through the Responses API."""
    if role not in CHAT_ROLES:
        raise ValueError(f"Unknown model role {role!r}; use one of {CHAT_ROLES}")
    return ChatOpenAI(
        model=config.models[role],
        use_responses_api=True,
        reasoning={"effort": config.reasoning[role]},
        max_tokens=config.limits.max_output_tokens,
    )


def embeddings(config: Config) -> Embeddings:
    return OpenAIEmbeddings(model=config.models["embeddings"])


class ScriptedChatModel(BaseChatModel):
    """Simulated model: answers each call with the next message of `script`, in order.

    `bind_tools` returns the model itself, so the same script serves `create_agent` and the
    structured output of the router (a tool call named after the schema). Every list of messages
    received is kept in `received`, so a test can check the prompts.
    """

    script: list[AIMessage]
    received: list[list[BaseMessage]] = Field(default_factory=list)
    position: int = 0

    @property
    def _llm_type(self) -> str:
        return "scripted"

    def _generate(self, messages: list[BaseMessage], stop=None, run_manager=None, **kwargs):
        self.received.append(list(messages))
        if self.position >= len(self.script):
            raise RuntimeError(f"Scripted model has no answer left ({len(self.script)} used)")
        message = self.script[self.position].model_copy(deep=True)
        self.position += 1
        return ChatResult(generations=[ChatGeneration(message=message)])

    def bind_tools(self, tools: Any, **kwargs: Any) -> "ScriptedChatModel":
        return self


@tool
def echo_word(word: str) -> str:
    """Return the given word. Used only by the smoke test to check tool calling."""
    return word


def smoke(config: Config) -> int:
    """One minimal call per chat model (plain and with a tool) and one short embedding."""
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set (put it in .env); smoke test not run.", file=sys.stderr)
        return 2
    for role in CHAT_ROLES:
        model = chat_model(role, config)
        reply = model.invoke("Answer only with the word: ok")
        print(
            f"[{role}] requested={config.models[role]} "
            f"returned={reply.response_metadata.get('model_name')} "
            f"text={reply.text!r} usage={reply.usage_metadata}"
        )
        tool_reply = model.bind_tools([echo_word]).invoke(
            "Call the echo_word tool with the word 'ping'. Do not answer with text."
        )
        print(f"[{role}] tool_calls={tool_reply.tool_calls} usage={tool_reply.usage_metadata}")
    vector = embeddings(config).embed_query("ok")
    print(f"[embeddings] model={config.models['embeddings']} dimensions={len(vector)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m job_search_agent.llm")
    parser.add_argument(
        "--smoke", action="store_true", help="make one minimal real call to each model"
    )
    arguments = parser.parse_args(argv)
    if not arguments.smoke:
        parser.print_help()
        return 0
    try:
        config = load_config()
    except ConfigError as failure:
        print(failure, file=sys.stderr)
        return 1
    return smoke(config)


if __name__ == "__main__":
    raise SystemExit(main())
