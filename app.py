from flask import Flask, jsonify
import yfinance as yf
from flask_cors import CORS
import os
import json
import glob

app = Flask(__name__)
CORS(app)

@app.route("/prices/<index_name>")
def get_prices_by_index(index_name):
    index_map = {
        "nifty500": "data/nifty500.json",
        "nifty50": "data/nifty50.json"
    }

    file_path = index_map.get(index_name.lower())
    if not file_path or not os.path.exists(file_path):
        return jsonify({"error": "Invalid index name"}), 400

    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        raw_symbols = data.get("Nifty 500") or data.get("Nifty 50") or []
        symbols = [s if s.endswith(".NS") else s + ".NS" for s in raw_symbols]
    except Exception as e:
        return jsonify({"error": f"Error loading symbols: {str(e)}"}), 500

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
