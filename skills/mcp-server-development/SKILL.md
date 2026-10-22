---
name: mcp-server-development
description: Guides building a Model Context Protocol server that exposes internal tools or data to Copilot and other agents - scoping tools, typed schemas, transport and auth choices, least privilege, output limits, testing with an MCP client, and a security review before sharing. Use when creating or extending an MCP server in Python (FastMCP or the official SDK) or another language.
---

# MCP Server Development

## Overview

An MCP server turns your systems into tools any MCP client (Copilot, VS Code agent mode, Claude, Foundry agents)
can call. That makes it an API with an unusually creative caller: the model. Design small, typed, read-first
tools, authenticate remote transports, cap outputs, and review security before anyone else connects.

## When to Use

- Exposing an internal API, database, docs or workflow to agents.
- Adding tools/resources/prompts to an existing MCP server.
- NOT for consuming third-party MCP servers — vet those with `mcp-implementation-security-review`.

## Process

1. **Scope tools from user tasks.** List the 3–7 tasks agents need; design one tool per task with a precise name
   and description. Avoid a generic `run_query(sql)` style tool.
2. **Pick the stack.** Python: **FastMCP** (Apache-2.0, now v4) or the official `mcp` Python SDK. .NET:
   the `dotnet-mcp-builder` guidance in awesome-copilot or the official C# SDK. Minimal FastMCP server
   (verified against the README, 2026-10-22):

   ```python
   from fastmcp import FastMCP

   mcp = FastMCP("orders")

   @mcp.tool
   def get_order_status(order_id: str) -> dict:
       """Return status and ETA for one order the caller is allowed to see."""
       ...

   if __name__ == "__main__":
       mcp.run()            # stdio by default; use streamable HTTP for remote servers
   ```

3. **Type and validate everything.** Typed parameters (the schema is generated from them), validate formats and
   ranges in code, reject unexpected input. Return structured results with bounded size (paginate, truncate with a
   marker).
4. **Choose transport and auth.**
   - **stdio** for local, per-user tools (inherits the user's environment; no network exposure).
   - **Streamable HTTP** for shared/remote servers — require OAuth/Entra ID; validate tokens and audience on every
     request; never accept unauthenticated calls on a network interface.
5. **Least privilege.** The server's identity gets only the permissions its tools need; write tools are separate,
   clearly named and documented as side-effecting so clients can require approval. Enforce per-caller authorization
   inside each tool.
6. **Treat inputs and your own outputs as untrusted.** Tool arguments come from a model that may be
   prompt-injected; returned content may carry instructions into the next model call. Don't echo secrets, internal
   hostnames or stack traces.
7. **Test.** Unit-test tool functions directly; integration-test through an MCP client (in-memory client or
   `mcp dev`/inspector) including invalid arguments and unauthorized callers.
8. **Review before sharing.** Run the `mcp-implementation-security-review` skill and fix findings. Pin dependency
   versions and publish with a changelog.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "One flexible `execute` tool is simpler" | It's an injection surface and the model misuses it. Narrow tools are safer and more accurate. |
| "It's internal, auth can wait" | A local HTTP port is reachable by other processes and, often, the network. |
| "The client will ask before calling write tools" | Some clients auto-approve. Enforce authorization server-side. |
| "Return the whole record, the model can pick" | Large outputs burn context and leak fields. Return what the task needs. |

## Red Flags

- Tools accepting raw SQL, shell commands, file paths or URLs without allowlists.
- HTTP transport bound to `0.0.0.0` without authentication.
- One service principal with broad write access behind every tool.
- Unbounded list/search results; stack traces returned as tool output.

## Verification

- [ ] Each tool has a typed schema, input validation and a size-bounded result (tests for invalid input).
- [ ] Remote transport requires and validates tokens (test: unauthenticated call rejected).
- [ ] Write tools are separate, documented as side-effecting, and authorized per caller.
- [ ] Integration test exercises the server through an MCP client.
- [ ] `mcp-implementation-security-review` was run and its findings addressed.
