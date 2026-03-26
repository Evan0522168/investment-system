from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    print("\n=== ROOT ===")
    print(r.json())


def test_price(stock_id="2330"):
    r = client.get(f"/price/{stock_id}")
    print(f"\n=== PRICE: {stock_id} ===")
    print(r.json())


def test_history(stock_id="2330", days=5):
    r = client.get(f"/price/{stock_id}/history?days={days}")
    print(f"\n=== HISTORY: {stock_id} (last {days} days) ===")
    print(r.json())


def test_analysis(stock_id="2330"):
    r = client.get(f"/analysis/{stock_id}")
    print(f"\n=== ANALYSIS: {stock_id} ===")
    print(r.json())


def test_portfolio():
    r = client.get("/portfolio/")
    print("\n=== PORTFOLIO ===")
    print(r.json())


def test_trade():
    r = client.post("/trade/execute", json={
        "stock_id": "2330",
        "shares": 100,
        "price": 780.0,
        "action": "buy"
    })
    print("\n=== TRADE (BUY) ===")
    print(r.json())


if __name__ == "__main__":
    test_root()
    test_price()
    test_history()
    test_analysis()
    test_portfolio()
    test_trade()
