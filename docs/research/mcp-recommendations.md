# MCP Servers for the Sierra Operator Stack

> Model Context Protocol servers worth installing into Claude Code (or
> Claude Desktop). Each entry: install command, env vars needed,
> Sierra-specific use case.

## Already installed in this session

- **GitHub MCP** — `mcp__github__*` tools. Reads/writes
  `dklein1123/ai-influencer`. Used for branch ops, commits, PRs.

## Top priority — install next

### Apify MCP
- **Repo:** [github.com/apify/actors-mcp-server](https://github.com/apify/actors-mcp-server)
- **Why:** Lets Claude pick + run Apify actors inline without our Python
  wrappers. Replaces ~30% of `tools/research/common.py`. Especially
  good for ad-hoc ("scrape @handle's last 50 posts and summarize") that
  doesn't justify a script.
- **Install (Claude Code):**
  ```bash
  claude mcp add apify -- npx -y @apify/actors-mcp-server
  ```
  Then add to `~/.claude.json` or the per-project `.mcp.json`:
  ```json
  {
    "mcpServers": {
      "apify": {
        "command": "npx",
        "args": ["-y", "@apify/actors-mcp-server"],
        "env": { "APIFY_TOKEN": "apify_api_..." }
      }
    }
  }
  ```

### Firecrawl MCP
- **Repo:** [github.com/mendableai/firecrawl-mcp-server](https://github.com/mendableai/firecrawl-mcp-server)
- **Why:** Same idea — scrape/search inline.
- **Install:**
  ```bash
  claude mcp add firecrawl -- npx -y firecrawl-mcp
  ```
  ```json
  {
    "mcpServers": {
      "firecrawl": {
        "command": "npx",
        "args": ["-y", "firecrawl-mcp"],
        "env": { "FIRECRAWL_API_KEY": "fc-..." }
      }
    }
  }
  ```

### Filesystem MCP
- **Repo:** [github.com/modelcontextprotocol/servers/tree/main/src/filesystem](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem)
- **Why:** Outside Claude Code's working dir, e.g. read-only access to
  the operator's Downloads folder for new reference photos, or to a
  side scratchpad. Already redundant inside this session.

### Brave Search MCP
- **Repo:** [github.com/modelcontextprotocol/servers/tree/main/src/brave-search](https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search)
- **Why:** Free SERP, conserves Firecrawl/Apify quota. Useful for
  pre-research (find candidate URLs) before scraping.
- **Get API key:** [brave.com/search/api](https://brave.com/search/api/)
  — free tier 2k queries/mo.
- **Install:**
  ```bash
  claude mcp add brave-search -- npx -y @modelcontextprotocol/server-brave-search
  ```

## Medium priority

### Higgsfield MCP
- **Status:** Already wired in this session per the env config.
- **Why:** Generate Sierra images directly from a Claude conversation.
  Good for ad-hoc; production runs still go through `tools/generation/`.

### Slack MCP
- **Repo:** [github.com/modelcontextprotocol/servers/tree/main/src/slack](https://github.com/modelcontextprotocol/servers/tree/main/src/slack)
- **Why:** When trend pulse or competitor tracker finds something
  urgent, post to an `#alerts` channel.
- **Install:**
  ```bash
  claude mcp add slack -- npx -y @modelcontextprotocol/server-slack
  ```
  Requires Slack bot token + signing secret.

### Notion MCP
- **Repo:** [github.com/makenotion/notion-mcp-server](https://github.com/makenotion/notion-mcp-server)
- **Why:** Skip if using Lovable portal. Use only if maintaining a
  parallel Notion workspace.

### Computer Use / Browser Use MCP
- **Repo:** [github.com/anthropic-experimental/browser-use-mcp-server](https://github.com/browser-use/browser-use)
- **Why:** Browser-controllable agent for sites with no API:
  - Threads (basic), BlueSky (until SDK matures), some IG flows.
  - Manually scheduling on Metricool when API would be overkill.
- **Install:** see repo README; needs Playwright + headed Chrome.

## Lower priority / situational

### Linear MCP
- Skip if using Lovable Tasks. Otherwise standard install.

### Sentry MCP
- Useful once we have production posting flows that can fail.

### PostgreSQL MCP
- Read access to the Lovable Supabase. Useful for ad-hoc analytics
  queries against the portal data without writing SQL by hand.
- **Install:**
  ```bash
  claude mcp add postgres -- npx -y @modelcontextprotocol/server-postgres "postgresql://..."
  ```
  Use the Supabase **read-only** connection string.

## How to validate an MCP is working

```bash
claude mcp list
# should show the server name + "connected" status
```

In a Claude Code session, type `/mcp` (if available) to see the loaded
servers and their tool counts.

## Where to put the config

- **Claude Code (this CLI):** `~/.claude.json` under `mcpServers`.
- **Claude Desktop (Mac/Windows app):** `~/Library/Application Support/
  Claude/claude_desktop_config.json` (Mac) or
  `%APPDATA%/Claude/claude_desktop_config.json` (Win).
- **Per-project:** `.mcp.json` in the repo root, committed (no secrets;
  reference env vars).

## Secret hygiene

MCP configs reference env vars (`$APIFY_TOKEN`, `$FIRECRAWL_API_KEY`).
Source from `~/.AI-Influencer.env` (mode 600, not committed) at
shell-init time:

```bash
# in ~/.zshrc / ~/.bashrc
set -a; source ~/.AI-Influencer.env; set +a
```

Then `claude` inherits the env. Never put raw keys in `.mcp.json`.
