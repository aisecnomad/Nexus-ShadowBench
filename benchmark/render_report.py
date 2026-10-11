#!/usr/bin/env python3
"""Write the ShadowBench report as one HTML file and a PDF printed from it."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BOARD = json.loads((ROOT / "results" / "scoreboard.json").read_text(encoding="utf-8"))
CASES = json.loads((ROOT / "results" / "cases.json").read_text(encoding="utf-8"))
OUT_HTML = Path("/workspace/public/shadowbench-report.html")
OUT_PDF = Path("/workspace/public/shadowbench-report.pdf")

NAMES = {
    "shadowscan": "ShadowScan",
    "vet": "SafeDep vet",
    "numbat": "Perplexity Numbat",
    "snyk-agent-scan": "Snyk Agent Scan",
    "ai-bom": "Trusera ai-bom",
    "nuguard": "NuGuard",
    "agentdiscover": "AgentDiscover",
    "agentic-radar": "Agentic Radar",
    "aiostack": "Aurva AIOstack",
    "curatedmcp": "CuratedMCP",
    "reference-lexicon": "Lexicon reference",
}

SURFACES = BOARD["benchmark"]["surfaces"]


def esc(value) -> str:
    return html.escape("" if value is None else str(value))


def pct(value) -> str:
    if value is None:
        return "—"
    return f"{int(value * 1000 + 0.5) / 10:.1f}%"


def num(value) -> str:
    if value is None:
        return "—"
    return f"{value:.2f}"


def tool_name(tool: dict) -> str:
    return NAMES.get(tool["id"], tool["id"])


def fact_of(tool: dict) -> dict:
    return ((tool.get("metrics") or {}).get("quality") or {}).get("fact") or {}


def case_of(tool: dict) -> dict:
    return ((tool.get("metrics") or {}).get("quality") or {}).get("case") or {}


def rows() -> list[dict]:
    tools = BOARD["tools"]
    products = [t for t in tools if t["role"] == "tool" and t.get("metrics")]
    products.sort(key=lambda t: fact_of(t).get("f1") or -1, reverse=True)
    missing = [t for t in tools if t["role"] == "tool" and not t.get("metrics")]
    reference = [t for t in tools if t["role"] == "reference"]
    return products + missing + reference


def score_table() -> str:
    body = []
    for index, tool in enumerate(rows(), start=1):
        fact = fact_of(tool)
        quality = (tool.get("metrics") or {}).get("quality") or {}
        status = {"scored": "Scored", "not_run": "Not run"}.get(tool["status"], tool["status"])
        if tool["role"] == "reference":
            status = "Reference"
        body.append(
            "<tr>"
            f"<td class='num'>{index}</td>"
            f"<td>{esc(tool_name(tool))}</td>"
            f"<td>{esc(status)}</td>"
            f"<td class='num'>{pct(fact.get('precision'))}</td>"
            f"<td class='num'>{pct(fact.get('recall'))}</td>"
            f"<td class='num emph'>{pct(fact.get('f1'))}</td>"
            f"<td class='num'>{pct((quality.get('case') or {}).get('specificity'))}</td>"
            f"<td class='num'>{pct((tool.get('metrics') or {}).get('estate_recall'))}</td>"
            "</tr>"
        )
    return (
        "<table class='grid'><thead><tr>"
        "<th class='num'>#</th><th>Tool</th><th>Status</th><th class='num'>Precision</th>"
        "<th class='num'>Recall</th><th class='num'>F1</th><th class='num'>Specificity</th>"
        "<th class='num'>Estate recall</th>"
        "</tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table>"
    )


SHORT = {
    "code": "Code",
    "identity": "Ident.",
    "gateway": "Gate",
    "lowcode": "Low-c.",
    "saas": "SaaS",
    "cloud": "Cloud",
    "endpoint": "Endpt",
    "network": "Net",
    "runtime": "Run",
}


def heat_table() -> str:
    heads = "".join(f"<th class='num'>{esc(SHORT[s])}</th>" for s in SURFACES)
    body = []
    for tool in rows():
        if not tool.get("metrics"):
            continue
        by = tool["metrics"]["quality"]["by_surface"]
        cells = []
        for surface in SURFACES:
            cell = by.get(surface)
            cells.append(f"<td class='num'>{pct(cell['recall']) if cell else '·'}</td>")
        body.append(f"<tr><th>{esc(tool_name(tool))}</th>{''.join(cells)}</tr>")
    return (
        "<table class='grid heat'><thead><tr><th>Tool</th>"
        + heads
        + "</tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table>"
    )


def tool_sections() -> str:
    blocks = []
    for index, tool in enumerate(rows(), start=1):
        quality = (tool.get("metrics") or {}).get("quality")
        surfaces = ", ".join(tool.get("applicable_surfaces") or []) or "none"
        detail = esc(tool.get("status_detail") or "")
        version = esc(tool.get("version") or "version not recorded")
        stats = ""
        if quality:
            fact = quality["fact"]
            case = quality["case"]
            ci = quality.get("fact_f1_ci95")
            ci_text = f"{pct(ci[0])} – {pct(ci[1])}" if ci else "—"
            lat = tool.get("latency_ms") or {}
            p50 = f"{lat['p50']} ms" if lat.get("p50") is not None else "—"
            p95 = f"{lat['p95']} ms" if lat.get("p95") is not None else "—"
            pairs = [
                ("Fact TP / FP / FN", f"{fact['tp']} / {fact['fp']} / {fact['fn']}"),
                ("Case TP / FP / TN / FN", f"{case['tp']} / {case['fp']} / {case['tn']} / {case['fn']}"),
                ("Matthews correlation", num(case.get("mcc"))),
                ("Balanced accuracy", pct(case.get("balanced_accuracy"))),
                ("Fact F1, 95% interval", ci_text),
                ("Errors excluded", str(quality["errors"])),
                ("Latency, median", p50),
                ("Latency, 95th", p95),
            ]
            stats = "<table class='spec'>" + "".join(
                f"<tr><th>{esc(label)}</th><td>{esc(value)}</td></tr>" for label, value in pairs
            ) + "</table>"
        blocks.append(
            "<section class='tool'>"
            f"<h3>{index}. {esc(tool_name(tool))}</h3>"
            f"<p class='detail'>{detail}</p>"
            f"<p class='meta'>{version} · {esc(surfaces)}</p>"
            f"{stats}</section>"
        )
    return "".join(blocks)


def case_table() -> str:
    body = []
    for case in CASES:
        facts = ", ".join(f"{f['category']}:{f['value']}" for f in case["facts"]) or "—"
        forbidden = ", ".join(f"{f['category']}:{f['value']}" for f in case["forbidden"]) or "—"
        body.append(
            "<tr>"
            f"<td class='mono'>{esc(case['id'])}<span class='sub'>{esc(case['title'])}</span></td>"
            f"<td>{esc(case['polarity'].replace('_', ' '))}</td>"
            f"<td>{esc(facts)}</td>"
            f"<td>{esc(forbidden)}</td>"
            "</tr>"
        )
    return (
        "<table class='grid cases'><thead><tr>"
        "<th>Case</th><th>Polarity</th><th>Planted facts</th><th>Must not emit</th>"
        "</tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table>"
    )


def formats() -> str:
    items = []
    for surface, text in BOARD["benchmark"]["formats"].items():
        items.append(f"<tr><th>{esc(surface)}</th><td>{esc(text)}</td></tr>")
    return "<table class='spec formats'>" + "".join(items) + "</table>"


def document() -> str:
    bench = BOARD["benchmark"]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(bench['name'])} — discovery report</title>
<style>
  :root {{
    --ink: #1c1915;
    --muted: #5e584e;
    --line: #d9d0c4;
    --rule: #1c1915;
    --accent: #9a3412;
    --paper: #fffdf8;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    color: var(--ink);
    background: #e6e0d6;
    font-family: "Liberation Serif", "FreeSerif", "DejaVu Serif", serif;
    font-size: 11pt;
    line-height: 1.45;
  }}
  .cover, main {{
    background: var(--paper);
    width: 210mm;
    margin: 12px auto;
    padding: 18mm 16mm 16mm;
  }}
  .cover {{
    min-height: 297mm;
    display: flex;
    flex-direction: column;
    padding-top: 28mm;
  }}
  .doc-kicker {{
    margin: 0;
    font-family: "Liberation Sans", sans-serif;
    font-size: 9pt;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--accent);
  }}
  h1 {{
    margin: 10px 0 0;
    font-family: "Liberation Sans", sans-serif;
    font-weight: 700;
    font-size: 42pt;
    line-height: 0.95;
    letter-spacing: -0.03em;
  }}
  .subtitle {{
    margin: 14px 0 0;
    max-width: 34em;
    font-family: "Liberation Sans", sans-serif;
    font-size: 13pt;
    line-height: 1.35;
    color: var(--muted);
  }}
  .cover hr {{
    width: 42mm;
    margin: 22px 0;
    border: 0;
    border-top: 2.5pt solid var(--accent);
  }}
  .lede {{ margin: 0; max-width: 38em; }}
  .id-block {{
    margin-top: 28px;
    width: 100%;
    border-collapse: collapse;
    font-family: "Liberation Sans", sans-serif;
    font-size: 9.5pt;
  }}
  .id-block th {{
    width: 34mm;
    padding: 5px 10px 5px 0;
    text-align: left;
    font-weight: 600;
    color: var(--muted);
    border-bottom: 0.4pt solid var(--line);
    vertical-align: top;
  }}
  .id-block td {{
    padding: 5px 0;
    border-bottom: 0.4pt solid var(--line);
    font-family: "Liberation Mono", monospace;
    font-size: 8.5pt;
    word-break: break-all;
  }}
  .cover-foot {{
    margin-top: auto;
    padding-top: 18px;
    font-family: "Liberation Sans", sans-serif;
    font-size: 8.5pt;
    color: var(--muted);
  }}
  h2 {{
    margin: 0 0 8px;
    padding-bottom: 4px;
    border-bottom: 1pt solid var(--rule);
    font-family: "Liberation Sans", sans-serif;
    font-size: 14pt;
    font-weight: 650;
    letter-spacing: -0.01em;
    break-after: avoid;
    page-break-after: avoid;
  }}
  h2 .sec {{
    color: var(--accent);
    font-variant-numeric: tabular-nums;
    margin-right: 0.45em;
  }}
  h3 {{
    margin: 0 0 2px;
    font-family: "Liberation Sans", sans-serif;
    font-size: 11.5pt;
    break-after: avoid;
  }}
  section {{ margin-top: 16pt; }}
  p {{ margin: 0 0 8px; }}
  .note, .detail, .meta {{ color: var(--muted); }}
  .meta {{
    margin: 0 0 6px;
    font-family: "Liberation Mono", monospace;
    font-size: 8pt;
  }}
  .caption {{
    margin: 12px 0 4px;
    font-family: "Liberation Sans", sans-serif;
    font-size: 8.5pt;
    font-weight: 650;
  }}
  .caption span {{ font-weight: 400; color: var(--muted); }}
  table.grid, table.spec {{
    width: 100%;
    border-collapse: collapse;
    font-family: "Liberation Sans", sans-serif;
    font-size: 8.5pt;
    line-height: 1.3;
  }}
  table.grid th, table.grid td {{
    padding: 4px 5px;
    text-align: left;
    vertical-align: top;
    border-bottom: 0.4pt solid var(--line);
  }}
  table.grid thead th {{
    border-bottom: 1pt solid var(--rule);
    font-size: 7.5pt;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-weight: 650;
  }}
  td.num, th.num {{
    text-align: right;
    font-variant-numeric: tabular-nums;
    font-family: "Liberation Sans", sans-serif;
    white-space: nowrap;
  }}
  td.emph {{ font-weight: 700; }}
  table.heat {{ font-size: 7.5pt; }}
  table.heat th:first-child {{ text-align: left; font-weight: 650; white-space: nowrap; }}
  table.spec th {{
    width: 46mm;
    padding: 3px 8px 3px 0;
    text-align: left;
    font-weight: 600;
    color: var(--muted);
    border-bottom: 0.4pt solid var(--line);
    vertical-align: top;
  }}
  table.spec td {{
    padding: 3px 0;
    border-bottom: 0.4pt solid var(--line);
    vertical-align: top;
  }}
  table.formats th {{ width: 24mm; text-transform: none; letter-spacing: 0; font-size: 9pt; }}
  .tool {{ break-inside: avoid; page-break-inside: avoid; margin-top: 12pt; }}
  .cases {{ font-size: 7.5pt; }}
  .cases td.mono {{
    font-family: "Liberation Mono", monospace;
    font-size: 7.5pt;
    white-space: nowrap;
    width: 28mm;
  }}
  .sub {{
    display: block;
    margin-top: 1px;
    font-family: "Liberation Sans", sans-serif;
    font-size: 7pt;
    color: var(--muted);
    white-space: normal;
    max-width: 38mm;
  }}
  .cases td:nth-child(2) {{ width: 22mm; }}
  .cases td:nth-child(4) {{ width: 38mm; }}
  @page {{
    size: A4;
    margin: 16mm 14mm 16mm;
    @top-left {{
      content: "ShadowBench";
      font-family: "Liberation Sans", sans-serif;
      font-size: 8pt;
      color: #5e584e;
    }}
    @top-right {{
      content: "Discovery report";
      font-family: "Liberation Sans", sans-serif;
      font-size: 8pt;
      color: #5e584e;
    }}
    @bottom-left {{
      content: "shadowbench-450-v1";
      font-family: "Liberation Mono", monospace;
      font-size: 7.5pt;
      color: #5e584e;
    }}
    @bottom-right {{
      content: counter(page);
      font-family: "Liberation Sans", sans-serif;
      font-size: 8pt;
      color: #5e584e;
    }}
  }}
  @page :first {{
    margin: 0;
    @top-left {{ content: none; }}
    @top-right {{ content: none; }}
    @bottom-left {{ content: none; }}
    @bottom-right {{ content: none; }}
  }}
  @media print {{
    body {{ background: white; }}
    .cover, main {{
      width: auto;
      margin: 0;
      padding: 0;
      box-shadow: none;
    }}
    .cover {{
      height: 297mm;
      padding: 28mm 18mm 18mm;
      break-after: page;
      page-break-after: always;
    }}
    thead {{ display: table-header-group; }}
    tr, h2, h3 {{ break-inside: avoid; }}
  }}
</style>
</head>
<body>
<section class="cover">
  <p class="doc-kicker">Report · {esc(bench['version'])} · 11 October 2026</p>
  <h1>{esc(bench['name'])}</h1>
  <p class="subtitle">Open-source discovery of shadow AI agents, measured on 450 planted cases across nine surfaces.</p>
  <hr>
  <p class="lede">Labels are planted evidence, not the output of any scanner. In-scope F1 counts only the surfaces a tool can read. Estate recall treats every other positive as a miss. The lexicon row is a string-match ceiling, not a product.</p>
  <table class="id-block">
    <tr><th>Cases</th><td>{bench['cases']}</td></tr>
    <tr><th>Seed</th><td>{esc(bench['seed'])}</td></tr>
    <tr><th>Provenance</th><td>{esc(bench['provenance'])}</td></tr>
    <tr><th>Corpus</th><td>{esc(bench['corpus_sha256'])}</td></tr>
    <tr><th>Labels</th><td>{esc(bench['label_rule'])}</td></tr>
  </table>
  <p class="cover-foot">Same scored run as the scoreboard. Tools were not scanned again for this document.</p>
</section>
<main>
  <section>
    <h2><span class="sec">1</span>Results</h2>
    <p>Eight tools ran. Two were probed and left blank because they cannot scan offline: a missing token is not a score of zero. Tools are ordered by in-scope fact F1. Precision, recall and F1 are fact-level. Specificity is case-level.</p>
    <p class="caption">Table 1. <span>In-scope quality and estate recall.</span></p>
    {score_table()}
  </section>

  <section>
    <h2><span class="sec">2</span>Coverage</h2>
    <p>A dot means the tool was not asked to read that surface. Unread negatives are not counted as true negatives.</p>
    <p class="caption">Table 2. <span>Fact recall by surface. Ident. identity, Gate gateway, Low-c. low-code, Endpt endpoint, Net network, Run runtime.</span></p>
    {heat_table()}
  </section>

  <section>
    <h2><span class="sec">3</span>Tool notes</h2>
    {tool_sections()}
  </section>

  <section>
    <h2><span class="sec">4</span>Method</h2>
    <p>Each surface holds 25 positives, 15 negatives and 10 near-misses. A positive fact is true only when its quote is in the cited file. A negative case must produce no mapped finding. A near-miss names the lookalike that must not be emitted: Minecraft Bedrock is not AWS Bedrock, a CSS cursor is not the Cursor IDE, Claude Bernard is not Claude.</p>
    <p>These are not private tenant dumps. One documented format is exercised per surface. That is the sampling frame, not the whole surface.</p>
    <p class="caption">Table 3. <span>Sampling frame.</span></p>
    {formats()}
    <p>Fact-level precision, recall and F1 are primary. A positive case is detected if any planted fact comes back. Any mapped finding on a negative or near-miss is a false positive. Specificity, false-positive rate, balanced accuracy and Matthews correlation use that case table. Crashes and timeouts leave the denominator and are counted as errors. A 1,000-draw bootstrap over cases gives a 95% interval on fact F1.</p>
    <p>Estate recall counts positives on unread surfaces as misses. The lexicon reference applies the published alias list to the artifact text, including paths. It does not read the answer key.</p>
  </section>

  <section>
    <h2><span class="sec">A</span>Case index</h2>
    <p class="note">{len(CASES)} cases. The quote that justifies each planted fact is in the case file. This index records the fact and the names a correct scanner must not emit.</p>
    <p class="caption">Table 4. <span>Case index.</span></p>
    {case_table()}
  </section>
</main>
</body>
</html>
"""


def write_pdf(html_path: Path, pdf_path: Path) -> None:
    import subprocess

    script = r"""
import { chromium } from "playwright";
const htmlPath = process.argv[1];
const pdfPath = process.argv[2];
const browser = await chromium.launch();
const page = await browser.newPage();
await page.goto(htmlPath, { waitUntil: "load" });
await page.pdf({
  path: pdfPath,
  preferCSSPageSize: true,
  printBackground: true,
  margin: { top: "0", right: "0", bottom: "0", left: "0" },
});
await browser.close();
"""
    subprocess.run(
        ["node", "--input-type=module", "-e", script, html_path.as_uri(), str(pdf_path)],
        cwd="/workspace",
        check=True,
    )


def main() -> None:
    OUT_HTML.write_text(document(), encoding="utf-8")
    write_pdf(OUT_HTML, OUT_PDF)
    print(OUT_HTML, OUT_HTML.stat().st_size)
    print(OUT_PDF, OUT_PDF.stat().st_size)


if __name__ == "__main__":
    main()
