"""Steps 1 & 3: Full ticket processor — 100% Qwen."""
import json, re
from datetime import datetime
from pipeline.model_router import call_qwen

SYSTEM_CONTEXT = """You are the AI backbone of Boldr's customer intelligence engine.
Boldr is a Singapore-based titanium watch micro-brand selling via Shopify.
Brand voice: friendly but not overly casual, direct, helpful, premium.
Reply format: Start with "Hi [Name]," — NEVER "Great question!" or "Dear Sir/Madam". Keep replies 3-5 sentences.
CRITICAL: If KB does not clearly answer the question, return kb_match: false. NEVER hallucinate."""


def _strip(text):
    return re.sub(r"^```json\s*|^```\s*|\s*```$", "", text.strip(), flags=re.MULTILINE).strip()


def process_ticket(ticket: dict, kb_context: str) -> dict:
    ticket_id = ticket.get("ticket_id", "unknown")
    subject = ticket.get("subject", "")
    body = ticket.get("message_body", ticket.get("body", ""))

    prompt = f"""{SYSTEM_CONTEXT}

KNOWLEDGE BASE:
{kb_context[:5000]}

CUSTOMER TICKET:
ID: {ticket_id}
Subject: {subject}
Message: {body}

Respond ONLY with valid JSON, no markdown fences:
{{
  "ticket_id": "{ticket_id}",
  "intent_summary": "one sentence what customer is asking",
  "question_type": "materials_safety|engraving|servicing|strap_compatibility|order_status|product_general|knowledge_gap",
  "buyer_persona": "health_conscious|gifter|enthusiast|active_outdoor|sustainability_advocate|owner_aftercare|transactional|prospect|niche_buyer",
  "persona_reasoning": "cite 1-2 keywords from message",
  "kb_match": true or false,
  "kb_source": "which KB file section answered this, or null",
  "confidence": "high|medium|low",
  "action": "draft_reply or flag_gap",
  "draft_reply": "if kb_match true: full reply in Boldr brand voice starting with Hi [Name],. Write a complete warm helpful reply. null if not answerable.",
  "gap_details": "if kb_match false: what is missing from KB and suggested direction. null if answerable.",
  "marketing_signal": true or false,
  "marketing_note": "if this reveals an untapped product or marketing opportunity, describe it briefly. null if not."
}}

Rules:
- If KB clearly answers: kb_match=true, action=draft_reply, write a complete reply
- If KB does NOT answer: kb_match=false, action=flag_gap, draft_reply=null
- draft_reply must be warm, direct, premium — 3-5 sentences max"""

    try:
        raw = _strip(call_qwen(prompt, max_tokens=1000))
        result = json.loads(raw)
        result["status"] = "pending_human_approval" if result.get("kb_match") else "flagged_gap"
        result["processed_at"] = datetime.now().isoformat()
        return result
    except Exception as e:
        return {
            "ticket_id": ticket_id,
            "error": str(e),
            "action": "flag_gap",
            "status": "error",
            "processed_at": datetime.now().isoformat()
        }
