# Third-party notices

## github/awesome-copilot

The following skills are copied without modification from
[github/awesome-copilot](https://github.com/github/awesome-copilot) at commit
`26f4f4581b92775543e4cddda21dd1d1b296db2e`, under the MIT License (full text in
[vendor/LICENSE-awesome-copilot.txt](vendor/LICENSE-awesome-copilot.txt)). Per-file SHA-256 hashes are recorded in
[vendor/skills.lock.json](vendor/skills.lock.json). `appinsights-instrumentation` also carries its own
`LICENSE.txt`.

- `skills/agent-owasp-compliance`
- `skills/appinsights-instrumentation`
- `skills/github-actions-hardening`
- `skills/mcp-implementation-security-review`
- `skills/microsoft-agent-framework`
- `skills/microsoft-docs`
- `skills/secret-scanning`
- `skills/semantic-kernel`

Reviewed but **not** imported: `eval-driven-dev` (its setup script re-downloads the skill from upstream at run time,
defeating pinning, and installs a third-party package and background web server) and `azure-role-selector` (too
thin to add value over `managed-identity-and-secrets`).

## Inspiration

Skill structure follows the anatomy documented in
[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) (MIT). No skill content is copied from it.
