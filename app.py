from flask import Flask, jsonify
import yfinance as yf
from flask_cors import CORS
import os
import json
import glob

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return jsonify({"message": "Welcome to Stock Price API!"})

@app.route("/price/<symbol>")
def get_price(symbol):
    try:
        stock = yf.Ticker(symbol.upper())
        data = stock.history(period="1d")
        company_name = stock.info.get("longName", "Not Available")
        if data.empty:
            return jsonify({"error": "No data found for symbol"}), 404
        ltp = float(data["Close"].iloc[-1])
        return jsonify({
            "symbol": symbol.upper(),
            "companyName": company_name,
            "ltp": ltp
        })
    except Exception as e:
        return jsonify({"error": f"Error fetching data for {symbol}: {str(e)}"}), 500

@app.route("/prices")
def get_prices():
    all_symbols = []
    try:
        # Load all JSON files in the data/ directory
        for file_path in glob.glob("data/*.json"):
            with open(file_path, "r") as f:
                data = json.load(f)
                symbols = data.get("Nifty 500", [])
                all_symbols.extend(symbols)

        # Add .NS suffix if missing
        symbols = [sym if sym.endswith(".NS") else sym + ".NS" for sym in all_symbols]
    except Exception as e:
        return jsonify({"error": f"Error loading symbol files: {str(e)}"}), 500

    prices = {}
    for sym in symbols:
        try:
            stock = yf.Ticker(sym)
            data = stock.history(period="1d")
            company_name = stock.info.get("longName", "Not Available")
            prices[sym] = {
                "companyName": company_name,
                "price": float(data["Close"].iloc[-1]) if not data.empty else None
            }
        except:
            prices[sym] = {"companyName": "Not Available", "price": None}
    return jsonify(prices)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
