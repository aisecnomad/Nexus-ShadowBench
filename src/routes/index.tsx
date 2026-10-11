import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ScanSearch } from "lucide-react";
import { previewPathPrefix } from "@/lib/preview-path-prefix";
import scoreboard from "@/data/scoreboard.json";
import cases from "@/data/cases.json";

type Fact = {
  category: string;
  value: string;
  path?: string;
  quote?: string;
};

type FactMetrics = {
  tp: number;
  fp: number;
  fn: number;
  precision: number | null;
  recall: number | null;
  f1: number | null;
};

type SurfaceMetrics = FactMetrics & {
  case_tp: number;
  case_fp: number;
  case_tn: number;
  case_fn: number;
};

type ToolRow = {
  id: string;
  role: string;
  status: string;
  status_detail: string;
  version?: string | null;
  applicable_surfaces: string[];
  metrics?: {
    quality: {
      cases_scored: number;
      errors: number;
      fact: FactMetrics;
      fact_f1_ci95: [number, number] | null;
      case: {
        tp: number;
        fp: number;
        tn: number;
        fn: number;
        precision: number | null;
        recall: number | null;
        specificity: number | null;
        fpr: number | null;
        balanced_accuracy: number | null;
        mcc: number | null;
      };
      by_surface: Record<string, SurfaceMetrics>;
    };
    estate_recall: number | null;
    estate_fact_fn: number;
    estate_fact_tp: number;
  };
  latency_ms?: { n: number; p50: number | null; p95: number | null };
};

type BenchCase = {
  id: string;
  surface: string;
  polarity: string;
  title: string;
  facts: Fact[];
  forbidden: { category: string; value: string }[];
};

const SURFACES = [
  "code",
  "identity",
  "gateway",
  "lowcode",
  "saas",
  "cloud",
  "endpoint",
  "network",
  "runtime",
];

const NAMES: Record<string, string> = {
  shadowscan: "ShadowScan",
  vet: "SafeDep vet",
  numbat: "Perplexity Numbat",
  "snyk-agent-scan": "Snyk Agent Scan",
  "ai-bom": "Trusera ai-bom",
  nuguard: "NuGuard",
  agentdiscover: "AgentDiscover",
  "agentic-radar": "Agentic Radar",
  aiostack: "Aurva AIOstack",
  curatedmcp: "CuratedMCP",
  "reference-lexicon": "Lexicon reference",
};

const board = scoreboard as {
  benchmark: {
    name: string;
    seed: string;
    cases: number;
    corpus_sha256: string;
    provenance: string;
  };
  tools: ToolRow[];
  methodology: Record<string, string | number>;
};

const library = cases as BenchCase[];

export const Route = createFileRoute("/")({ component: Home });

function pct(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return `${Math.round(value * 1000) / 10}%`;
}

function num(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return value.toFixed(2);
}

