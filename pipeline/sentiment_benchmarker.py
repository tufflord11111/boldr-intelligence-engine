"""BONUS: External sentiment benchmarking — powered by Qwen."""
import json, re
from datetime import datetime
from pipeline.model_router import call_qwen


def _strip(text):
    return re.sub(r"^```json\s*|^```\s*|\s*```$", "", text.strip(), flags=re.MULTILINE).strip()


def benchmark(cluster: dict, external_data: list) -> dict:
    if not external_data:
        return {"error": "no external data", "benchmarked_themes": []}

    themes = json.dumps([
        {"theme": t.get("theme_name"), "tickets": t.get("ticket_count"),
         "signal": t.get("marketing_signal_strength"), "personas": t.get("primary_personas")}
        for t in cluster.get("themes", [])
    ], indent=2)

    ext = json.dumps([
        {"source": r.get("source"), "theme": r.get("theme"),
         "sentiment": r.get("sentiment"), "frequency": r.get("frequency"),
         "excerpt": str(r.get("excerpt",""))[:100]}
        for r in external_data
    ], indent=2)

    prompt = f"""You are a market intelligence analyst for Boldr watches (Singapore titanium micro-brand).

INTERNAL TICKET THEMES:
{themes}

EXTERNAL FORUM/REVIEW DATA:
{ext}

Cross-validate at least 3 themes. Respond ONLY with valid JSON, no markdown fences:
{{
  "generated_at": "{datetime.now().isoformat()}",
  "benchmarked_themes": [
    {{
      "theme": "theme name",
      "internal_ticket_count": 0,
      "internal_signal_strength": "high|medium|low",
      "external_sources": ["sources"],
      "external_sentiment": "positive|negative|neutral|mixed",
      "external_frequency": "high|medium|low",
      "verdict": "boldr_specific|market_wide|boldr_advantage",
      "verdict_explanation": "cite evidence from both sources",
      "boldr_action": "specific recommended action"
    }}
  ],
  "key_finding": "most strategically important finding",
  "first_mover_opportunity": "which theme gives Boldr biggest first-mover advantage and why"
}}"""

    try:
        raw = _strip(call_qwen(prompt, max_tokens=2000))
        return json.loads(raw)
    except Exception as e:
        return {"error": str(e), "benchmarked_themes": [], "generated_at": datetime.now().isoformat()}
