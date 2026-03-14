# Microsoft 365 MCP Server — Token & Scope Handling

## Architecture Overview

```
User (browser)
  |
  |-- SSO login -> Microsoft Entra -> access token (delegated, user's scopes)
  |
  |-- Chat input -> your backend
  |                    |
  |                    |-- gemini-cli --headless
  |                    |       |
  |                    |       |-- MCP Server: ms365_graph (with user's token)
  |                    |       |-- MCP Server: (others?)
  |                    |       |
  |                    |       +-- Gemini processes, calls tools, responds
  |                    |
  |                    +-- streams response back to frontend
  |
  +-- sees response
```

## 1. Token Storage — Container Security

**Don't write the token to disk inside the container.** If the container is compromised or the volume is inspected, the token is exposed. Instead:

```
Frontend (SSO) -> Backend (holds tokens in memory/encrypted store)
                    |
                    |  docker exec / API call to set env var
                    |  OR pass as env at container start
                    v
                Docker container
                    |
                    |-- gemini-cli (headless)
                    |     +-- MCP server inherits env: MS365_ACCESS_TOKEN
                    |
                    +-- no token on disk anywhere
```

The token should live as a **process environment variable** only — set when you launch (or re-launch) the gemini-cli process inside the container. Your backend is the token broker; the container never persists it.

Since a Graph API access token lives ~1 hour and the user selects a workspace (which starts/resumes a session), the natural injection point is: **backend sets the env var when spawning/restarting the gemini-cli process for that workspace session.**

## 2. Token Refresh — Keep the User in the Loop, But Make It Seamless

**Architecture: backend holds refresh token, container only ever sees short-lived access tokens.**

```
User authenticates (SSO, browser)
    |
    v
Your backend receives:
    |-- access_token  (1 hour TTL)
    +-- refresh_token (stored encrypted, server-side only, NEVER in container)

Backend pushes access_token -> container env var
    |
    |  ... 50 minutes later ...
    |
Backend uses refresh_token to get new access_token
    (silent, no user interaction, standard OAuth2 refresh_token grant)
Backend pushes new access_token -> container
```

### Why this is safe

- The refresh token never leaves your backend — it's not in the container, not on disk, not in any MCP server process
- The access token is short-lived (1h) and scoped — even if the container is compromised, the blast radius is limited
- The refresh itself is a standard OAuth2 flow, no user interaction needed — Microsoft's own SDKs (MSAL) do this silently by default
- The user **was** involved: they consented at SSO login. The refresh token is just continuing that session

### When to force re-authentication (user involvement required)

- Refresh token itself expires (typically 24h-90 days depending on your Entra tenant policy)
- User revokes consent
- Conditional Access policy kicks in (MFA required, location change, etc.)

In those cases, your backend gets a 401 on the refresh attempt -> notify the frontend -> user re-authenticates. This is the standard pattern that Outlook, Teams, and every Microsoft app uses.

### What to avoid

**Do not** store the refresh token inside the container or have the MCP server itself do the refresh — that puts too much trust in the container.

## 3. Scopes — Request What You Need at SSO Time

Scopes are baked into the token at authentication time. The flow:

```
Frontend SSO login request:
    scope: "openid profile Mail.Read Mail.Send Calendars.ReadWrite
            Team.ReadBasic.All Chat.Read ChatMessage.Send
            Channel.ReadBasic.All ChannelMessage.Read.All ChannelMessage.Send
            Sites.Read.All Files.Read User.Read"
    |
    v
User sees consent screen listing these permissions -> approves
    |
    v
Token is minted with exactly these scopes
```

### Option A: Static scope set (simpler, recommended to start)

Your SSO login always requests the full set of scopes needed by all MCP servers the user could access. User consents once. Done.

### Option B: Incremental consent (better UX for many servers)

Login with minimal scopes (User.Read). When the user activates the M365 MCP server in their workspace, your frontend triggers an incremental consent prompt for the additional scopes. Microsoft Entra supports this natively — you just add the new scopes to the auth request and it only prompts for the ones not yet consented.

### Scope validation in the MCP server

As a safety net, the MCP server decodes the JWT access token on startup, reads the `scp` claim, and checks which scopes are present. Tools whose required scopes are missing are disabled and a warning is logged. This prevents confusing Graph API 403 errors at runtime.

## Summary

| Concern | Recommendation |
|---------|---------------|
| Token storage | Env var only, never disk. Backend is the token broker. |
| Token refresh | Backend holds refresh token, silently pushes new access tokens to container. Re-auth only when refresh token expires. |
| Scopes | Request full scope set at SSO login (option A). Add scope validation to the MCP server as a safety net. |
| Container security | Access token in env (1h TTL), no refresh token in container, no token on disk. |
