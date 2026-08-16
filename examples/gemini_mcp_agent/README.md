# Gemini CLI + MCP Agent Example

Run gemini-cli in headless mode with the MS365 Graph MCP server.

## Setup

1. Copy `settings.json` to `~/.gemini/settings.json` inside the user's Docker container
2. Set the `MS365_ACCESS_TOKEN` env var (injected by your backend at process start)
3. Launch gemini-cli in headless mode

## Usage

```bash
# Backend injects the token and starts gemini-cli
export MS365_ACCESS_TOKEN="eyJ0eXAi..."
gemini --headless
```

## Token Flow

See [scope_handling.md](./scope_handling.md) for the full token lifecycle, refresh strategy, and scope management guide.

## Required Graph API Scopes

The following scopes should be requested during SSO login:

```
openid profile User.Read
Mail.Read Mail.ReadWrite Mail.Send
Calendars.Read Calendars.ReadWrite Calendars.Read.Shared
Team.ReadBasic.All TeamMember.Read.All
Channel.ReadBasic.All ChannelMessage.Read.All ChannelMessage.Send
Chat.Read ChatMessage.Read ChatMessage.Send
Sites.Read.All Files.Read
```

The MCP server validates token scopes on startup and disables tools whose required scopes are missing.
