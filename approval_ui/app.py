"""
Boldr CS Intelligence Hub — Premium Redesigned UI
Inspired by Circle Admin Dashboard + Be.run aesthetics
Warm neutrals, bold numbers, teal accents, premium minimal
"""
from flask import Flask, render_template_string, request, redirect, jsonify, send_file
import json, os, sys
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
BASE = Path(__file__).parent.parent
OUTPUT_DIR = BASE / "outputs"


def load_json(filename):
    p = OUTPUT_DIR / filename
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return None

def save_json(data, filename):
    with open(OUTPUT_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_kb_entries():
    folder = OUTPUT_DIR / "new_kb_entries"
    entries = []
    if folder.exists():
        for f in sorted(folder.glob("*.json")):
            try:
                with open(f, encoding="utf-8") as fh:
                    entries.append(json.load(fh))
            except: pass
    return entries

def load_brief():
    p = OUTPUT_DIR / "marketing_brief.md"
    return p.read_text(encoding="utf-8") if p.exists() else None

# Read the HTML template from the separate file
HTML_PATH = Path(__file__).parent / "template.html"

@app.route("/")
def index():
    tickets = load_json("processed_tickets.json") or []
    kb_entries = load_kb_entries()
    brief = load_brief()
    cluster = load_json("weekly_theme_cluster.json")
    html = HTML_PATH.read_text(encoding="utf-8")
    from flask import render_template_string
    return render_template_string(html,
        tickets=tickets, kb_entries=kb_entries,
        brief=brief, cluster=cluster)

@app.route("/approve/<tid>", methods=["POST"])
def approve(tid):
    tickets = load_json("processed_tickets.json") or []
    for t in tickets:
        if t.get("ticket_id") == tid:
            t["status"] = "approved"
            t["approved_at"] = datetime.now().isoformat()
    save_json(tickets, "processed_tickets.json")
    return redirect("/")

@app.route("/reject/<tid>", methods=["POST"])
def reject(tid):
    tickets = load_json("processed_tickets.json") or []
    for t in tickets:
        if t.get("ticket_id") == tid:
            t["status"] = "rejected"
    save_json(tickets, "processed_tickets.json")
    return redirect("/")

@app.route("/resolve_gap/<tid>", methods=["POST"])
def resolve_gap(tid):
    resolution = request.form.get("resolution", "").strip()
    if not resolution:
        return redirect("/")
    tickets = load_json("processed_tickets.json") or []
    gap = next((t for t in tickets if t.get("ticket_id") == tid), None)
    if gap:
        sys.path.insert(0, str(BASE))
        from pipeline.kb_updater import draft_kb_entry
        draft_kb_entry(gap, resolution, OUTPUT_DIR / "new_kb_entries")
        gap["status"] = "gap_resolved"
        gap["resolution"] = resolution
        save_json(tickets, "processed_tickets.json")
    return redirect("/")

@app.route("/api/process_live", methods=["POST"])
def process_live():
    data = request.json
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "No question provided"})
    try:
        sys.path.insert(0, str(BASE))
        from pipeline.kb_loader import KBLoader
        from pipeline.ticket_processor import process_ticket
        kb = KBLoader(BASE / "data")
        kb.build_index()
        kb_context = kb.get_full_context()
        fake_ticket = {"ticket_id": "LIVE-001", "subject": question[:80], "message_body": question}
        result = process_ticket(fake_ticket, kb_context)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/download_brief")
def download_brief():
    p = OUTPUT_DIR / "marketing_brief.md"
    if p.exists():
        return send_file(p, as_attachment=True)
    return "No brief found", 404

@app.route("/api/stats")
def api_stats():
    tickets = load_json("processed_tickets.json") or []
    return jsonify({
        "total": len(tickets),
        "approved": sum(1 for t in tickets if t.get("status") == "approved"),
        "gaps": sum(1 for t in tickets if t.get("action") == "flag_gap"),
        "signals": sum(1 for t in tickets if t.get("marketing_signal"))
    })

if __name__ == "__main__":
    print("Boldr CS Hub running at http://localhost:5000")
    app.run(debug=True, port=5000)
