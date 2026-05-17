"""
Boldr Intelligence Engine — Multi-Model Router
Claude → reply drafting (brand voice critical)
Qwen  → clustering, briefs, KB entries, benchmarking (bulk processing)
"""
import os
from dotenv import load_dotenv
load_dotenv()

import anthropic
from openai import OpenAI

# Claude — for brand-voice reply drafting only
def get_claude():
    return anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Qwen — for all bulk processing steps
def get_qwen():
    return OpenAI(
        api_key=os.environ.get("QWEN_API_KEY"),
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    )

CLAUDE_MODEL = "claude-haiku-4-5-20251001"   # cheapest Claude, brand voice
QWEN_MODEL   = "qwen-plus"                    # Qwen bulk processing


def call_claude(prompt: str, max_tokens: int = 1000) -> str:
    """Call Claude for brand-voice reply drafting."""
    client = get_claude()
    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


def call_qwen(prompt: str, max_tokens: int = 1500) -> str:
    """Call Qwen for bulk processing — clustering, briefs, KB entries."""
    client = get_qwen()
    response = client.chat.completions.create(
        model=QWEN_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens
    )
    return response.choices[0].message.content
