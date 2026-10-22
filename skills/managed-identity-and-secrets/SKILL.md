---
name: managed-identity-and-secrets
description: Guides keyless authentication and least-privilege access for Azure AI workloads - managed identity and DefaultAzureCredential, data-plane RBAC roles for Azure OpenAI, AI Search and Storage, Key Vault for unavoidable secrets, and keeping secrets out of code, logs and prompts. Use when connecting a service to Azure resources, adding a credential, or reviewing auth configuration.
---

# Managed Identity and Secrets

## Overview

The safest secret is the one that doesn't exist. Azure AI services support Entra ID data-plane auth, so services
should authenticate with a **managed identity** and receive only the **data-plane roles** they need. Secrets that
must exist (third-party API keys) live in **Key Vault**, are fetched at runtime, and never enter prompts or logs.

## When to Use

- A new service, function, container or pipeline needs to call Azure OpenAI, AI Search, Storage, Cosmos DB, etc.
- Any code or config introduces an API key, connection string or token.
- Reviewing IaC role assignments.

## Process

1. **Use `DefaultAzureCredential`** in code (local dev resolves to `az login`; in Azure, to managed identity).
   Prefer a **user-assigned** managed identity for apps that need stable identity across redeployments.
2. **Assign data-plane roles, scoped to the resource**, not the subscription. Common minimums:

   | Need | Role |
   |---|---|
   | Call Azure OpenAI models | Cognitive Services OpenAI User |
   | Query an AI Search index | Search Index Data Reader |
   | Write documents to an index | Search Index Data Contributor |
   | Read blobs for ingestion | Storage Blob Data Reader |
   | Read a Key Vault secret | Key Vault Secrets User |

   Verify role names and scope with `microsoft-docs` for any service not listed.
3. **Disable local (key) auth** on resources that support it once every caller is keyless.
4. **Key Vault for the rest.** Reference secrets from app settings (Key Vault references) or fetch with the SDK;
   cache with a TTL; rotate. Never copy a secret into `.env` committed to git.
5. **Keep secrets out of model context.** Don't put credentials, connection strings or internal URLs in prompts,
   tool outputs or agent memory — models can repeat them.
6. **Scan.** Enable secret scanning and push protection on the repo (`secret-scanning` skill); add a pre-commit
   scanner for local defense.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "Contributor on the resource group is simpler" | It grants control-plane power the app never needs. Data-plane roles exist for this. |
| "The key is in a private repo" | Private repos get cloned, forked and leaked. Push protection exists because this keeps happening. |
| "Managed identity doesn't work locally" | `DefaultAzureCredential` falls back to your `az login` identity. Same code everywhere. |

## Red Flags

- `api_key=`, `AccountKey=`, `admin-key` or connection strings with secrets in code, IaC or `.env` in git.
- `Owner`/`Contributor` assigned to an application identity.
- Logging full request headers or exception messages that embed credentials.
- The same identity shared across unrelated services.

## Verification

- [ ] Code paths authenticate with a credential object, not a key (or the exception is documented).
- [ ] IaC assigns data-plane roles at resource scope; no Owner/Contributor for app identities.
- [ ] Key auth is disabled where all callers are keyless.
- [ ] Secret scanning/push protection is on; a scanner run over the diff is clean.
