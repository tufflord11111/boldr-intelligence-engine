# Boldr Intelligence Engine
**ECSG2026 AI Workflow Competition** | **Track:** Revenue Rocket
**Builder:** Cayden Chai Ming Yang

## Overview
The Boldr Intelligence Engine is a self-improving B2B customer intelligence pipeline designed for SME e-commerce brands. It transforms reactive customer support (where emails are answered and forgotten) into a proactive marketing intelligence engine. 

Instead of a standard chatbot, this workflow ingests customer emails, drafts bilingual replies, flags knowledge gaps without hallucinating, and surfaces hidden marketing insights (like the "BPA-Free" campaign opportunity) directly to the founders.

## The 7-Step Autonomous Pipeline
1. **Intent & Persona Extraction:** Analyzes incoming tickets via Qwen.
2. **Semantic Search:** Queries a local FAISS vector index of PDFs, DOCXs, and SOPs.
3. **Draft or Flag:**
   * **If Answerable:** Drafts a reply in the brand's exact tone (English & Mandarin) and queues for human approval.
   * **If Not Answerable:** Flags a knowledge gap to the CS team to prevent hallucinations.
4. **Auto-KB Updates:** Once a human resolves the gap, the system auto-drafts a new Knowledge Base entry.
5. **Theme Clustering:** Groups weekly tickets by business intent.
6. **Marketing Briefs:** Generates a monthly intelligence report highlighting underserved buyer needs.
7. **Sentiment Benchmarking:** Cross-validates internal signals with external forum/Reddit data.

## Tech Stack
* **AI/LLM:** Qwen Plus (Alibaba Cloud)
* **Vector Database:** FAISS + sentence-transformers
* **Backend/Orchestration:** Python
* **Frontend/Approval UI:** Flask + HTML/CSS

## Business Impact & ROI
* **Cost Efficiency:** Reduces cost per ticket from SGD 2.39 (manual) to SGD 0.08. 
* **Time Saved:** 97% reduction in processing time.
* **Revenue Generation:** Automatically isolates and prioritizes hidden marketing signals to drive new product campaigns.

## Setup and Installation

**1. Clone the repository:**
```bash
git clone [https://github.com/tufflord11111/boldr-intelligence-engine.git](https://github.com/tufflord11111/boldr-intelligence-engine.git)
cd boldr-intelligence-engine
2. Install dependencies:

Bash
py -m pip install -r requirements.txt
3. Set your API Key (Windows PowerShell):

Bash
$env:QWEN_API_KEY = "your-qwen-key-here"
4. Run the core pipeline:

Bash
py main.py --full
5. Launch the Approval UI:

Bash
py -m approval_ui.app
Access the dashboard at: http://localhost:5000
