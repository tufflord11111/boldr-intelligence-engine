"""Step 5: Weekly theme clustering — powered by Qwen."""
import json, re
from datetime import datetime
from pipeline.model_router import call_qwen


def _strip(text):
    return re.sub(r"^```json\s*|^```\s*|\s*```$", "", text.strip(), flags=re.MULTILINE).strip()


def cluster_themes(processed_tickets: list) -> dict:
    if not processed_tickets:
        return {"error": "no tickets", "themes": []}

    summary = "\n".join([
        f"- [{t.get('ticket_id')}] {t.get('question_type')} | {t.get('buyer_persona')} | {str(t.get('intent_summary',''))[:80]} | signal={t.get('marketing_signal')}"
        for t in processed_tickets if not t.get("error")
    ])

    prompt = f"""You are generating Boldr's weekly customer intelligence cluster report.
Boldr is a Singapore titanium watch micro-brand.

Tickets this period:
{summary}

Group into 5-7 meaningful themes. Respond ONLY with valid JSON, no markdown fences:
{{
  "report_date": "{datetime.now().strftime('%Y-%m-%d')}",
  "total_tickets": {len(processed_tickets)},
  "themes": [
    {{
      "theme_name": "descriptive name",
      "theme_slug": "snake_case",
      "ticket_count": 0,
      "ticket_ids": ["TKT-xxxx"],
      "top_questions": ["up to 3 questions"],
      "primary_personas": ["persona1"],
      "kb_gaps_count": 0,
      "marketing_signal_strength": "high|medium|low",
      "marketing_opportunity": "specific opportunity",
      "recommended_action": "concrete next step"
    }}
  ],
  "top_insight": "single most important finding",
  "urgent_gaps": ["ticket_ids needing immediate resolution"]
}}
Order by ticket_count descending."""

    try:
        raw = _strip(call_qwen(prompt, max_tokens=2000))
        return json.loads(raw)
    except Exception as e:
        return {"error": str(e), "themes": [], "report_date": datetime.now().strftime('%Y-%m-%d')}
