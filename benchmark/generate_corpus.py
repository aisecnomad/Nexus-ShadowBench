#!/usr/bin/env python3
"""ShadowBench corpus generator.

Sampling frame (frozen, not fit to any scanner):
  9 surfaces x 50 cases = 450.
  Per surface: indices 0-24 positive, 25-39 negative, 40-49 near-miss.

Provenance is synthetic-realistic: vendor-shaped artifacts with planted
evidence quotes. These are not private tenant dumps and were not labeled by
any tool under test. A third party verifies a case by reading truth.json and
confirming each quote occurs in the cited file.

One documented format is exercised per surface (see SURFACE_FORMAT). That is
a sampling-frame limit, not a claim that the format is the whole surface.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CORPUS = ROOT / "corpus"
SEED = "shadowbench-450-v1"
NAME = "ShadowBench"

SURFACES = (
    "code",
    "identity",
    "gateway",
    "lowcode",
    "saas",
    "cloud",
    "endpoint",
    "network",
    "runtime",
)

SURFACE_FORMAT = {
    "code": "Minimal application tree (Python or Node, plus optional agent config).",
    "identity": "Okta GET /api/v1/apps JSON export, status ACTIVE.",
    "gateway": "LiteLLM-style JSONL spend log (one record).",
    "lowcode": "n8n workflow export JSON (id, name, nodes, connections).",
    "saas": "Slack admin approved-app record JSON, with workspace id.",
    "cloud": "JSONL record in the AWS inventory dump shape (agent or lambda).",
    "endpoint": "Linux home-directory fragment with vendor config paths.",
    "network": "JSONL DNS log row with src_ip, query and ts.",
    "runtime": "osquery processes JSON array (name, path, cmdline, pid).",
}

# Closed vocabulary. Aliases live in score.py and must not be edited to chase a tool.
PRODUCTS = [
    ("chatgpt", "ChatGPT", "https://chat.openai.com", "openai"),
    ("claude", "Claude", "https://claude.ai", "anthropic"),
    ("gemini", "Gemini", "https://gemini.google.com", "google-gemini"),
    ("github-copilot", "GitHub Copilot", "https://github.com/features/copilot", "github-copilot"),
    ("notion-ai", "Notion AI", "https://www.notion.so/product/ai", "notion-ai"),
    ("microsoft-copilot", "Microsoft Copilot", "https://copilot.microsoft.com", "microsoft-copilot"),
    ("perplexity", "Perplexity", "https://www.perplexity.ai", "perplexity"),
    ("cursor", "Cursor", "https://cursor.com", "cursor"),
    ("mistral", "Mistral", "https://chat.mistral.ai", "mistral"),
    ("groq", "Groq", "https://groq.com", "groq"),
    ("cohere", "Cohere", "https://cohere.com", "cohere"),
    ("midjourney", "Midjourney", "https://www.midjourney.com", "midjourney"),
    ("elevenlabs", "ElevenLabs", "https://elevenlabs.io", "elevenlabs"),
    ("runway", "Runway", "https://runwayml.com", "runway"),
    ("character-ai", "Character.AI", "https://character.ai", "character-ai"),
    ("poe", "Poe", "https://poe.com", "poe"),
    ("phind", "Phind", "https://www.phind.com", "phind"),
    ("codeium", "Codeium", "https://codeium.com", "codeium"),
    ("tabnine", "Tabnine", "https://www.tabnine.com", "tabnine"),
    ("cody", "Sourcegraph Cody", "https://sourcegraph.com/cody", "cody"),
    ("amazon-q", "Amazon Q", "https://aws.amazon.com/q", "amazon-q"),
    ("jasper", "Jasper", "https://www.jasper.ai", "jasper"),
    ("copy-ai", "Copy.ai", "https://www.copy.ai", "copy-ai"),
    ("you-com", "You.com", "https://you.com", "you-com"),
    ("huggingface", "Hugging Face", "https://huggingface.co", "huggingface"),
]

NEG_APPS = [
    ("Workday", "https://www.workday.com"),
    ("DocuSign", "https://www.docusign.com"),
    ("Zendesk", "https://www.zendesk.com"),
    ("PagerDuty", "https://www.pagerduty.com"),
    ("Figma", "https://www.figma.com"),
    ("Box", "https://www.box.com"),
    ("Dropbox", "https://www.dropbox.com"),
    ("Datadog", "https://www.datadoghq.com"),
    ("ServiceNow ITSM", "https://www.servicenow.com"),
    ("Jira", "https://www.atlassian.com/software/jira"),
    ("Okta Dashboard", "https://www.okta.com"),
    ("Salesforce CRM", "https://www.salesforce.com"),
    ("Zoom Meetings", "https://zoom.us"),
    ("Slack", "https://slack.com"),
    ("GitHub", "https://github.com"),
]

NEAR_APPS = [
    ("Claude Bernard Gallery", "https://claudebernard.example", "claude"),
    ("Cursor Manufacturing ERP", "https://cursor-mfg.example", "cursor"),
    ("Gemini Freight Lines", "https://geminifreight.example", "gemini"),
    ("Copilot Insurance Agency", "https://copilot-insurance.example", "github-copilot"),
    ("Bedrock Landscaping", "https://bedrock-landscaping.example", "bedrock-agent"),
    ("Agent Provocateur HR", "https://agent-hr.example", "chatgpt"),
    ("Einstein Bros Catering", "https://einsteinbros.example", "salesforce-einstein"),
    ("Open Air Travel", "https://openair.example", "openai"),
    ("Notion Template Club", "https://notion-templates.example", "notion-ai"),
    ("AI Book Club", "https://aibookclub.example", "slack-ai"),
]

CODE_POS = [
    ("provider", "openai", {"requirements.txt": "openai==1.40.0\n", "src/chat.py": "from openai import OpenAI\nclient = OpenAI()\n"}, "src/chat.py", "from openai import OpenAI"),
    ("framework", "langchain", {"requirements.txt": "langchain==0.2.14\n", "src/chain.py": "from langchain.chat_models import ChatOpenAI\n"}, "src/chain.py", "from langchain.chat_models import ChatOpenAI"),
    ("framework", "langgraph", {"requirements.txt": "langgraph==0.2.16\n", "src/graph.py": "from langgraph.graph import StateGraph\nworkflow = StateGraph(dict)\n"}, "src/graph.py", "from langgraph.graph import StateGraph"),
    ("framework", "crewai", {"requirements.txt": "crewai==0.51.0\n", "src/crew.py": "from crewai import Agent, Crew\n"}, "src/crew.py", "from crewai import Agent, Crew"),
    ("framework", "autogen", {"requirements.txt": "pyautogen==0.2.35\n", "src/team.py": "from autogen import AssistantAgent\n"}, "src/team.py", "from autogen import AssistantAgent"),
    ("provider", "anthropic", {"requirements.txt": "anthropic==0.34.0\n", "src/ask.py": "import anthropic\nclient = anthropic.Anthropic()\n"}, "src/ask.py", "import anthropic"),
    ("provider", "google-gemini", {"requirements.txt": "google-generativeai==0.7.2\n", "src/gem.py": "import google.generativeai as genai\n"}, "src/gem.py", "import google.generativeai as genai"),
    ("mcp", "mcp-github", {".cursor/mcp.json": '{\n  "mcpServers": {\n    "github": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"]}\n  }\n}\n'}, ".cursor/mcp.json", "@modelcontextprotocol/server-github"),
    ("agent", "claude-code", {".mcp.json": '{\n  "mcpServers": {\n    "filesystem": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]}\n  }\n}\n', "CLAUDE.md": "# Project notes\nUse the filesystem tools already configured.\n"}, ".mcp.json", "@modelcontextprotocol/server-filesystem"),
    ("framework", "llamaindex", {"requirements.txt": "llama-index==0.10.55\n", "src/idx.py": "from llama_index.core import VectorStoreIndex\n"}, "src/idx.py", "from llama_index.core import VectorStoreIndex"),
    ("framework", "dspy", {"requirements.txt": "dspy-ai==2.4.14\n", "src/opt.py": "import dspy\nlm = dspy.LM('local-student')\n"}, "src/opt.py", "import dspy"),
    ("framework", "pydantic-ai", {"requirements.txt": "pydantic-ai==0.0.14\n", "src/agent.py": "from pydantic_ai import Agent\n"}, "src/agent.py", "from pydantic_ai import Agent"),
    ("framework", "haystack", {"requirements.txt": "haystack-ai==2.4.0\n", "src/pipe.py": "from haystack import Pipeline\n"}, "src/pipe.py", "from haystack import Pipeline"),
    ("framework", "smolagents", {"requirements.txt": "smolagents==1.0.0\n", "src/loop.py": "from smolagents import CodeAgent\n"}, "src/loop.py", "from smolagents import CodeAgent"),
    ("provider", "mistral", {"requirements.txt": "mistralai==1.0.3\n", "src/m.py": "from mistralai.client import MistralClient\n"}, "src/m.py", "from mistralai.client import MistralClient"),
    ("provider", "groq", {"requirements.txt": "groq==0.9.0\n", "src/g.py": "from groq import Groq\nclient = Groq()\n"}, "src/g.py", "from groq import Groq"),
    ("provider", "cohere", {"requirements.txt": "cohere==5.8.0\n", "src/c.py": "import cohere\nco = cohere.Client()\n"}, "src/c.py", "import cohere"),
    ("provider", "ollama", {"requirements.txt": "ollama==0.3.3\n", "src/local.py": "import ollama\nollama.chat(model='local')\n"}, "src/local.py", "import ollama"),
    ("local_model", "ollama", {"Modelfile": "FROM llama3.1\nSYSTEM You are a reviewer.\n"}, "Modelfile", "FROM llama3.1"),
    ("mcp", "mcp-filesystem", {".vscode/mcp.json": '{\n  "servers": {\n    "filesystem": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]}\n  }\n}\n'}, ".vscode/mcp.json", "@modelcontextprotocol/server-filesystem"),
    ("agent", "cursor", {"package.json": '{\n  "name": "desk",\n  "private": true\n}\n', ".cursor/mcp.json": '{\n  "mcpServers": {\n    "memory": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-memory"]}\n  }\n}\n'}, ".cursor/mcp.json", "@modelcontextprotocol/server-memory"),
    ("provider", "openrouter", {"requirements.txt": "openai==1.40.0\n", "src/route.py": "from openai import OpenAI\nclient = OpenAI(base_url='https://openrouter.ai/api/v1')\n"}, "src/route.py", "https://openrouter.ai/api/v1"),
    ("provider", "aws-bedrock", {"src/bedrock_call.py": "import boto3\nclient = boto3.client('bedrock-runtime')\nclient.invoke_model(modelId='anthropic.claude-3-haiku')\n"}, "src/bedrock_call.py", "boto3.client('bedrock-runtime')"),
    ("framework", "semantic-kernel", {"requirements.txt": "semantic-kernel==1.9.0\n", "src/sk.py": "import semantic_kernel\n"}, "src/sk.py", "import semantic_kernel"),
    ("a2a", "a2a-card", {"agent-card.json": '{\n  "name": "support-agent",\n  "protocol": "a2a",\n  "url": "https://agents.internal.example/support"\n}\n'}, "agent-card.json", '"protocol": "a2a"'),
]

# Fix: index 8 plants mcp filesystem AND is labeled agent claude-code because of CLAUDE.md.
# The quote is the mcp package; also record the agent fact from CLAUDE.md presence via a second fact
# added below in emit_code.

CODE_NEG_LIBS = [
    ("flask", "Flask==3.0.3"),
    ("requests", "requests==2.32.3"),
    ("numpy", "numpy==1.26.4"),
    ("pandas", "pandas==2.2.2"),
    ("fastapi", "fastapi==0.112.0"),
    ("click", "click==8.1.7"),
    ("pyyaml", "PyYAML==6.0.2"),
    ("rich", "rich==13.7.1"),
    ("httpx", "httpx==0.27.0"),
    ("pydantic", "pydantic==2.8.2"),
    ("sqlalchemy", "SQLAlchemy==2.0.32"),
    ("pytest", "pytest==8.3.2"),
    ("typer", "typer==0.12.4"),
    ("uvicorn", "uvicorn==0.30.6"),
    ("jinja2", "Jinja2==3.1.4"),
]

HOSTS = {
    "openai": "api.openai.com",
    "anthropic": "api.anthropic.com",
    "google-gemini": "generativelanguage.googleapis.com",
    "mistral": "api.mistral.ai",
    "groq": "api.groq.com",
    "cohere": "api.cohere.ai",
    "openrouter": "openrouter.ai",
    "ollama": "localhost",
}

N8N_NODES = [
    ("@n8n/n8n-nodes-langchain.openAi", "n8n-openai", "openai"),
    ("@n8n/n8n-nodes-langchain.anthropic", "n8n-anthropic", "anthropic"),
    ("@n8n/n8n-nodes-langchain.googleGemini", "n8n-gemini", "google-gemini"),
    ("@n8n/n8n-nodes-langchain.mistral", "n8n-mistral", "mistral"),
    ("@n8n/n8n-nodes-langchain.agent", "n8n-agent", "langchain"),
]


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def case_id(surface: str, index: int) -> str:
    return f"{surface}-{index + 1:03d}"


def polarity(index: int) -> str:
    if index < 25:
        return "positive"
    if index < 40:
        return "negative"
    return "near_miss"


def dump_truth(directory: Path, payload: dict) -> None:
    for fact in payload["facts"]:
        body = (directory / fact["path"]).read_text(encoding="utf-8")
        if fact["quote"] not in body:
            raise SystemExit(f"quote missing in {payload['id']}: {fact['quote']!r}")
    write(directory / "truth.json", json.dumps(payload, indent=2) + "\n")


def base_truth(surface: str, index: int, title: str, facts: list, forbidden: list) -> dict:
    return {
        "id": case_id(surface, index),
        "surface": surface,
        "index": index,
        "polarity": polarity(index),
        "title": title,
        "provenance": "synthetic-realistic",
        "format": SURFACE_FORMAT[surface],
        "seed": SEED,
        "facts": facts,
        "forbidden": forbidden,
    }


def emit_code(index: int, directory: Path) -> None:
    pol = polarity(index)
    if pol == "positive":
        cat, value, files, quote_path, quote = CODE_POS[index]
        for rel, body in files.items():
            write(directory / rel, body)
        facts = [{"category": cat, "value": value, "path": quote_path, "quote": quote}]
        if index == 8:
            facts.append({"category": "mcp", "value": "mcp-filesystem", "path": ".mcp.json", "quote": "@modelcontextprotocol/server-filesystem"})
            facts[0] = {"category": "agent", "value": "claude-code", "path": "CLAUDE.md", "quote": "filesystem tools already configured"}
        if index == 21:
            facts.append({"category": "provider", "value": "openai", "path": "src/route.py", "quote": "from openai import OpenAI"})
        if index == 22:
            facts.append({"category": "provider", "value": "anthropic", "path": "src/bedrock_call.py", "quote": "anthropic.claude-3-haiku"})
        title = f"Code signal {value}"
        forbidden = []
    elif pol == "negative":
        lib, pin = CODE_NEG_LIBS[index - 25]
        write(directory / "requirements.txt", pin + "\n")
        write(directory / "src/app.py", f"import {lib.split('-')[0] if False else 'sys'}\n\ndef main():\n    print({lib!r})\n")
        write(directory / "README.md", f"# {lib}\nInternal utility. No model calls.\n")
        facts, forbidden, title = [], [], f"Ordinary {lib} service"
    else:
        kind = index - 40
        facts = []
        if kind == 0:
            write(directory / "README.md", "This mod targets Minecraft Bedrock edition. The agent path is the mob spawner, not a model.\n")
            forbidden = [{"category": "provider", "value": "aws-bedrock"}, {"category": "cloud_agent", "value": "bedrock-agent"}]
            title = "Minecraft Bedrock notes"
        elif kind == 1:
            write(directory / "package.json", '{\n  "name": "desk-proxy",\n  "dependencies": {"agent-base": "7.1.1", "https-proxy-agent": "7.0.5"}\n}\n')
            forbidden = [{"category": "agent", "value": "cursor"}, {"category": "framework", "value": "autogen"}]
            title = "HTTP agent-base dependency"
        elif kind == 2:
            write(directory / "docs/history.md", "In the seminar we discussed OpenAI as a company. This file is not a client SDK.\n")
            forbidden = [{"category": "provider", "value": "openai"}]
            title = "Prose mention of OpenAI"
        elif kind == 3:
            write(directory / "web/theme.css", ".cursor { cursor: pointer; caret-color: auto; }\n")
            forbidden = [{"category": "agent", "value": "cursor"}]
            title = "CSS cursor property"
        elif kind == 4:
            write(directory / "src/essay.py", "# claude bernard was a physiologist\nprint('lecture notes')\n")
            forbidden = [{"category": "agent", "value": "claude-code"}, {"category": "provider", "value": "anthropic"}]
            title = "Comment naming Claude Bernard"
        elif kind == 5:
            write(directory / "README.md", "Our travel agent booked the offsite. No software agent is installed.\n")
            forbidden = [{"category": "agent", "value": "claude-code"}]
            title = "Travel agent prose"
        elif kind == 6:
            write(directory / "src/mock_notes.py", "SAMPLE = 'gpt is an initialism in this glossary, not a client'\n")
            forbidden = [{"category": "provider", "value": "openai"}]
            title = "Glossary initialism"
        elif kind == 7:
            write(directory / "infra/readme.md", "The hostname bedrock.minecraft.net is a game status page.\n")
            forbidden = [{"category": "provider", "value": "aws-bedrock"}, {"category": "cloud_agent", "value": "bedrock-agent"}]
            title = "Minecraft hostname"
        elif kind == 8:
            write(directory / "package.json", '{\n  "name": "shop",\n  "dependencies": {"express": "4.19.2"}\n}\n')
            write(directory / "src/index.js", "const express = require('express')\n")
            forbidden = [{"category": "framework", "value": "langchain"}]
            title = "Express shop"
        else:
            write(directory / "docs/hr.md", "The on-call copilot is a human rotation, not Microsoft Copilot.\n")
            forbidden = [{"category": "agent", "value": "github-copilot"}, {"category": "saas_ai", "value": "microsoft-copilot"}]
            title = "Human on-call copilot"
    dump_truth(directory, base_truth("code", index, title, facts, forbidden))


def okta_app(app_id: str, label: str, url: str) -> str:
    body = {
        "id": app_id,
        "name": "oidc_client",
        "label": label,
        "status": "ACTIVE",
        "signOnMode": "OPENID_CONNECT",
        "settings": {"oauthClient": {"client_uri": url}},
    }
    return json.dumps([body], indent=2) + "\n"


def emit_identity(index: int, directory: Path) -> None:
    pol = polarity(index)
    if pol == "positive":
        value, label, url, _alias = PRODUCTS[index]
        write(directory / "okta-apps.json", okta_app(f"0oa{index:04d}BENCH", label, url))
        facts = [{"category": "identity_grant", "value": value, "path": "okta-apps.json", "quote": label}]
        forbidden, title = [], f"Okta grant {label}"
    elif pol == "negative":
        label, url = NEG_APPS[index - 25]
        write(directory / "okta-apps.json", okta_app(f"0oaN{index:04d}", label, url))
        facts, forbidden, title = [], [], f"Okta grant {label}"
    else:
        label, url, forbidden_value = NEAR_APPS[index - 40]
        write(directory / "okta-apps.json", okta_app(f"0oaM{index:04d}", label, url))
        cat = "provider" if forbidden_value in {"openai"} else "identity_grant"
        if forbidden_value == "bedrock-agent":
            cat = "cloud_agent"
        facts, forbidden, title = [], [{"category": cat, "value": forbidden_value}], f"Okta near-miss {label}"
    dump_truth(directory, base_truth("identity", index, title, facts, forbidden))


def emit_gateway(index: int, directory: Path) -> None:
    pol = polarity(index)
    if pol == "positive":
        providers = ["openai", "anthropic", "google-gemini", "mistral", "groq", "cohere", "openrouter"]
        provider = providers[index % len(providers)]
        model = {
            "openai": "gpt-4o",
            "anthropic": "claude-3-5-sonnet",
            "google-gemini": "gemini-1.5-pro",
            "mistral": "mistral-large",
            "groq": "llama-3.1-70b",
            "cohere": "command-r-plus",
            "openrouter": "openai/gpt-4o",
        }[provider]
        host = HOSTS[provider]
        row = {
            "request_id": f"req-{index:03d}",
            "model": model,
            "custom_llm_provider": provider if provider != "google-gemini" else "gemini",
            "api_base": f"https://{host}",
            "user": f"svc-{index}@example.com",
            "startTime": "2026-06-01T12:00:00Z",
        }
        write(directory / "spend.jsonl", json.dumps(row) + "\n")
        facts = [{"category": "provider", "value": provider, "path": "spend.jsonl", "quote": model}]
        forbidden, title = [], f"Gateway call {model}"
    elif pol == "negative":
        row = {
            "request_id": f"req-n-{index}",
            "method": "GET",
            "api_base": "https://api.github.com",
            "user": "ci@example.com",
            "startTime": "2026-06-01T12:00:00Z",
            "path": "/repos/acme/billing",
        }
        write(directory / "spend.jsonl", json.dumps(row) + "\n")
        facts, forbidden, title = [], [], "Gateway call to GitHub REST"
    else:
        row = {
            "request_id": f"req-m-{index}",
            "model": "steve",
            "api_base": "https://bedrock.minecraft.net/status",
            "user": "player@example.com",
            "startTime": "2026-06-01T12:00:00Z",
            "custom_llm_provider": "status",
        }
        write(directory / "spend.jsonl", json.dumps(row) + "\n")
        facts = []
        forbidden = [{"category": "provider", "value": "aws-bedrock"}, {"category": "cloud_agent", "value": "bedrock-agent"}]
        title = "Gateway row for a game status host"
    dump_truth(directory, base_truth("gateway", index, title, facts, forbidden))


def n8n(workflow_id: str, name: str, node_type: str, node_name: str) -> str:
    body = {
        "id": workflow_id,
        "name": name,
        "nodes": [
            {
                "id": "n1",
                "name": node_name,
                "type": node_type,
                "parameters": {},
                "position": [240, 300],
            }
        ],
        "connections": {},
    }
    return json.dumps(body, indent=2) + "\n"


def emit_lowcode(index: int, directory: Path) -> None:
    pol = polarity(index)
    if pol == "positive":
        node_type, low_value, provider = N8N_NODES[index % len(N8N_NODES)]
        write(directory / "workflow.json", n8n(f"wf-{index:03d}", f"flow-{index}", node_type, "Model"))
        facts = [
            {"category": "lowcode", "value": low_value, "path": "workflow.json", "quote": node_type},
            {"category": "provider" if provider != "langchain" else "framework", "value": provider, "path": "workflow.json", "quote": node_type},
        ]
        if "langchain" in node_type and provider != "langchain":
            facts.append({"category": "framework", "value": "langchain", "path": "workflow.json", "quote": "langchain"})
        forbidden, title = [], f"n8n node {node_type}"
    elif pol == "negative":
        write(directory / "workflow.json", n8n(f"wf-n-{index}", "Nightly CSV", "n8n-nodes-base.spreadsheetFile", "Sheet"))
        facts, forbidden, title = [], [], "n8n spreadsheet workflow"
    else:
        write(directory / "workflow.json", n8n(f"wf-m-{index}", "AI ideas inbox", "n8n-nodes-base.webhook", "Inbox"))
        facts = []
        forbidden = [{"category": "lowcode", "value": "n8n-openai"}, {"category": "provider", "value": "openai"}]
        title = "n8n webhook named AI ideas"
    dump_truth(directory, base_truth("lowcode", index, title, facts, forbidden))


def slack_app(app_id: str, name: str) -> str:
    body = {
        "id": app_id,
        "name": name,
        "scopes": ["chat:write", "users:read"],
        "team_id": "T000BENCH",
    }
    return json.dumps(body, indent=2) + "\n"


def emit_saas(index: int, directory: Path) -> None:
    pol = polarity(index)
    if pol == "positive":
        value, label, _url, _alias = PRODUCTS[index]
        write(directory / "approved-app.json", slack_app(f"A{index:04d}", label))
        facts = [{"category": "saas_ai", "value": value, "path": "approved-app.json", "quote": label}]
        forbidden, title = [], f"Slack app {label}"
    elif pol == "negative":
        label, _url = NEG_APPS[index - 25]
        write(directory / "approved-app.json", slack_app(f"A9{index:04d}", label))
        facts, forbidden, title = [], [], f"Slack app {label}"
    else:
        label, _url, forbidden_value = NEAR_APPS[index - 40]
        write(directory / "approved-app.json", slack_app(f"A8{index:04d}", label))
        cat = "saas_ai"
        if forbidden_value in {"openai"}:
            cat = "provider"
        if forbidden_value == "bedrock-agent":
            cat = "cloud_agent"
        facts, forbidden, title = [], [{"category": cat, "value": forbidden_value}], f"Slack near-miss {label}"
    dump_truth(directory, base_truth("saas", index, title, facts, forbidden))


def emit_cloud(index: int, directory: Path) -> None:
    pol = polarity(index)
    if pol == "positive":
        models = [
            ("anthropic.claude-3-sonnet-20240229-v1:0", "anthropic"),
            ("amazon.titan-text-express-v1", "aws-bedrock"),
            ("meta.llama3-70b-instruct-v1:0", "aws-bedrock"),
            ("mistral.mistral-large-2402-v1:0", "mistral"),
            ("cohere.command-r-plus-v1:0", "cohere"),
        ]
        model, provider = models[index % len(models)]
        rec = {
            "_kind": "bedrock-agent",
            "agentName": f"agent-{index:03d}",
            "agentId": f"A{index:04d}AGENT",
            "agentStatus": "PREPARED",
            "foundationModel": model,
            "agentArn": f"arn:aws:bedrock:us-east-1:123456789012:agent/A{index:04d}AGENT",
            "_region": "us-east-1",
        }
        write(directory / "aws.jsonl", json.dumps(rec) + "\n")
        facts = [
            {"category": "cloud_agent", "value": "bedrock-agent", "path": "aws.jsonl", "quote": rec["agentName"]},
            {"category": "provider", "value": "aws-bedrock", "path": "aws.jsonl", "quote": "bedrock"},
        ]
        if provider != "aws-bedrock":
            facts.append({"category": "provider", "value": provider, "path": "aws.jsonl", "quote": model})
        forbidden, title = [], f"Bedrock agent {rec['agentName']}"
    elif pol == "negative":
        rec = {
            "_kind": "lambda",
            "FunctionName": f"billing-csv-{index}",
            "Runtime": "python3.12",
            "Handler": "index.handler",
            "FunctionArn": f"arn:aws:lambda:us-east-1:123456789012:function:billing-csv-{index}",
        }
        write(directory / "aws.jsonl", json.dumps(rec) + "\n")
        facts, forbidden, title = [], [], f"Lambda {rec['FunctionName']}"
    else:
        rec = {
            "_kind": "lambda",
            "FunctionName": "bedrock-minecraft-status",
            "Runtime": "nodejs20.x",
            "Handler": "index.handler",
            "Description": "Polls bedrock.minecraft.net for the office game server",
            "FunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:bedrock-minecraft-status",
        }
        write(directory / "aws.jsonl", json.dumps(rec) + "\n")
        facts = []
        forbidden = [{"category": "cloud_agent", "value": "bedrock-agent"}, {"category": "provider", "value": "aws-bedrock"}]
        title = "Lambda that polls a game host"
    dump_truth(directory, base_truth("cloud", index, title, facts, forbidden))


ENDPOINT_POS = [
    ("agent", "cursor", ".cursor/mcp.json", '{\n  "mcpServers": {\n    "github": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"]}\n  }\n}\n', "@modelcontextprotocol/server-github", "mcp", "mcp-github"),
    ("agent", "claude-code", ".claude.json", '{\n  "mcpServers": {\n    "filesystem": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem"]}\n  }\n}\n', "server-filesystem", "mcp", "mcp-filesystem"),
    ("agent", "claude-desktop", ".config/Claude/claude_desktop_config.json", '{\n  "mcpServers": {\n    "slack": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-slack"]}\n  }\n}\n', "server-slack", "mcp", "mcp-slack"),
    ("agent", "gemini-cli", ".gemini/settings.json", '{\n  "mcpServers": {\n    "memory": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-memory"]}\n  }\n}\n', "server-memory", "mcp", "mcp-memory"),
    ("agent", "windsurf", ".codeium/windsurf/mcp_config.json", '{\n  "mcpServers": {\n    "github": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"]}\n  }\n}\n', "server-github", "mcp", "mcp-github"),
    ("agent", "codex-cli", ".codex/config.toml", 'model = "gpt-4.1"\n[mcp_servers.github]\ncommand = "npx"\nargs = ["-y", "@modelcontextprotocol/server-github"]\n', "mcp_servers.github", "mcp", "mcp-github"),
    ("local_model", "ollama", ".ollama/models/manifests/registry.ollama.ai/library/llama3.1", '{"model":"llama3.1"}\n', "llama3.1", None, None),
    ("agent", "continue", ".continue/config.json", '{\n  "models": [{"title": "GPT-4o", "provider": "openai", "model": "gpt-4o"}]\n}\n', '"provider": "openai"', "provider", "openai"),
    ("agent", "github-copilot", ".config/Code/User/mcp.json", '{\n  "servers": {\n    "github": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-github"]}\n  }\n}\n', "server-github", "mcp", "mcp-github"),
    ("agent", "openclaw", ".openclaw/config.json", '{\n  "agent": "openclaw",\n  "model": "openai/gpt-4o"\n}\n', '"agent": "openclaw"', "provider", "openai"),
]


def emit_endpoint(index: int, directory: Path) -> None:
    home = directory / "home"
    pol = polarity(index)
    if pol == "positive":
        spec = ENDPOINT_POS[index % len(ENDPOINT_POS)]
        cat, value, rel, body, quote, extra_cat, extra_val = spec
        # Vary the home so cases are not duplicates: stamp an inert file.
        write(home / rel, body)
        write(home / f".cache/note-{index}.txt", f"device fragment {index}\n")
        facts = [{"category": cat, "value": value, "path": f"home/{rel}", "quote": quote}]
        if extra_cat:
            facts.append({"category": extra_cat, "value": extra_val, "path": f"home/{rel}", "quote": quote})
        forbidden, title = [], f"Endpoint {value}"
    elif pol == "negative":
        write(home / ".bashrc", "alias ll='ls -la'\n")
        write(home / "Documents/todo.txt", f"Buy paper. Case {index}.\n")
        facts, forbidden, title = [], [], "Quiet home directory"
    else:
        write(home / "notes/travel-agent.txt", "Our travel agent booked the train. No coding agent is configured.\n")
        write(home / "web/theme.css", ".cursor { cursor: text; }\n")
        facts = []
        forbidden = [{"category": "agent", "value": "cursor"}, {"category": "agent", "value": "claude-code"}]
        title = "Home directory with prose and CSS"
    dump_truth(directory, base_truth("endpoint", index, title, facts, forbidden))


def emit_network(index: int, directory: Path) -> None:
    pol = polarity(index)
    hosts = [
        ("api.openai.com", "openai"),
        ("api.anthropic.com", "anthropic"),
        ("generativelanguage.googleapis.com", "google-gemini"),
        ("api.mistral.ai", "mistral"),
        ("api.groq.com", "groq"),
        ("api.cohere.ai", "cohere"),
        ("openrouter.ai", "openrouter"),
    ]
    if pol == "positive":
        host, provider = hosts[index % len(hosts)]
        row = {"ts": 1717200000 + index, "src_ip": f"10.1.0.{index + 1}", "query": host}
        write(directory / "dns.jsonl", json.dumps(row) + "\n")
        facts = [{"category": "egress", "value": provider, "path": "dns.jsonl", "quote": host}]
        forbidden, title = [], f"DNS query {host}"
    elif pol == "negative":
        row = {"ts": 1717200000, "src_ip": "10.1.0.4", "query": "login.microsoftonline.com"}
        write(directory / "dns.jsonl", json.dumps(row) + "\n")
        facts, forbidden, title = [], [], "DNS query for Microsoft login"
    else:
        row = {"ts": 1717200000, "src_ip": "10.1.0.9", "query": "bedrock.minecraft.net"}
        write(directory / "dns.jsonl", json.dumps(row) + "\n")
        facts = []
        forbidden = [{"category": "egress", "value": "aws-bedrock"}, {"category": "provider", "value": "aws-bedrock"}]
        title = "DNS query for a game host"
    dump_truth(directory, base_truth("network", index, title, facts, forbidden))


RUNTIME_POS = [
    ("claude", "/usr/bin/claude", "claude", "agent", "claude-code"),
    ("Claude", "/opt/Claude/claude", "/opt/Claude/claude", "agent", "claude-desktop"),
    ("cursor", "/usr/bin/cursor", "cursor .", "agent", "cursor"),
    ("ollama", "/usr/local/bin/ollama", "ollama serve", "local_model", "ollama"),
    ("gemini", "/usr/bin/gemini", "gemini", "agent", "gemini-cli"),
    ("codex", "/usr/bin/codex", "codex", "agent", "codex-cli"),
    ("windsurf", "/usr/bin/windsurf", "windsurf", "agent", "windsurf"),
    ("openclaw", "/usr/local/bin/openclaw", "openclaw", "agent", "openclaw"),
]


def emit_runtime(index: int, directory: Path) -> None:
    pol = polarity(index)
    if pol == "positive":
        name, path, cmd, cat, value = RUNTIME_POS[index % len(RUNTIME_POS)]
        row = [{"pid": 4000 + index, "name": name, "path": path, "cmdline": cmd, "username": "dev"}]
        write(directory / "processes.json", json.dumps(row, indent=2) + "\n")
        facts = [{"category": cat, "value": value, "path": "processes.json", "quote": cmd}]
        forbidden, title = [], f"Process {cmd}"
    elif pol == "negative":
        row = [{"pid": 80, "name": "nginx", "path": "/usr/sbin/nginx", "cmdline": "nginx: worker", "username": "www-data"}]
        write(directory / "processes.json", json.dumps(row, indent=2) + "\n")
        facts, forbidden, title = [], [], "nginx worker"
    else:
        row = [{"pid": 9, "name": "cursor-blink", "path": "/usr/bin/cursor-blink", "cmdline": "cursor-blink --demo", "username": "dev"}]
        write(directory / "processes.json", json.dumps(row, indent=2) + "\n")
        facts = []
        forbidden = [{"category": "agent", "value": "cursor"}]
        title = "Unrelated cursor-blink process"
    dump_truth(directory, base_truth("runtime", index, title, facts, forbidden))


EMITTERS = {
    "code": emit_code,
    "identity": emit_identity,
    "gateway": emit_gateway,
    "lowcode": emit_lowcode,
    "saas": emit_saas,
    "cloud": emit_cloud,
    "endpoint": emit_endpoint,
    "network": emit_network,
    "runtime": emit_runtime,
}


def corpus_hash() -> str:
    digest = hashlib.sha256()
    for truth in sorted(CORPUS.glob("*/*/truth.json")):
        digest.update(truth.relative_to(CORPUS).as_posix().encode())
        digest.update(b"\0")
        digest.update(truth.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def generate() -> dict:
    if CORPUS.exists():
        for child in sorted(CORPUS.glob("*/*")):
            if child.is_dir():
                for f in child.rglob("*"):
                    if f.is_file():
                        f.unlink()
    counts = {s: {"positive": 0, "negative": 0, "near_miss": 0} for s in SURFACES}
    for surface in SURFACES:
        for index in range(50):
            directory = CORPUS / surface / case_id(surface, index)
            EMITTERS[surface](index, directory)
            counts[surface][polarity(index)] += 1
    manifest = {
        "name": NAME,
        "version": "1.0.0",
        "seed": SEED,
        "cases": 450,
        "surfaces": list(SURFACES),
        "per_surface": counts,
        "formats": SURFACE_FORMAT,
        "provenance": "synthetic-realistic",
        "corpus_sha256": corpus_hash(),
        "label_rule": "Labels are the planted facts in truth.json. No evaluated tool produced them.",
    }
    write(CORPUS / "MANIFEST.json", json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    print(json.dumps(generate(), indent=2))