function Home() {
  const tools = board.tools;
  const products = tools.filter((tool) => tool.role === "tool");
  const [tab, setTab] = useState<"board" | "cases" | "method">("board");
  const [selected, setSelected] = useState(
    products.find((tool) => tool.status === "scored")?.id ?? products[0]?.id ?? "",
  );
  const [surface, setSurface] = useState("all");
  const [polarity, setPolarity] = useState("all");
  const [prefix, setPrefix] = useState("");
  const [query, setQuery] = useState("");
  useEffect(() => {
    const found = previewPathPrefix(window.location.hostname, window.location.pathname);
    if (found) setPrefix(found);
  }, []);

  const active = tools.find((tool) => tool.id === selected);
  const chart = products
    .filter((tool) => tool.metrics)
    .map((tool) => ({
      name: NAMES[tool.id] ?? tool.id,
      f1: Math.round((tool.metrics?.quality.fact.f1 ?? 0) * 1000) / 10,
    }));

  const visibleCases = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return library.filter((item) => {
      if (surface !== "all" && item.surface !== surface) return false;
      if (polarity !== "all" && item.polarity !== polarity) return false;
      if (!needle) return true;
      const blob = `${item.id} ${item.title} ${item.facts.map((fact) => fact.value).join(" ")}`.toLowerCase();
      return blob.includes(needle);
    });
  }, [polarity, query, surface]);

  return (
    <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
      <header className="flex flex-col gap-6 border-b border-line pb-8 sm:flex-row sm:items-end sm:justify-between">
        <div className="max-w-2xl">
          <div className="mb-3 flex items-center gap-2 text-accent">
            <ScanSearch className="size-5" aria-hidden="true" />
            <p className="font-mono text-xs tracking-widest uppercase">Discovery benchmark</p>
          </div>
          <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">{board.benchmark.name}</h1>
          <p className="mt-3 text-base leading-relaxed text-muted">
            Nine surfaces, fifty cases each. Labels are planted evidence, not the output of any
            scanner. In-scope F1 only counts surfaces a tool can actually read.
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            <a
              className="cursor-pointer rounded-full border border-line bg-surface px-4 py-2 text-sm text-ink"
              href={`${prefix}/shadowbench-report.html`}
            >
              HTML report
            </a>
            <a
              className="cursor-pointer rounded-full bg-ink px-4 py-2 text-sm text-paper"
              href={`${prefix}/shadowbench-report.pdf`}
            >
              PDF report
            </a>
          </div>
        </div>
        <dl className="grid grid-cols-2 gap-x-6 gap-y-2 font-mono text-xs text-muted">
          <div>
            <dt>Cases</dt>
            <dd className="text-sm text-ink">{board.benchmark.cases}</dd>
          </div>
          <div>
            <dt>Seed</dt>
            <dd className="text-sm text-ink">{board.benchmark.seed}</dd>
          </div>
          <div className="col-span-2">
            <dt>Corpus</dt>
            <dd className="truncate text-sm text-ink">{board.benchmark.corpus_sha256}</dd>
          </div>
        </dl>
      </header>

      <nav className="mt-6 flex gap-2" aria-label="Sections">
        {(
          [
            ["board", "Scoreboard"],
            ["cases", "Cases"],
            ["method", "Method"],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            onClick={() => setTab(id)}
            className={
              tab === id
                ? "rounded-full bg-ink px-4 py-2 text-sm text-paper"
                : "rounded-full border border-line bg-surface px-4 py-2 text-sm text-ink"
            }
          >
            {label}
          </button>
        ))}
      </nav>

      {tab === "board" && (
        <section className="mt-8 flex flex-col gap-8">
          {products.length === 0 && (
            <p className="rounded-lg border border-line bg-surface p-4 text-sm text-muted">
              The scoring run has not been copied into this view yet.
            </p>
          )}
          <div className="overflow-x-auto rounded-lg border border-line bg-surface">
            <table className="w-full min-w-[44rem] text-left text-sm">
              <thead className="border-b border-line text-xs tracking-wide text-muted uppercase">
                <tr>
                  <th className="px-4 py-3 font-medium">Tool</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Precision</th>
                  <th className="px-4 py-3 font-medium">Recall</th>
                  <th className="px-4 py-3 font-medium">F1</th>
                  <th className="px-4 py-3 font-medium">Specificity</th>
                  <th className="px-4 py-3 font-medium">Estate recall</th>
                </tr>
              </thead>
              <tbody>
                {products.map((tool) => {
                  const fact = tool.metrics?.quality.fact;
                  const on = tool.id === selected;
                  return (
                    <tr key={tool.id} className={on ? "bg-accent-soft" : "border-t border-line"}>
                      <td className="px-4 py-3">
                        <button type="button" className="text-left" onClick={() => setSelected(tool.id)}>
                          <span className="font-medium">{NAMES[tool.id] ?? tool.id}</span>
                        </button>
                      </td>
                      <td className="px-4 py-3 text-muted">{tool.status === "scored" ? "Scored" : "Not run"}</td>
                      <td className="px-4 py-3 font-mono">{pct(fact?.precision)}</td>
                      <td className="px-4 py-3 font-mono">{pct(fact?.recall)}</td>
                      <td className="px-4 py-3 font-mono">{pct(fact?.f1)}</td>
                      <td className="px-4 py-3 font-mono">{pct(tool.metrics?.quality.case.specificity)}</td>
                      <td className="px-4 py-3 font-mono">{pct(tool.metrics?.estate_recall)}</td>
                    </tr>
                  );
                })}
                {tools
                  .filter((tool) => tool.role === "reference")
                  .map((tool) => {
                    const fact = tool.metrics?.quality.fact;
                    return (
                      <tr key={tool.id} className="border-t border-line">
                        <td className="px-4 py-3">
                          <button type="button" className="text-left" onClick={() => setSelected(tool.id)}>
                            <span className="font-medium">{NAMES[tool.id]}</span>
                            <span className="mt-1 block text-xs text-muted">String ceiling, not a product</span>
                          </button>
                        </td>
                        <td className="px-4 py-3 text-muted">Reference</td>
                        <td className="px-4 py-3 font-mono">{pct(fact?.precision)}</td>
                        <td className="px-4 py-3 font-mono">{pct(fact?.recall)}</td>
                        <td className="px-4 py-3 font-mono">{pct(fact?.f1)}</td>
                        <td className="px-4 py-3 font-mono">{pct(tool.metrics?.quality.case.specificity)}</td>
                        <td className="px-4 py-3 font-mono">{pct(tool.metrics?.estate_recall)}</td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>

          {chart.length > 0 && (
            <div className="rounded-lg border border-line bg-surface p-4">
              <h2 className="text-sm font-medium">In-scope fact F1</h2>
              <p className="mt-1 text-xs text-muted">Only surfaces that tool claims to read. 95% bootstrap interval is in the detail.</p>
              <div className="mt-4 h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chart} layout="vertical" margin={{ left: 24, right: 8 }}>
                    <XAxis type="number" domain={[0, 100]} hide />
                    <YAxis type="category" dataKey="name" width={140} tick={{ fill: "var(--color-ink)", fontSize: 12 }} />
                    <Tooltip formatter={(value) => [`${value}%`, "F1"]} />
                    <Bar dataKey="f1" fill="var(--color-accent)" radius={2} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {active && <ToolDetail tool={active} />}
          <Heat tools={products} />
        </section>
      )}

      {tab === "cases" && (
        <section className="mt-8">
          <div className="flex flex-col gap-3 sm:flex-row">
            <select
              className="rounded-lg border border-line bg-surface px-3 py-2 text-sm"
              value={surface}
              onChange={(event) => setSurface(event.target.value)}
              aria-label="Surface"
            >
              <option value="all">All surfaces</option>
              {SURFACES.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
            <select
              className="rounded-lg border border-line bg-surface px-3 py-2 text-sm"
              value={polarity}
              onChange={(event) => setPolarity(event.target.value)}
              aria-label="Polarity"
            >
              <option value="all">All polarities</option>
              <option value="positive">Positive</option>
              <option value="negative">Negative</option>
              <option value="near_miss">Near miss</option>
            </select>
            <input
              className="flex-1 rounded-lg border border-line bg-surface px-3 py-2 text-sm"
              placeholder="Filter by id or signal"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              aria-label="Filter cases"
            />
          </div>
          <p className="mt-3 text-xs text-muted">{visibleCases.length} cases</p>
          <ul className="mt-4 flex flex-col gap-3">
            {visibleCases.slice(0, 40).map((item) => (
              <li key={item.id} className="rounded-lg border border-line bg-surface p-4">
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <h2 className="font-medium">{item.title}</h2>
                  <p className="font-mono text-xs text-muted">
                    {item.id} · {item.polarity}
                  </p>
                </div>
                {item.facts.length > 0 && (
                  <ul className="mt-2 flex flex-col gap-1">
                    {item.facts.map((fact) => (
                      <li key={`${fact.category}:${fact.value}:${fact.path}`} className="text-sm text-muted">
                        <span className="font-mono text-ink">
                          {fact.category}:{fact.value}
                        </span>
                        {fact.quote ? ` — “${fact.quote}”` : ""}
                        {fact.path ? ` in ${fact.path}` : ""}
                      </li>
                    ))}
                  </ul>
                )}
                {item.forbidden.length > 0 && (
                  <p className="mt-2 text-sm text-accent">
                    Must not emit {item.forbidden.map((fact) => `${fact.category}:${fact.value}`).join(", ")}
                  </p>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {tab === "method" && <Method />}
    </main>
  );
}

function ToolDetail({ tool }: { tool: ToolRow }) {
  const quality = tool.metrics?.quality;
  return (
    <article className="rounded-lg border border-line bg-surface p-4 sm:p-6">
      <h2 className="text-xl font-semibold">{NAMES[tool.id] ?? tool.id}</h2>
      <p className="mt-2 text-sm leading-relaxed text-muted">{tool.status_detail}</p>
      <p className="mt-2 font-mono text-xs text-muted">
        {tool.version || "version not recorded"} · surfaces {tool.applicable_surfaces.join(", ") || "none"}
      </p>
      {quality && (
        <dl className="mt-5 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <Stat label="Fact TP / FP / FN" value={`${quality.fact.tp} / ${quality.fact.fp} / ${quality.fact.fn}`} />
          <Stat
            label="Case TP / FP / TN / FN"
            value={`${quality.case.tp} / ${quality.case.fp} / ${quality.case.tn} / ${quality.case.fn}`}
          />
          <Stat label="MCC" value={num(quality.case.mcc)} />
          <Stat label="Balanced accuracy" value={pct(quality.case.balanced_accuracy)} />
          <Stat
            label="F1 95% interval"
            value={
              quality.fact_f1_ci95
                ? `${pct(quality.fact_f1_ci95[0])} – ${pct(quality.fact_f1_ci95[1])}`
                : "—"
            }
          />
          <Stat label="Errors excluded" value={String(quality.errors)} />
          <Stat label="Latency p50" value={tool.latency_ms?.p50 != null ? `${tool.latency_ms.p50} ms` : "—"} />
          <Stat label="Latency p95" value={tool.latency_ms?.p95 != null ? `${tool.latency_ms.p95} ms` : "—"} />
        </dl>
      )}
    </article>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="text-xs text-muted">{label}</dt>
      <dd className="mt-1 font-mono text-sm">{value}</dd>
    </div>
  );
}

function Heat({ tools }: { tools: ToolRow[] }) {
  const scored = tools.filter((tool) => tool.metrics);
  if (scored.length === 0) return null;
  return (
    <div className="overflow-x-auto rounded-lg border border-line bg-surface p-4">
      <h2 className="text-sm font-medium">Recall by surface</h2>
      <p className="mt-1 text-xs text-muted">Blank means the tool was not asked to read that surface.</p>
      <table className="mt-4 w-full min-w-[40rem] text-left text-xs">
        <thead>
          <tr className="text-muted">
            <th className="py-2 pr-3 font-medium">Tool</th>
            {SURFACES.map((surface) => (
              <th key={surface} className="px-1 py-2 font-medium">
                {surface}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {scored.map((tool) => (
            <tr key={tool.id} className="border-t border-line">
              <th className="py-2 pr-3 text-left font-medium">{NAMES[tool.id] ?? tool.id}</th>
              {SURFACES.map((surface) => {
                const cell = tool.metrics?.quality.by_surface[surface];
                const recall = cell?.recall;
                return (
                  <td key={surface} className="px-1 py-2 font-mono">
                    {cell ? pct(recall) : "·"}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Method() {
  return (
    <article className="mt-8 max-w-3xl text-sm leading-relaxed text-muted">
      <h2 className="text-xl font-semibold text-ink">What this measures</h2>
      <p className="mt-3">
        Each surface holds 25 positives, 15 negatives and 10 near-misses. A positive fact is true
        only when its quote is in the cited file. A negative case must produce no mapped finding. A
        near-miss names the lookalike that must not be emitted: Minecraft Bedrock is not AWS
        Bedrock, a CSS cursor is not the Cursor IDE, Claude Bernard is not Claude.
      </p>
      <p className="mt-3">
        These are not private tenant dumps. Identity is an Okta app export, gateways are LiteLLM-style
        JSONL, low-code is an n8n workflow, SaaS is a Slack approved app, cloud is a Bedrock inventory
        record, endpoints are home-directory configs, network is a DNS row, runtime is an osquery
        process list. One documented format per surface. That is the sampling frame.
      </p>
      <h2 className="mt-8 text-xl font-semibold text-ink">How a point is scored</h2>
      <p className="mt-3">
        Fact-level precision, recall and F1 are primary. A positive case is detected if any planted
        fact comes back. Any mapped finding on a negative or near-miss is a false positive.
        Specificity, false-positive rate, balanced accuracy and Matthews correlation use that case
        table. Crashes and timeouts leave the denominator and are counted as errors. A 1,000-draw
        bootstrap over cases gives a 95% interval on fact F1.
      </p>
      <p className="mt-3">
        Estate recall is the harsher number: positives on surfaces the tool cannot read count as
        misses. Unscanned negatives are not called true negatives. The lexicon reference applies the
        published alias list to the artifact text, including paths. It is a string-match ceiling, not
        an eleventh product.
      </p>
      <h2 className="mt-8 text-xl font-semibold text-ink">What was not done</h2>
      <p className="mt-3">
        Tools that need a vendor token or a live Kubernetes cluster were probed and then marked not
        run. Their F1 is left blank on purpose. A zero would pretend the scan happened. Labels were
        not edited to delete a miss after the tools ran. Alias mapping is a published table, and it
        does not read the answer key to pick a category.
      </p>
    </article>
  );
}
