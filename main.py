"""
Boldr Self-Improving Customer Intelligence Engine
ECSG2026 · AI Workflow Competition · Revenue Rocket Track

Run:
  py main.py           # demo mode — 10 curated tickets
  py main.py --full    # full mode — all 70 tickets
"""
import os, sys, json, csv, argparse
from pathlib import Path
from dotenv import load_dotenv

# Load .env first
load_dotenv()

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))

OUTPUT_DIR = BASE / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
(OUTPUT_DIR / "new_kb_entries").mkdir(exist_ok=True)

from pipeline.kb_loader import KBLoader
from pipeline.ticket_processor import process_ticket
from pipeline.kb_updater import draft_kb_entry
from pipeline.theme_clusterer import cluster_themes
from pipeline.marketing_brief import generate_brief
from pipeline.sentiment_benchmarker import benchmark

# Curated demo tickets showing all workflow branches
DEMO_TICKET_IDS = [
    "TKT-1048",  # materials_safety | health_conscious | BPA-free | MARKETING SIGNAL
    "TKT-1046",  # knowledge_gap | niche_buyer | magnetic fields | MARKETING SIGNAL
    "TKT-1047",  # engraving | gifter | caseback engraving
    "TKT-1036",  # knowledge_gap | sustainability | vegan materials | MARKETING SIGNAL
    "TKT-1001",  # servicing | owner_aftercare | turnaround time
    "TKT-1035",  # strap_compatibility | active_outdoor | rubber strap swimming
    "TKT-1009",  # order_status | transactional | where is my order
    "TKT-1066",  # product_general | health_conscious | safe for kids | MARKETING SIGNAL
    "TKT-1013",  # knowledge_gap | sustainability | carbon shipping | MARKETING SIGNAL
    "TKT-1067",  # materials_safety | health_conscious | EU certification | MARKETING SIGNAL
]


def load_tickets(demo_mode: bool = True) -> list:
    path = BASE / "data" / "01_customer_tickets.csv"
    if not path.exists():
        print(f"[!] Missing: {path}")
        return []
    with open(path, encoding="utf-8") as f:
        all_tickets = list(csv.DictReader(f))
    if demo_mode:
        tickets = [t for t in all_tickets if t.get("ticket_id") in DEMO_TICKET_IDS]
        # If none matched, just take first 10
        if not tickets:
            tickets = all_tickets[:10]
        print(f"  Demo mode: {len(tickets)} curated tickets")
    else:
        tickets = all_tickets
        print(f"  Full mode: all {len(tickets)} tickets")
    return tickets


def load_external_data() -> list:
    path = BASE / "data" / "09_external_sentiment_data.csv"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_json(data: dict | list, filename: str):
    path = OUTPUT_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Saved → {filename} ({path.stat().st_size:,} bytes)")


def save_text(text: str, filename: str):
    path = OUTPUT_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"  Saved → {filename} ({path.stat().st_size:,} bytes)")


def print_summary(results: list, cluster: dict = None):
    print("\n" + "=" * 72)
    print(f"{'TICKET':<12} {'ACTION':<16} {'PERSONA':<24} {'SIG':<5} {'CONF'}")
    print("-" * 72)
    for r in results:
        if r.get("error"):
            print(f"{r.get('ticket_id','?'):<12} {'ERROR':<16} {'—':<24} {'—':<5} —")
            continue
        action = "✅ DRAFT REPLY" if r.get("action") == "draft_reply" else "⚠️  FLAG GAP"
        signal = "🔥" if r.get("marketing_signal") else "—"
        persona = str(r.get("buyer_persona", "?"))
        conf = str(r.get("confidence", "?"))
        print(f"{r.get('ticket_id','?'):<12} {action:<16} {persona:<24} {signal:<5} {conf}")
    print("=" * 72)

    replies = sum(1 for r in results if r.get("action") == "draft_reply")
    gaps = sum(1 for r in results if r.get("action") == "flag_gap")
    signals = sum(1 for r in results if r.get("marketing_signal"))
    errors = sum(1 for r in results if r.get("error"))
    print(f"\n📊 Results: {replies} replies drafted | {gaps} gaps flagged | {signals} marketing signals | {errors} errors")

    if cluster and cluster.get("top_insight"):
        print(f"\n💡 Top insight: {cluster['top_insight']}")
    print()


