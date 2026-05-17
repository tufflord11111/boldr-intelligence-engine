"""Step 6: Monthly marketing brief — powered by Qwen."""
from datetime import datetime
from pipeline.model_router import call_qwen


def generate_brief(cluster: dict, external_data: list = None) -> str:
    ext = ""
    if external_data:
        ext = "\n\nEXTERNAL SENTIMENT:\n" + "\n".join([
            f"- [{r.get('source')}] {r.get('theme')} | {r.get('sentiment')} | {str(r.get('excerpt',''))[:100]}"
            for r in external_data
        ])

    prompt = f"""Write Boldr's monthly Customer Intelligence Brief for the founder and marketing lead.
Boldr is a Singapore titanium watch micro-brand selling via Shopify.

CLUSTER DATA:
{str(cluster)[:3000]}
{ext}

Write an actionable brief in markdown. Structure:

# Boldr Customer Intelligence Brief — {datetime.now().strftime('%B %Y')}

## Executive Summary
[2-3 sentences. Lead with biggest revenue insight.]

## What Customers Are Asking (Not On Your Product Pages)
[Top themes: ticket count, personas, specific questions, gap]

## 🥇 #1 Marketing Opportunity — What Boldr Doesn't Know Yet
[The single biggest untapped angle with specific action. Lead with BPA-free/health-conscious if present.]

## Theme Breakdown
| Theme | Tickets | Personas | Signal | Action |
[One row per theme]

## External Sentiment Cross-Validation
[For each theme: Boldr-specific or market-wide? Strategic implication.]

## Recommended Actions (Priority Order)
1. [Most urgent, most specific]
2.
3.

## New FAQ Entries Needed This Week
- [Specific gaps to become KB entries]

Tone: direct, data-driven, written for a founder who wants to know exactly what to do next week."""

    try:
        return call_qwen(prompt, max_tokens=2000)
    except Exception as e:
        return f"# Brief generation error\n\n{e}"
