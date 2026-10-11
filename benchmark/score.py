#!/usr/bin/env python3
"""Map scanner strings onto the closed ShadowBench vocabulary and score them.

The alias table is public knowledge (package names, API hosts, product names).
It is not edited against tool output. Mapping never reads truth.json.
A minecraft hostname suppresses AWS Bedrock, because that collision is a
general English/ops ambiguity, not a case id.
"""

from __future__ import annotations

import json
import math
import random
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# (regex, category, value). First match wins per alias; a string may match several aliases.
ALIASES: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"@modelcontextprotocol/server-github|\bmcp-github\b", re.I), "mcp", "mcp-github"),
    (re.compile(r"@modelcontextprotocol/server-filesystem|\bmcp-filesystem\b", re.I), "mcp", "mcp-filesystem"),
    (re.compile(r"@modelcontextprotocol/server-slack|\bmcp-slack\b", re.I), "mcp", "mcp-slack"),
    (re.compile(r"@modelcontextprotocol/server-memory|\bmcp-memory\b", re.I), "mcp", "mcp-memory"),
    (re.compile(r"\blanggraph\b", re.I), "framework", "langgraph"),
    (re.compile(r"\blangchain\b", re.I), "framework", "langchain"),
    (re.compile(r"\bcrewai\b", re.I), "framework", "crewai"),
    (re.compile(r"\bautogen\b|\bpyautogen\b", re.I), "framework", "autogen"),
    (re.compile(r"\bllama[_-]?index\b", re.I), "framework", "llamaindex"),
    (re.compile(r"\bdspy\b", re.I), "framework", "dspy"),
    (re.compile(r"\bpydantic[_-]ai\b", re.I), "framework", "pydantic-ai"),
    (re.compile(r"\bhaystack\b", re.I), "framework", "haystack"),
    (re.compile(r"\bsmolagents\b", re.I), "framework", "smolagents"),
    (re.compile(r"\bsemantic[_-]kernel\b", re.I), "framework", "semantic-kernel"),
    (re.compile(r"api\.openai\.com|chat\.openai\.com|\bopenai\b", re.I), "provider", "openai"),
    (re.compile(r"api\.anthropic\.com|\bimport anthropic\b|\banthropic==|\banthropic\.claude\b|\bclaude-3"), "provider", "anthropic"),
    (re.compile(r"generativelanguage\.googleapis\.com|\bgoogle\.generativeai\b|\bgemini-1\.5\b|\bgoogle-generativeai\b", re.I), "provider", "google-gemini"),
    (re.compile(r"api\.mistral\.ai|\bmistralai\b|\bmistral-large\b|\bmistral\.mistral\b", re.I), "provider", "mistral"),
    (re.compile(r"api\.groq\.com|\bfrom groq import\b|\bgroq==", re.I), "provider", "groq"),
    (re.compile(r"api\.cohere\.ai|\bimport cohere\b|\bcohere==|\bcommand-r-plus\b|\bcohere\.command\b", re.I), "provider", "cohere"),
    (re.compile(r"openrouter\.ai", re.I), "provider", "openrouter"),
    (re.compile(r"\bbedrock-runtime\b|\bprovider\.aws-bedrock\b|\baws-bedrock\b", re.I), "provider", "aws-bedrock"),
    (re.compile(r"\bimport ollama\b|\bollama==", re.I), "provider", "ollama"),
    (re.compile(r"\bollama serve\b|\bllama3\.1\b|\.ollama/", re.I), "local_model", "ollama"),
    (re.compile(r"claude_desktop_config|/opt/Claude/claude|\bclaude-desktop\b", re.I), "agent", "claude-desktop"),
    (re.compile(r"\.claude\.json|\bclaude-code\b|/usr/bin/claude\b", re.I), "agent", "claude-code"),
    (re.compile(r"\.cursor/mcp\.json|(?<![\w.-])cursor(?![\w:-])", re.I), "agent", "cursor"),
    (re.compile(r"\.gemini/|\bgemini-cli\b|/usr/bin/gemini\b", re.I), "agent", "gemini-cli"),
    (re.compile(r"windsurf", re.I), "agent", "windsurf"),
    (re.compile(r"\.codex/|/usr/bin/codex\b|\bcodex-cli\b", re.I), "agent", "codex-cli"),
    (re.compile(r"\.continue/config\.json", re.I), "agent", "continue"),
    (re.compile(r"github copilot|\bgithub-copilot\b", re.I), "agent", "github-copilot"),
    (re.compile(r"\bopenclaw\b", re.I), "agent", "openclaw"),
    (re.compile(r"n8n-nodes-langchain\.openAi", re.I), "lowcode", "n8n-openai"),
    (re.compile(r"n8n-nodes-langchain\.anthropic", re.I), "lowcode", "n8n-anthropic"),
    (re.compile(r"n8n-nodes-langchain\.googleGemini", re.I), "lowcode", "n8n-gemini"),
    (re.compile(r"n8n-nodes-langchain\.mistral", re.I), "lowcode", "n8n-mistral"),
    (re.compile(r"n8n-nodes-langchain\.agent", re.I), "lowcode", "n8n-agent"),
    (re.compile(r"bedrock-agent|Bedrock Agent|_kind\"?\s*:\s*\"bedrock-agent\"", re.I), "cloud_agent", "bedrock-agent"),
    (re.compile(r"\bChatGPT\b"), "product", "chatgpt"),
    (re.compile(r"\bClaude\b"), "product", "claude"),
    (re.compile(r"\bGemini\b"), "product", "gemini"),
    (re.compile(r"GitHub Copilot"), "product", "github-copilot"),
    (re.compile(r"Notion AI"), "product", "notion-ai"),
    (re.compile(r"Microsoft Copilot"), "product", "microsoft-copilot"),
    (re.compile(r"\bPerplexity\b"), "product", "perplexity"),
    (re.compile(r"\bMistral\b"), "product", "mistral"),
    (re.compile(r"\bGroq\b"), "product", "groq"),
    (re.compile(r"\bCohere\b"), "product", "cohere"),
    (re.compile(r"\bMidjourney\b"), "product", "midjourney"),
    (re.compile(r"\bElevenLabs\b"), "product", "elevenlabs"),
    (re.compile(r"\bRunway\b"), "product", "runway"),
    (re.compile(r"Character\.AI"), "product", "character-ai"),
    (re.compile(r"\bPoe\b"), "product", "poe"),
    (re.compile(r"\bPhind\b"), "product", "phind"),
    (re.compile(r"\bCodeium\b"), "product", "codeium"),
    (re.compile(r"\bTabnine\b"), "product", "tabnine"),
    (re.compile(r"Sourcegraph Cody|\bCody\b"), "product", "cody"),
    (re.compile(r"Amazon Q"), "product", "amazon-q"),
    (re.compile(r"\bJasper\b"), "product", "jasper"),
    (re.compile(r"Copy\.ai"), "product", "copy-ai"),
    (re.compile(r"You\.com"), "product", "you-com"),
    (re.compile(r"Hugging Face"), "product", "huggingface"),
]

