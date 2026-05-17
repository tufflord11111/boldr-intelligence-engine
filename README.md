# Boldr Self-Improving Customer Intelligence Engine
**ECSG2026 AI Workflow Competition — Revenue Rocket Track**

**Live Demo:** https://n1njla-boldr-intelligence-engine.hf.space

## The Problem
Boldr's 3-person CS team answers 70+ customer emails weekly. Every answer is forgotten. Novel questions about BPA-free materials, sustainability, and product specs disappear into inboxes instead of feeding back into marketing strategy.

## The 7-Step Workflow
1. **Ingest** — Customer email received, intent extracted, buyer persona tagged (Qwen Plus)
2. **KB Search** — FAISS semantic search across FAQ PDF, rate cards, SOP, product docs
3a. **Draft Reply** — If answerable: reply drafted in Boldr brand voice, queued for human approval
3b. **Flag Gap** — If not answerable: gap flagged with details, routed to CS team. Never hallucinates.
4. **KB Update** — When CS resolves gap: AI auto-drafts new FAQ entry for 1-click approval
5. **Theme Cluster** — Weekly: tickets grouped by theme and buyer persona
6. **Marketing Brief** — Monthly: "What customers ask that isn't on your product pages"
7. **BONUS** — External sentiment benchmarking vs WatchUSeek, Reddit, Amazon reviews

## Tech Stack
- **Qwen Plus** (Alibaba Cloud) — All AI processing. $50 sponsor credit.
- **FAISS** — Local vector KB search, zero hosting cost
- **Flask** — Human approval UI
- **Python** — Orchestration

## Key Results
- 70 tickets processed, 0 errors
- 35 replies drafted, 35 gaps flagged
- 37 marketing signals detected
- 6 theme clusters identified
- SGD 0.08 per ticket vs SGD 2.39 manually (97% reduction)
- SGD 8,125 annual saving

## How to Run
```bash
pip install -r requirements.txt
# Set QWEN_API_KEY in .env
python main.py          # demo: 10 tickets
python main.py --full   # all 70 tickets
python -m approval_ui.app  # launch UI at localhost:5000
```

## Responsible AI
- Human approval required before any reply sends
- Never hallucinates — gaps flagged, not fabricated
- KB updates require 1-click human approval
- No PII stored externally
