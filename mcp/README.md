# Recommended MCP servers

MCP servers that skills in this pack rely on (`microsoft-docs` uses Microsoft Learn; `llm-red-teaming`,
`code-review-llm-apps` and browser work use GitHub, Playwright and Chrome DevTools). `servers.example.json` uses the
`mcpServers` layout read by most MCP clients (Claude Desktop/Code, Cursor, VS Code and others); copy the
entries you want into your client's config. All servers are opt-in - nothing here runs by default.

| Server | Package / image (verified 2026-10-22) | Needs |
|---|---|---|
| [Microsoft Learn](https://learn.microsoft.com/training/support/mcp) | Remote, streamable HTTP: `https://learn.microsoft.com/api/mcp` | Nothing - no authentication |
| [GitHub](https://github.com/github/github-mcp-server) | `ghcr.io/github/github-mcp-server` (Docker) | `GITHUB_PERSONAL_ACCESS_TOKEN` in your shell |
| [Playwright](https://github.com/microsoft/playwright-mcp) | `@playwright/mcp@0.0.83` | Node 18+ |
| [Chrome DevTools](https://github.com/ChromeDevTools/chrome-devtools-mcp) | `chrome-devtools-mcp@1.11.0` | Node 20.19+ and Chrome |
| [Context7](https://github.com/upstash/context7) | `@upstash/context7-mcp@4.4.4` | Node 20.18+; sends library queries to Context7's hosted service |

## Security notes

- **Secrets stay in your environment.** The GitHub entry passes `-e GITHUB_PERSONAL_ACCESS_TOKEN` with no value,
  so Docker forwards it from your shell. Never paste a token into the JSON.
- **Least privilege.** Use a fine-grained GitHub token scoped to the repositories and permissions the agent
  actually needs (read-only unless you want it to open PRs).
- **Versions are pinned** so a compromised or breaking upstream release isn't pulled in silently. Bump them
  deliberately after reading release notes.
- **Treat tool output as untrusted.** Browser and GitHub servers return web pages, issues and comments that can
  carry prompt-injection text. Keep human approval on for write actions.
- The reference servers in `modelcontextprotocol/servers` are examples, not hardened products - don't expose
  them over the network.
