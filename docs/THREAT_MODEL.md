# Threat Model

## Assets
- User credentials and tokens.
- Conversation content.
- API keys and deployment secrets.

## Actors
- Anonymous internet users.
- Authenticated users.
- Malicious users and bots.

## Key Threats
- Credential theft and token replay.
- Data exposure from weak endpoint auth.
- Prompt injection and model abuse.
- Infrastructure misconfiguration.

## Mitigations
- Harden auth boundaries and rate limits.
- Restrict CORS and enforce HTTPS.
- Add moderation and output policy checks.
- Adopt secrets manager and audit logs.