PRODUCT_CATEGORY = {
    "identity": "identity_grant",
    "saas": "saas_ai",
    "network": "egress",
    "gateway": "provider",
    "code": "provider",
    "endpoint": "agent",
    "runtime": "agent",
    "cloud": "provider",
    "lowcode": "provider",
}

# Product values that are providers when seen on a technical surface.
PRODUCT_AS_PROVIDER = {
    "openai", "anthropic", "google-gemini", "mistral", "groq", "cohere", "openrouter", "aws-bedrock",
}
PRODUCT_VALUE_ALIAS = {
    "chatgpt": "openai",
    "claude": "anthropic",
    "gemini": "google-gemini",
}


def map_text(text: str, surface: str) -> set[tuple[str, str]]:
    if not text or "minecraft" in text.lower() and "bedrock" in text.lower() and "agentArn" not in text:
        # Keep non-bedrock matches (none expected) but drop bedrock claims tied to the game.
        suppressed = True
    else:
        suppressed = False
    found: set[tuple[str, str]] = set()
    for pattern, category, value in ALIASES:
        if pattern.search(text) is None:
            continue
        if suppressed and value in {"bedrock-agent", "aws-bedrock"}:
            continue
        if category == "product":
            if surface in {"identity", "saas"}:
                found.add((PRODUCT_CATEGORY[surface], value))
            elif surface == "network":
                found.add(("egress", PRODUCT_VALUE_ALIAS.get(value, value)))
            elif surface == "endpoint":
                if value == "claude":
                    found.add(("agent", "claude-desktop"))
                elif value == "cursor":
                    found.add(("agent", "cursor"))
                elif value == "gemini":
                    found.add(("agent", "gemini-cli"))
            elif surface == "runtime":
                if value == "claude":
                    found.add(("agent", "claude-code"))
            else:
                provider = PRODUCT_VALUE_ALIAS.get(value)
                if provider:
                    found.add(("provider", provider))
            continue
        if category == "provider" and surface == "network":
            found.add(("egress", value))
            continue
        if category == "local_model" and surface == "code" and value == "ollama":
            found.add(("local_model", "ollama"))
            continue
        found.add((category, value))
    return found


