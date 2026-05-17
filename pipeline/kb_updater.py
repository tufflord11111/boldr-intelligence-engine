"""Step 4: Auto-draft KB entry — powered by Qwen."""
import json, re
from pathlib import Path
from datetime import datetime
from pipeline.model_router import call_qwen


def _strip(text):
    return re.sub(r"^```json\s*|^```\s*|\s*```$", "", text.strip(), flags=re.MULTILINE).strip()


def draft_kb_entry(gap: dict, cs_resolution: str, output_dir: Path) -> dict:
    prompt = f"""Draft a new FAQ entry for Boldr's knowledge base (Singapore titanium watch brand).

Customer asked: "{gap.get('intent_summary', gap.get('question', ''))}"
CS team answer: "{cs_resolution}"
Buyer persona: {gap.get('buyer_persona', 'general')}
Marketing signal: {gap.get('marketing_signal', False)}

Respond ONLY with valid JSON, no markdown fences:
{{
  "faq_id": "FAQ-{datetime.now().strftime('%Y%m%d')}-001",
  "question": "canonical clean question",
  "answer": "full answer in Boldr brand voice — friendly, direct, premium. Never start with Great question!",
  "category": "materials_safety|engraving|servicing|strap_compatibility|product_general|sustainability",
  "persona_tags": ["list", "of", "personas"],
  "marketing_flag": true or false,
  "marketing_action": "specific product/page/campaign action or null",
  "created_from_ticket": "{gap.get('ticket_id', 'unknown')}",
  "status": "pending_approval",
  "created_at": "{datetime.now().isoformat()}"
}}"""

    try:
        raw = _strip(call_qwen(prompt, max_tokens=800))
        entry = json.loads(raw)
    except Exception as e:
        entry = {"error": str(e), "created_from_ticket": gap.get("ticket_id"), "status": "error"}

    output_dir.mkdir(parents=True, exist_ok=True)
    fname = output_dir / f"{gap.get('ticket_id','unknown')}_{datetime.now().strftime('%H%M%S')}.json"
    with open(fname, "w") as f:
        json.dump(entry, f, indent=2)
    print(f"  KB entry drafted → {fname.name}")
    return entry
