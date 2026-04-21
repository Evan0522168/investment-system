from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import price, analysis, backtest

app = FastAPI(
    title="量化回測平台 API",
    description="策略回測與分析平台",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(price.router,     prefix="/price",     tags=["Price"])
app.include_router(analysis.router,  prefix="/analysis",  tags=["Analysis"])
app.include_router(backtest.router,  prefix="/backtest",  tags=["Backtest"])


@app.get("/")
@app.head("/")
def root():
    return {
        "message": "量化回測平台 API",
        "version": "2.0.0",
        "endpoints": ["/price", "/analysis", "/backtest"]
    }
"""from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import price, analysis, trade, portfolio

app = FastAPI(
    title="TWSE Stock Analyzer API",
    description="投資分析與模擬交易平台 API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(price.router, prefix="/price", tags=["Price"])
app.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
app.include_router(trade.router, prefix="/trade", tags=["Trade"])
app.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])


@app.get("/")
@app.head("/")
def root():
    return {
        "message": "TWSE Stock Analyzer API",
        "version": "1.0.0",
        "endpoints": ["/price", "/analysis", "/trade", "/portfolio"],
    }"""