def map_strings(strings: list[str], surface: str) -> list[dict]:
    found: set[tuple[str, str]] = set()
    for text in strings:
        found |= map_text(text, surface)
    return [{"category": c, "value": v} for c, v in sorted(found)]


def _prf(tp: int, fp: int, fn: int) -> dict:
    precision = tp / (tp + fp) if (tp + fp) else None
    recall = tp / (tp + fn) if (tp + fn) else None
    if precision is None or recall is None or (precision + recall) == 0:
        f1 = None if precision is None and recall is None else 0.0 if precision is not None or recall is not None else None
        if precision == 0 or recall == 0:
            f1 = 0.0
        elif precision is None or recall is None:
            f1 = None
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision, "recall": recall, "f1": f1}


def _mcc(tp: int, fp: int, tn: int, fn: int) -> float | None:
    denom = (tp + fp) * (tp + fn) * (tn + fp) * (tn + fn)
    if denom == 0:
        return None
    return (tp * tn - fp * fn) / math.sqrt(denom)


def score_tool(cases: list[dict], predictions: dict[str, dict], applicable: set[str]) -> dict:
    """predictions[case_id] = {findings: [{category,value}], error: bool}"""

    def accumulate(surface_filter: set[str] | None, missing_is_fn: bool) -> dict:
        tp = fp = fn = 0
        c_tp = c_fp = c_tn = c_fn = 0
        errors = 0
        by_surface = {}
        scanned = 0
        for case in cases:
            if surface_filter is not None and case["surface"] not in surface_filter:
                if not missing_is_fn:
                    continue
            pred = predictions.get(case["id"])
            if pred is None or pred.get("error"):
                errors += 1
                if missing_is_fn:
                    fn += len(case["facts"])
                    if case["polarity"] == "positive":
                        c_fn += 1
                continue
            if surface_filter is not None and case["surface"] not in surface_filter:
                # Estate view: tool did not look. Count missed positives, do not count negatives as TN.
                if case["polarity"] == "positive":
                    fn += len(case["facts"])
                    c_fn += 1
                continue
            scanned += 1
            found = {(f["category"], f["value"]) for f in pred.get("findings") or []}
            truth = {(f["category"], f["value"]) for f in case["facts"]}
            stp, sfp, sfn = len(found & truth), len(found - truth), len(truth - found)
            tp += stp
            fp += sfp
            fn += sfn
            bucket = by_surface.setdefault(case["surface"], {"tp": 0, "fp": 0, "fn": 0, "case_tp": 0, "case_fp": 0, "case_tn": 0, "case_fn": 0})
            bucket["tp"] += stp
            bucket["fp"] += sfp
            bucket["fn"] += sfn
            if case["polarity"] == "positive":
                if truth and (found & truth):
                    c_tp += 1
                    bucket["case_tp"] += 1
                else:
                    c_fn += 1
                    bucket["case_fn"] += 1
            else:
                if found:
                    c_fp += 1
                    bucket["case_fp"] += 1
                else:
                    c_tn += 1
                    bucket["case_tn"] += 1
        fact = _prf(tp, fp, fn)
        spec = c_tn / (c_tn + c_fp) if (c_tn + c_fp) else None
        case_recall = c_tp / (c_tp + c_fn) if (c_tp + c_fn) else None
        case_precision = c_tp / (c_tp + c_fp) if (c_tp + c_fp) else None
        surfaces = {}
        for name, bucket in by_surface.items():
            surfaces[name] = {**_prf(bucket["tp"], bucket["fp"], bucket["fn"]), "case_tp": bucket["case_tp"], "case_fp": bucket["case_fp"], "case_tn": bucket["case_tn"], "case_fn": bucket["case_fn"]}
        return {
            "cases_scored": scanned,
            "errors": errors,
            "fact": fact,
            "case": {
                "tp": c_tp,
                "fp": c_fp,
                "tn": c_tn,
                "fn": c_fn,
                "precision": case_precision,
                "recall": case_recall,
                "specificity": spec,
                "fpr": (1 - spec) if spec is not None else None,
                "balanced_accuracy": ((case_recall + spec) / 2) if case_recall is not None and spec is not None else None,
                "mcc": _mcc(c_tp, c_fp, c_tn, c_fn),
            },
            "by_surface": surfaces,
        }

    quality = accumulate(applicable, missing_is_fn=False)
    estate = accumulate(applicable, missing_is_fn=True)
    # Bootstrap fact-F1 over applicable cases that did not error.
    rng = random.Random(450)
    pool = [c for c in cases if c["surface"] in applicable and not (predictions.get(c["id"]) or {}).get("error")]
    scores = []
    if pool:
        for _ in range(1000):
            sample = [pool[rng.randrange(len(pool))] for _ in range(len(pool))]
            tp = fp = fn = 0
            for case in sample:
                found = {(f["category"], f["value"]) for f in (predictions.get(case["id"]) or {}).get("findings") or []}
                truth = {(f["category"], f["value"]) for f in case["facts"]}
                tp += len(found & truth)
                fp += len(found - truth)
                fn += len(truth - found)
            f1 = _prf(tp, fp, fn)["f1"]
            if f1 is not None:
                scores.append(f1)
    scores.sort()
    ci = None
    if scores:
        ci = [scores[int(0.025 * (len(scores) - 1))], scores[int(0.975 * (len(scores) - 1))]]
    quality["fact_f1_ci95"] = ci
    return {"quality": quality, "estate_recall": estate["fact"]["recall"], "estate_fact_fn": estate["fact"]["fn"], "estate_fact_tp": estate["fact"]["tp"]}


