# TradingAgents Research Bridge (prototype)

This is a research-only FastAPI wrapper around the original TauricResearch/TradingAgents. It **does not** place brokerage orders. The original framework may simulate trading decisions; treat these as research, not recommendations.

## Deploy
1. Choose a Docker-capable Python hosting service. Check current free-tier availability; it is **not guaranteed**.
2. Upload these files to a private Git repository or host's source upload. Do not upload API keys.
3. Configure host **secrets**: `GOOGLE_API_KEY` (from Google AI Studio), `BRIDGE_TOKEN` (a long random secret). Optional: `GEMINI_MODEL`.
4. Deploy the Dockerfile and expose port `7860` over HTTPS.
5. Test `GET /health`; then `POST /analyze` with an Authorization header `Bearer <BRIDGE_TOKEN>` and JSON `{"ticker":"NVDA","analysis_date":"2026-09-01"}`.
6. Verify actual Gemini model availability, market-data requirements, provider quotas, and the installed TradingAgents configuration before relying on results.

## Security and limitations
- This is a **prototype, untested in a live host**. No deployment, endpoint, or ChatGPT tool connection has been completed.
- Use private environment secrets and HTTPS; never put the token in a public plugin package or screenshot.
- `/health` is public but reveals no credentials. `/analyze` requires a bearer token.
- Long synchronous jobs may exceed free host HTTP timeouts. For production, use a job queue and status polling, persistence, rate limiting, and authenticated admin controls.
- A ChatGPT plugin **skill alone** cannot invoke this API. A supported connector/tool integration must be created separately, and its availability depends on platform support.
- Do not enable real-money trading, broker credentials, or order-execution routes.
- The exact number of active agents depends on upstream TradingAgents configuration and analyst selection; this wrapper does not independently verify 11 active agents.
