import os
import re
import secrets
import threading
from datetime import date
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title='TradingAgents Research Bridge', version='0.1.0')
_lock = threading.Lock()

class ResearchRequest(BaseModel):
    ticker: str
    analysis_date: date

@app.get('/health')
def health():
    return {'status': 'ok', 'mode': 'research_only', 'engine_configured': bool(os.getenv('GOOGLE_API_KEY'))}

@app.post('/analyze')
def analyze(request: ResearchRequest, authorization: str | None = Header(default=None)):
    expected = os.getenv('BRIDGE_TOKEN')
    if not expected or not authorization or not secrets.compare_digest(authorization, f'Bearer {expected}'):
        raise HTTPException(401, 'Unauthorized')
    ticker = request.ticker.strip().upper()
    if not re.fullmatch(r'[A-Z][A-Z0-9.\-]{0,11}', ticker):
        raise HTTPException(422, 'Invalid ticker')
    if request.analysis_date > date.today():
        raise HTTPException(422, 'Future date not allowed')
    if not os.getenv('GOOGLE_API_KEY'):
        raise HTTPException(503, 'GOOGLE_API_KEY missing')
    if not _lock.acquire(blocking=False):
        raise HTTPException(429, 'Another analysis is running')
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        config = DEFAULT_CONFIG.copy()
        config.update({
            'llm_provider': 'google',
            'quick_think_provider': 'google',
            'deep_think_provider': 'google',
            'quick_think_llm': os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'),
            'deep_think_llm': os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'),
            'max_debate_rounds': 1,
            'max_risk_discuss_rounds': 1,
        })
        graph = TradingAgentsGraph(debug=False, config=config)
        state, decision = graph.propagate(ticker, request.analysis_date.isoformat())
        return {'ticker': ticker, 'analysis_date': request.analysis_date.isoformat(), 'decision': str(decision), 'mode': 'research_only', 'note': 'No broker execution is implemented.'}
    except Exception as exc:
        # Do not expose provider keys or request internals in public responses.
        raise HTTPException(502, f'Analysis failed ({type(exc).__name__}); check server logs') from None
    finally:
        _lock.release()
