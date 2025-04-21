from flask import Flask, jsonify
import yfinance as yf
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Root route (optional)
@app.route("/")
def index():
    return jsonify({"message": "Welcome to Stock Price API!"})

@app.route("/price/<symbol>")
def get_price(symbol):
    try:
        stock = yf.Ticker(symbol.upper())
        data = stock.history(period="1d")
        ltp = float(data["Close"].iloc[-1])
        return jsonify({"symbol": symbol.upper(), "ltp": ltp})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/prices")
def get_prices():
    symbols = ["TCS.NS", "INFY", "RELIANCE.NS"]
    prices = {}
    for sym in symbols:
        try:
            stock = yf.Ticker(sym)
            data = stock.history(period="1d")
            prices[sym] = float(data["Close"].iloc[-1])
        except:
            prices[sym] = None
    return jsonify(prices)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
