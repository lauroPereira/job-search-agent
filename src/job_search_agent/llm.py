"""Model provider interface. The only module that imports langchain_openai.

The rest of the project receives a BaseChatModel and an Embeddings, which also allows the
simulated model of the tests and of the evaluation.

`python -m job_search_agent.llm --smoke` makes one minimal real call to each configured model
(needs OPENAI_API_KEY in .env; never run in CI).
"""

import argparse
import os
import sys

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from job_search_agent.config import CHAT_ROLES, Config, load_config


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
    return smoke(load_config())


if __name__ == "__main__":
    raise SystemExit(main())
