"""
Boldr CS Intelligence Hub — Human Approval UI
Run: py -m approval_ui.app
Then open: http://localhost:5000
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
            with open(f, encoding="utf-8") as fh:
                try:
                    entries.append(json.load(fh))
                except:
                    pass
    return entries


def load_brief():
    p = OUTPUT_DIR / "marketing_brief.md"
    return p.read_text(encoding="utf-8") if p.exists() else None


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Boldr CS Intelligence Hub</title>
<style>
:root{--bg:#0f0f0f;--s1:#1a1a1a;--s2:#242424;--bd:#2e2e2e;--tx:#f0f0f0;--mu:#888;
--gr:#1d9e75;--gbg:#0d2e22;--gtx:#4ade9e;--or:#ef9f27;--obg:#2e1f08;--otx:#fbbf24;
--rd:#ef4444;--rbg:#2e1010;--rtx:#f87171;--bl:#3b82f6;--bbg:#0f1f3d;--btx:#60a5fa;--pu:#8b5cf6}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--tx);font-family:-apple-system,BlinkMacSystemFont,'Inter',sans-serif;font-size:14px}
.sidebar{position:fixed;top:0;left:0;width:210px;height:100vh;background:var(--s1);border-right:1px solid var(--bd);padding:20px 0;z-index:100}
.main{margin-left:210px;padding:28px 32px;min-height:100vh}
.brand{padding:0 20px 16px;border-bottom:1px solid var(--bd);margin-bottom:12px}
.brand-name{font-size:15px;font-weight:600}.brand-sub{font-size:11px;color:var(--mu);margin-top:2px}
.nav-s{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;color:var(--mu);padding:14px 20px 6px}
.nav-a{display:flex;align-items:center;gap:10px;padding:9px 20px;color:var(--mu);text-decoration:none;font-size:13px;cursor:pointer;border-left:2px solid transparent;border:none;background:none;width:100%;text-align:left}
.nav-a:hover,.nav-a.active{color:var(--tx);background:var(--s2);border-left:2px solid var(--gr)}
.nbadge{margin-left:auto;background:var(--or);color:#000;font-size:10px;font-weight:700;padding:1px 6px;border-radius:10px}
.ph{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}
.pt{font-size:20px;font-weight:600}.ps{font-size:12px;color:var(--mu);margin-top:3px}
.live{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--gtx);background:var(--gbg);padding:5px 12px;border-radius:20px;border:1px solid var(--gr)}
.ld{width:6px;height:6px;background:var(--gr);border-radius:50%;animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px}
.sc{background:var(--s1);border:1px solid var(--bd);border-radius:10px;padding:16px}
.sn{font-size:26px;font-weight:600}.sl{font-size:11px;color:var(--mu);margin-top:4px}
.tabs{display:flex;gap:2px;background:var(--s1);border:1px solid var(--bd);border-radius:8px;padding:4px;margin-bottom:16px;width:fit-content}
.tb{padding:6px 14px;border-radius:6px;font-size:12px;font-weight:500;cursor:pointer;border:none;background:none;color:var(--mu)}
.tb.active{background:var(--s2);color:var(--tx)}
.panel{display:none}.panel.active{display:block}
.card{background:var(--s1);border:1px solid var(--bd);border-radius:10px;margin-bottom:10px;overflow:hidden}
.ch{display:flex;align-items:center;gap:10px;padding:12px 16px;border-bottom:1px solid var(--bd)}
.cid{font-family:monospace;font-size:11px;color:var(--mu);background:var(--s2);padding:2px 8px;border-radius:4px}
.csub{font-weight:500;flex:1}
.cb{padding:14px 16px}
.tag{display:inline-block;font-size:11px;font-weight:500;padding:2px 8px;border-radius:4px;margin-right:5px;margin-bottom:4px}
.tg{background:var(--gbg);color:var(--gtx);border:1px solid var(--gr)}
.to{background:var(--obg);color:var(--otx);border:1px solid var(--or)}
.tb2{background:var(--bbg);color:var(--btx);border:1px solid var(--bl)}
.tr{background:var(--rbg);color:var(--rtx);border:1px solid var(--rd)}
.tm{background:var(--s2);color:var(--mu);border:1px solid var(--bd)}
.tp{background:#1e1040;color:#c4b5fd;border:1px solid var(--pu)}
.draft{background:var(--s2);border:1px solid var(--bd);border-radius:8px;padding:12px;font-size:13px;line-height:1.7;white-space:pre-wrap;margin-top:6px}
.gap-box{background:var(--obg);border:1px solid var(--or);border-radius:8px;padding:10px 12px;font-size:13px;color:var(--otx)}
.mkt-box{background:var(--gbg);border:1px solid var(--gr);border-radius:8px;padding:10px 12px;font-size:12px;color:var(--gtx)}
.sl2{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.07em;color:var(--mu);margin-bottom:5px;margin-top:10px}
.ar{display:flex;gap:8px;padding:12px 16px;background:var(--s2);border-top:1px solid var(--bd)}
.btn{padding:7px 16px;border-radius:7px;font-size:13px;font-weight:500;cursor:pointer;border:none}
.ba{background:var(--gr);color:#fff}.ba:hover{background:#16a066}
.br{background:var(--rbg);color:var(--rtx);border:1px solid var(--rd)}.br:hover{background:#3d1515}
.be{background:var(--s1);color:var(--tx);border:1px solid var(--bd)}
.ok{color:var(--gtx);font-size:12px;font-weight:500}.no{color:var(--rtx);font-size:12px;font-weight:500}
textarea{width:100%;background:var(--s2);border:1px solid var(--bd);border-radius:8px;padding:10px;color:var(--tx);font-size:13px;resize:vertical;min-height:80px;font-family:inherit;margin-top:6px}
.brief-wrap{background:var(--s1);border:1px solid var(--bd);border-radius:10px;padding:22px}
.brief-content{font-size:13px;line-height:1.8;white-space:pre-wrap}
.brief-content h1{font-size:18px;font-weight:600;margin:0 0 14px}
.brief-content h2{font-size:14px;font-weight:600;margin:18px 0 8px;color:var(--otx);border-bottom:1px solid var(--bd);padding-bottom:4px}
.brief-content h3{font-size:13px;font-weight:600;margin:12px 0 5px;color:var(--btx)}
.tg2{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.tc{background:var(--s1);border:1px solid var(--bd);border-radius:10px;padding:14px}
.tn{font-size:14px;font-weight:500;margin-bottom:4px}
.tnum{font-size:24px;font-weight:600;color:var(--otx)}
.empty{text-align:center;padding:60px 20px;color:var(--mu)}
.empty-icon{font-size:40px;margin-bottom:12px}
form{display:inline}
p{font-size:13px;color:var(--mu);line-height:1.6}
</style>
</head>
<body>
<div class="sidebar">
  <div class="brand">
    <div class="brand-name">⌚ Boldr CS Hub</div>
    <div class="brand-sub">ECSG2026 · AI Workflow</div>
  </div>
  <div class="nav-s">Approval Queue</div>
  <button class="nav-a active" onclick="show('replies',this)">📨 Reply Drafts
    {% set pend=tickets|selectattr('action','equalto','draft_reply')|selectattr('status','equalto','pending_human_approval')|list %}
    {% if pend %}<span class="nbadge">{{pend|length}}</span>{% endif %}
  </button>
  <button class="nav-a" onclick="show('gaps',this)">⚠️ Knowledge Gaps
    {% set g=tickets|selectattr('action','equalto','flag_gap')|list %}
    {% if g %}<span class="nbadge">{{g|length}}</span>{% endif %}
  </button>
  <button class="nav-a" onclick="show('kb',this)">📚 KB Drafts
    {% if kb_entries %}<span class="nbadge">{{kb_entries|length}}</span>{% endif %}
  </button>
  <div class="nav-s">Intelligence</div>
  <button class="nav-a" onclick="show('themes',this)">📊 Theme Clusters</button>
  <button class="nav-a" onclick="show('brief',this)">✍️ Marketing Brief</button>
</div>

<div class="main">
  <div class="ph">
    <div><div class="pt">Customer Intelligence Hub</div><div class="ps">Nothing sends without your approval</div></div>
    <div class="live"><span class="ld"></span> AI Engine Active</div>
  </div>
  <div class="stats">
    <div class="sc" style="border-top:2px solid var(--gr)">
      <div class="sn" style="color:var(--gtx)">{{tickets|selectattr('action','equalto','draft_reply')|list|length}}</div>
      <div class="sl">Reply drafts ready</div></div>
    <div class="sc" style="border-top:2px solid var(--or)">
      <div class="sn" style="color:var(--otx)">{{tickets|selectattr('action','equalto','flag_gap')|list|length}}</div>
      <div class="sl">Gaps flagged</div></div>
    <div class="sc" style="border-top:2px solid var(--bl)">
      <div class="sn" style="color:var(--btx)">{{tickets|selectattr('marketing_signal','equalto',true)|list|length}}</div>
      <div class="sl">Marketing signals</div></div>
    <div class="sc" style="border-top:2px solid var(--rd)">
      <div class="sn" style="color:var(--rtx)">{{kb_entries|length}}</div>
      <div class="sl">KB entries pending</div></div>
  </div>
  <div class="tabs">
    <button class="tb active" onclick="show('replies',this)">📨 Replies</button>
    <button class="tb" onclick="show('gaps',this)">⚠️ Gaps</button>
    <button class="tb" onclick="show('kb',this)">📚 KB Drafts</button>
    <button class="tb" onclick="show('themes',this)">📊 Themes</button>
    <button class="tb" onclick="show('brief',this)">✍️ Brief</button>
  </div>

  <div id="p-replies" class="panel active">
    {% set rt=tickets|selectattr('action','equalto','draft_reply')|list %}
    {% if rt %}{% for t in rt %}
    <div class="card">
      <div class="ch">
        <span class="cid">{{t.ticket_id}}</span>
        <span class="csub">{{t.intent_summary or 'No summary'}}</span>
        <span class="tag {{'tg' if t.status=='approved' else 'tr' if t.status=='rejected' else 'to'}}">
          {{(t.status or 'pending')|replace('_',' ')|title}}</span>
        {% if t.marketing_signal %}<span class="tag tg">🔥 Signal</span>{% endif %}
      </div>
      <div class="cb">
        <div style="margin-bottom:10px">
          <span class="tag tb2">{{(t.question_type or '')|replace('_',' ')|title}}</span>
          <span class="tag tp">{{(t.buyer_persona or '')|replace('_',' ')|title}}</span>
          <span class="tag tm">{{t.confidence or 'high'}} confidence</span>
        </div>
        {% if t.marketing_note %}<div class="sl2">💡 Marketing Signal</div><div class="mkt-box">{{t.marketing_note}}</div>{% endif %}
        <div class="sl2">AI Draft Reply</div>
        <div class="draft">{{t.draft_reply or 'No draft generated.'}}</div>
      </div>
      <div class="ar">
        {% if t.status=='approved' %}<span class="ok">✅ Approved — ready to send</span>
        {% elif t.status=='rejected' %}<span class="no">❌ Rejected</span>
        {% else %}
        <form method="POST" action="/approve/{{t.ticket_id}}"><button class="btn ba">✅ Approve</button></form>
        <form method="POST" action="/reject/{{t.ticket_id}}"><button class="btn br">❌ Reject</button></form>
        {% endif %}
      </div>
    </div>
    {% endfor %}{% else %}
    <div class="empty"><div class="empty-icon">📭</div><div>No reply drafts yet. Run py main.py first.</div></div>
    {% endif %}
  </div>

  <div id="p-gaps" class="panel">
    {% set gt=tickets|selectattr('action','equalto','flag_gap')|list %}
    {% if gt %}{% for t in gt %}
    <div class="card">
      <div class="ch">
        <span class="cid">{{t.ticket_id}}</span>
        <span class="csub">{{t.intent_summary or 'Knowledge gap'}}</span>
        <span class="tag to">⚠️ Gap</span>
        {% if t.marketing_signal %}<span class="tag tg">🔥 Signal</span>{% endif %}
      </div>
      <div class="cb">
        <div style="margin-bottom:10px">
          <span class="tag tp">{{(t.buyer_persona or '')|replace('_',' ')|title}}</span>
        </div>
        <div class="sl2">What's missing from KB</div>
        <div class="gap-box">{{t.gap_details or 'No details.'}}</div>
        {% if t.marketing_note %}<div class="sl2">💡 Opportunity</div><div class="mkt-box">{{t.marketing_note}}</div>{% endif %}
        <div class="sl2">Resolve this gap — AI will auto-draft the KB entry</div>
        <form method="POST" action="/resolve_gap/{{t.ticket_id}}" style="display:block">
          <textarea name="resolution" placeholder="Type the answer here..."></textarea><br>
          <button type="submit" class="btn ba" style="margin-top:8px">→ Resolve & Auto-Draft KB Entry</button>
        </form>
      </div>
    </div>
    {% endfor %}{% else %}
    <div class="empty"><div class="empty-icon">✅</div><div>No gaps flagged.</div></div>
    {% endif %}
  </div>

  <div id="p-kb" class="panel">
    {% if kb_entries %}{% for e in kb_entries %}
    <div class="card" style="border-color:var(--gr)">
      <div class="ch">
        <span class="tag tg">New KB Entry</span>
        <span class="tag tb2">{{(e.category or 'general')|replace('_',' ')|title}}</span>
        <span style="font-family:monospace;font-size:11px;color:var(--mu)">{{e.faq_id or 'auto-id'}}</span>
        {% if e.marketing_flag %}<span class="tag to">🔥 Marketing</span>{% endif %}
      </div>
      <div class="cb">
        <div class="sl2">Proposed Question</div>
        <div style="font-size:15px;font-weight:500;margin-bottom:8px">{{e.question or 'No question'}}</div>
        <div class="sl2">Proposed Answer</div>
        <div class="draft">{{e.answer or 'No answer.'}}</div>
        {% if e.marketing_action %}<div class="mkt-box" style="margin-top:8px">💡 {{e.marketing_action}}</div>{% endif %}
      </div>
      <div class="ar">
        <span class="tag tm">Created from {{e.created_from_ticket}}</span>
        <span class="tag {{'tg' if e.status=='approved' else 'tr' if e.status=='rejected' else 'to'}}">{{e.status or 'pending'}}</span>
      </div>
    </div>
    {% endfor %}{% else %}
    <div class="empty"><div class="empty-icon">📚</div><div>No KB drafts yet. Resolve a gap to generate one.</div></div>
    {% endif %}
  </div>

  <div id="p-themes" class="panel">
    {% if cluster %}
    <div class="card" style="padding:14px 16px;margin-bottom:14px">
      <div style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.07em;color:var(--mu);margin-bottom:6px">Top Insight This Week</div>
      <div style="font-size:14px;line-height:1.6">{{cluster.top_insight or 'Run pipeline to generate.'}}</div>
    </div>
    <div class="tg2">
    {% for t in cluster.themes or [] %}
    <div class="tc">
      <div class="tn">{{t.theme_name}}</div>
      <div style="display:flex;align-items:baseline;gap:8px;margin:4px 0">
        <div class="tnum">{{t.ticket_count}}</div><div style="font-size:11px;color:var(--mu)">tickets</div>
        <span class="tag {{'tg' if t.marketing_signal_strength=='high' else 'to' if t.marketing_signal_strength=='medium' else 'tm'}}" style="margin-left:auto">{{(t.marketing_signal_strength or 'low')|upper}} signal</span>
      </div>
      {% for p in t.primary_personas or [] %}<span class="tag tp">{{p|replace('_',' ')}}</span>{% endfor %}
      {% if t.marketing_opportunity %}<div class="mkt-box" style="margin-top:8px;font-size:11px">💡 {{t.marketing_opportunity[:110]}}</div>{% endif %}
    </div>
    {% endfor %}
    </div>
    {% else %}
    <div class="empty"><div class="empty-icon">📊</div><div>No cluster data. Run the pipeline first.</div></div>
    {% endif %}
  </div>

  <div id="p-brief" class="panel">
    {% if brief %}
    <div class="brief-wrap">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
        <div style="font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.07em;color:var(--mu)">Monthly Intelligence Brief</div>
        <a href="/download_brief" class="btn be" style="text-decoration:none;font-size:12px">⬇ Download .md</a>
      </div>
      <div class="brief-content">{{brief}}</div>
    </div>
    {% else %}
    <div class="empty"><div class="empty-icon">✍️</div><div>No brief yet. Run the pipeline first.</div></div>
    {% endif %}
  </div>
</div>

<script>
function show(name, btn) {
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-a,.tb').forEach(b=>b.classList.remove('active'));
  document.getElementById('p-'+name).classList.add('active');
  if(btn) btn.classList.add('active');
}
</script>
</body>
</html>"""


@app.route("/")
def index():
    tickets = load_json("processed_tickets.json") or []
    kb_entries = load_kb_entries()
    brief = load_brief()
    cluster = load_json("weekly_theme_cluster.json")
    return render_template_string(HTML, tickets=tickets, kb_entries=kb_entries, brief=brief, cluster=cluster)


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
            t["rejected_at"] = datetime.now().isoformat()
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
        "pending": sum(1 for t in tickets if t.get("status") == "pending_human_approval"),
        "approved": sum(1 for t in tickets if t.get("status") == "approved"),
        "gaps": sum(1 for t in tickets if t.get("action") == "flag_gap"),
        "signals": sum(1 for t in tickets if t.get("marketing_signal"))
    })


if __name__ == "__main__":
    print("🚀 Boldr CS Hub → http://localhost:5000")
    app.run(debug=True, port=5000)