def run_pipeline(demo_mode: bool = True):
    print("\n" + "=" * 72)
    print("  🚀  BOLDR SELF-IMPROVING CUSTOMER INTELLIGENCE ENGINE")
    print("       ECSG2026 · Revenue Rocket Track")
    print("=" * 72 + "\n")

    # ── Step 2: Load Knowledge Base ──────────────────────────────────────────
    print("📚 Step 2 — Loading Knowledge Base...")
    kb = KBLoader(BASE / "data")
    kb.build_index()
    kb_context = kb.get_full_context()
    if not kb_context:
        print("  [!] KB is empty — check data/ folder has the Boldr files")
    print()

    # ── Steps 1 & 3: Process tickets ─────────────────────────────────────────
    print("📨 Steps 1 & 3 — Processing tickets...")
    tickets = load_tickets(demo_mode)
    if not tickets:
        print("  [!] No tickets found. Check data/01_customer_tickets.csv exists.")
        return

    results = []
    for i, ticket in enumerate(tickets):
        tid = ticket.get("ticket_id", f"#{i+1}")
        subj = str(ticket.get("subject", ""))[:55]
        print(f"  [{i+1:02d}/{len(tickets)}] {tid}: {subj}")
        result = process_ticket(ticket, kb_context)
        results.append(result)
        if not result.get("error"):
            icon = "✅" if result.get("action") == "draft_reply" else "⚠️ "
            print(f"           {icon} {result.get('action')} | {result.get('buyer_persona')} | signal={'🔥' if result.get('marketing_signal') else '—'}")

    save_json(results, "processed_tickets.json")
    print()

    # ── Step 4: Auto-draft KB entry for first gap ─────────────────────────────
    print("📝 Step 4 — Auto-drafting KB entry for first gap...")
    gaps = [r for r in results if r.get("action") == "flag_gap" and not r.get("error")]
    if gaps:
        sample_resolution = (
            "After checking with our manufacturing partner, our movements have moderate magnetic resistance "
            "but are not rated for MRI environments. We recommend removing the watch before entering any MRI "
            "scan room as a precaution. This applies to all Boldr models."
        )
        draft_kb_entry(gaps[0], sample_resolution, OUTPUT_DIR / "new_kb_entries")
    else:
        print("  No gaps to draft KB entry for.")
    print()

    # ── Step 5: Theme clustering ──────────────────────────────────────────────
    print("📊 Step 5 — Weekly theme clustering...")
    # Use all ticket data for richer clustering even in demo mode
    all_path = BASE / "data" / "01_customer_tickets.csv"
    cluster_input = results  # default to processed results
    if all_path.exists():
        with open(all_path, encoding="utf-8") as f:
            all_raw = list(csv.DictReader(f))
        cluster_input = [
            {
                "ticket_id": t.get("ticket_id"),
                "question_type": t.get("question_type"),
                "buyer_persona": t.get("buyer_persona"),
                "intent_summary": t.get("subject", ""),
                "marketing_signal": t.get("answered_by_kb") == "no" or t.get("requires_escalation") == "yes",
                "action": "flag_gap" if t.get("answered_by_kb") == "no" else "draft_reply"
            }
            for t in all_raw
        ]

    cluster = cluster_themes(cluster_input)
    save_json(cluster, "weekly_theme_cluster.json")
    n_themes = len(cluster.get("themes", []))
    print(f"  {n_themes} themes identified")
    print()

    # ── Step 6: Marketing brief ───────────────────────────────────────────────
    print("✍️  Step 6 — Generating marketing intelligence brief...")
    external = load_external_data()
    brief = generate_brief(cluster, external)
    save_text(brief, "marketing_brief.md")
    print()

    # ── BONUS: External sentiment benchmark ───────────────────────────────────
    if external:
        print("🌐 BONUS — External sentiment benchmarking...")
        bench = benchmark(cluster, external)
        save_json(bench, "external_benchmark.json")
        print()

    # ── Summary ───────────────────────────────────────────────────────────────
    print_summary(results, cluster)

    print("✅ Pipeline complete!\n")
    print("📁 Output files:")
    for f in sorted(OUTPUT_DIR.rglob("*")):
        if f.is_file():
            rel = f.relative_to(OUTPUT_DIR)
            print(f"   {rel}  ({f.stat().st_size:,} bytes)")

    print("\n🖥️  Launch the approval UI:")
    print("   py -m approval_ui.app")
    print("   Then open: http://localhost:5000\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Boldr Intelligence Engine")
    parser.add_argument("--full", action="store_true", help="Process all 70 tickets (default: 10 demo tickets)")
    args = parser.parse_args()
    run_pipeline(demo_mode=not args.full)
