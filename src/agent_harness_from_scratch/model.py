"""Step 0.1: call a chat model once.

Any OpenAI-compatible server works (local Ollama, Hugging Face router, OpenAI).
Which one is chosen by three settings in `.env`; see `.env.example`.
"""

import os
import sys

from dotenv import find_dotenv, load_dotenv
from openai import OpenAI

# usecwd=True: look for .env starting from the folder you run the command in.
load_dotenv(find_dotenv(usecwd=True))

DEFAULT_BASE_URL = "http://localhost:11434/v1"  # local Ollama
DEFAULT_API_KEY = "ollama"  # Ollama ignores the key, but the SDK requires one
DEFAULT_MODEL = "qwen3.5:9b"


def make_client() -> OpenAI:
    """Build a client for the server named by MODEL_BASE_URL."""
    return OpenAI(
        base_url=os.getenv("MODEL_BASE_URL", DEFAULT_BASE_URL),
        api_key=os.getenv("MODEL_API_KEY", DEFAULT_API_KEY),
    )


def call_model(prompt: str) -> str:
    """Send one user message to the model and return its text reply."""
    client = make_client()
    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME", DEFAULT_MODEL),
        messages=[{"role": "user", "content": prompt}],
    )
    # content is None when the model replies only with tool calls (step 0.5).
    return response.choices[0].message.content or ""


def main() -> None:
    prompt = " ".join(sys.argv[1:]) or "What is the capital of France?"
    print(call_model(prompt))


if __name__ == "__main__":
    main()
