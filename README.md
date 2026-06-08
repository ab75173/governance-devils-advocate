# AI Governance Devil's Advocate — MCP Server

**Live endpoint:** `https://governance-devils-advocate.onrender.com/mcp` (Render free tier — first request after idle may take ~50s to cold-start).

A remote [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server that exposes structured AI-governance knowledge and decision-memo formatting to any MCP client (Claude Desktop, Claude Code, Cursor, VS Code with Copilot). When connected, it lets the calling LLM reason through proposed AI deployment scenarios by chaining tool calls across philosophical ethics frameworks and real-world AI governance frameworks: **NIST AI RMF**, **MITRE ATLAS**, and the **EU AI Act**.

Built for [SEAS 6413 (Cloud and Big Data Management, GW SEAS) Homework #1](#academic-context). Designed as a portfolio piece for forward-deployed engineering roles: the canonical MCP pattern an enterprise customer would adopt for internal governance tooling.

## Architectural principle

> The server provides **structured knowledge and formatting only**. The client LLM does all reasoning.

Tools return data, framework prompts, and templates — they do not generate arguments themselves. No external LLM calls from inside the server. Tools are deterministic given their inputs.

This is the canonical MCP design pattern. It is what makes the project reusable by an enterprise customer who wants to self-host the same architecture with their own proprietary frameworks and policies.

## Stack

- **Language:** Python 3.11+
- **MCP framework:** [FastMCP](https://github.com/jlowin/fastmcp)
- **Transport:** Streamable HTTP (per the 2025-03-26 MCP spec)
- **Deployment target:** [Render.com](https://render.com) free tier (GitHub-connected auto-deploy)
- **Public endpoint:** Single URL ending in `/mcp`

## Tools

| Tool | Purpose |
|---|---|
| `lookup_nist_ai_rmf(query)` | Surface NIST AI RMF (AI 100-1) and Generative AI Profile (AI 600-1) subcategories matching a free-text query. |
| `lookup_mitre_atlas(query)` | Surface MITRE ATLAS techniques and mitigations relevant to LLM-integrated systems. |
| `classify_eu_ai_act(scenario)` | Classify an AI deployment scenario into an EU AI Act risk tier and return regulatory obligations. |
| `get_ethical_framework(framework)` | Return a structured analytical scaffold for one of `utilitarian`, `deontological`, `virtue_ethics`, `care_ethics`, `rawlsian`. |
| `format_decision_memo(...)` | Render a clean Markdown decision memo from arguments the LLM has produced. |

## Quick start (local)

```bash
git clone https://github.com/ab75173/governance-devils-advocate.git
cd governance-devils-advocate
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m src.server
# Server starts on http://0.0.0.0:8000/mcp
```

Run the tests:

```bash
pip install -e ".[dev]"
pytest -v
```

## Connect from Claude Desktop

Add the server to your Claude Desktop MCP config. The remote-server form (Claude Desktop ≥ 2025):

```jsonc
{
  "mcpServers": {
    "governance-devils-advocate": {
      "url": "https://governance-devils-advocate.onrender.com/mcp"
    }
  }
}
```

For a local run during development, use the same form with `http://127.0.0.1:8000/mcp`.

Then in a Claude Desktop conversation, ask Claude to use the governance tools.

## Demo prompt

After connecting the server, paste this into Claude Desktop:

> I'm thinking about deploying an LLM-based system to triage incoming security alerts at a federal agency. Walk me through the governance considerations using the connected MCP tools.

Expected behavior: Claude chains the tools — `classify_eu_ai_act` (→ high-risk under Annex III) → `lookup_nist_ai_rmf` (governance, measurement, monitoring subcategories) → `lookup_mitre_atlas` (prompt injection, data leakage, tool compromise, mitigations) → `get_ethical_framework` (multiple, e.g. `utilitarian`, `deontological`, `care_ethics`, `rawlsian`) → `format_decision_memo`. The result is a complete decision memo with framework-grounded arguments for and against.

## Deploy to Render

1. Push this repo to GitHub.
2. In Render, **New → Blueprint** and point it at the repo. Render reads `render.yaml` and provisions the service.
3. Once the build is green, the public URL ends with `/mcp` — that's the MCP endpoint to connect from Claude Desktop.

`render.yaml` configures:
- `python -m src.server` as the start command
- `PORT` injected by Render, bound to `0.0.0.0`
- A health-check path at `/mcp/` (the FastMCP streamable HTTP endpoint)

## Project structure

```
governance-devils-advocate/
├── src/
│   ├── server.py              # FastMCP app entrypoint
│   ├── tools/
│   │   ├── nist_rmf.py
│   │   ├── mitre_atlas.py
│   │   ├── eu_ai_act.py
│   │   ├── ethics.py
│   │   └── memo.py
│   └── data/
│       ├── nist_ai_rmf.json
│       ├── mitre_atlas.json
│       ├── eu_ai_act_tiers.json
│       └── ethical_frameworks.json
├── tests/
│   └── test_tools.py
├── render.yaml
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Extending for your own organization (fork guide)

Everything an enterprise customer would want to swap lives in `src/data/`:

- **Replace the framework data.** Each tool reads a versioned JSON file. Drop in your proprietary control catalog (SOC 2, internal AI policy, sectoral rules) keeping the same shape.
- **Add a tier.** `eu_ai_act_tiers.json` is rule-based — add tiers or change the `classification_rules` to encode your own risk taxonomy.
- **Swap the ethics scaffolds.** `ethical_frameworks.json` is plain text; replace with whatever decision-making frameworks your organization actually uses (RACI, OODA, premortem, whatever).
- **Add tools sparingly.** Large tool surfaces destroy the calling LLM's context budget. Five is the design target.
- **Add OAuth 2.1.** This demo deployment has no auth. For production, follow the [MCP authorization spec](https://modelcontextprotocol.io/specification/draft/basic/authorization).

## Non-goals

- No web UI. The "demo" is via Claude Desktop or another MCP client adding the server URL.
- No LLM calls from inside the server — see the architectural principle above.
- No exhaustive encoding of every NIST/ATLAS/EU AI Act control. Curated enough for compelling demos with a documented data-loading pattern.
- No multi-agent debate framework. The agentic behavior lives on the client side via tool chaining.

## Academic context

Built as the deliverable for **SEAS 6413 (Cloud and Big Data Management, GW SEAS) Homework #1** under the prompt _"Build and chat with your own Agentic AI using Python and Google API Key,"_ substituting Anthropic's MCP stack and Claude API for the Google API Key path under the "come up with your own topic" clause. The chat happens inside any MCP-compatible client; this repo is the agent's tool surface.

## References

- [MCP specification](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [MITRE ATLAS](https://atlas.mitre.org/)
- [EU AI Act](https://artificialintelligenceact.eu/)

## License

MIT — see [LICENSE](LICENSE).