def load_cases(corpus: Path) -> list[dict]:
    cases = []
    for path in sorted(corpus.glob("*/*/truth.json")):
        cases.append(json.loads(path.read_text(encoding="utf-8")))
    return cases


def _self_test() -> None:
    assert ("provider", "openai") in map_text("from openai import OpenAI", "code")
    assert ("cloud_agent", "bedrock-agent") not in map_text("polls bedrock.minecraft.net", "cloud")
    assert ("framework", "langchain") in map_text("from langchain.chat_models import ChatOpenAI", "code")
    assert ("agent", "cursor") not in map_text(".cursor { cursor: pointer; }", "code")
    assert ("mcp", "mcp-github") in map_text("@modelcontextprotocol/server-github", "endpoint")
    assert ("identity_grant", "chatgpt") in map_text("ChatGPT", "identity")
    assert ("saas_ai", "notion-ai") in map_text("Notion AI", "saas")
    cases = [
        {"id": "a", "surface": "code", "polarity": "positive", "facts": [{"category": "provider", "value": "openai"}]},
        {"id": "b", "surface": "code", "polarity": "negative", "facts": []},
        {"id": "c", "surface": "code", "polarity": "near_miss", "facts": []},
        {"id": "d", "surface": "identity", "polarity": "positive", "facts": [{"category": "identity_grant", "value": "chatgpt"}]},
    ]
    preds = {
        "a": {"findings": [{"category": "provider", "value": "openai"}], "error": False},
        "b": {"findings": [], "error": False},
        "c": {"findings": [{"category": "provider", "value": "openai"}], "error": False},
        "d": {"findings": [], "error": False},
    }
    scored = score_tool(cases, preds, {"code"})
    assert scored["quality"]["fact"]["tp"] == 1
    assert scored["quality"]["fact"]["fp"] == 1
    assert scored["quality"]["fact"]["fn"] == 0
    assert scored["quality"]["case"]["tn"] == 1
    assert scored["quality"]["case"]["fp"] == 1
    assert scored["estate_recall"] == 0.5


if __name__ == "__main__":
    _self_test()
    print("score self-test ok")
