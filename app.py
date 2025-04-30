from flask import Flask, jsonify
from flask_cors import CORS
import os
import json
import requests

app = Flask(__name__)
CORS(app)

# Your actual Google Apps Script endpoint
GAS_BASE_URL = "https://script.google.com/macros/s/AKfycbyIOipbHQFC5egIqqdbnmbFaNwjHRVpRclP1g-ms9YOoVi4ssR9bUUfO75UkBDKh92c1Q/exec"

@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to Stock API!",
        "routes": ["/price/<symbol>", "/prices/nifty50", "/prices/nifty500"]
    })

@app.route("/price/<symbol>")
def get_price(symbol):
    try:
        response = requests.get(f"{GAS_BASE_URL}?symbol={symbol}")
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch from Google Apps Script"}), 500

        data = response.json()

        # If the result is a list, return the exact symbol match
        if isinstance(data, list):
            for item in data:
                if item.get("symbol", "").upper() == symbol.upper():
                    return jsonify(item)
            return jsonify({"error": f"No exact match found for {symbol}"}), 404

        # Single result case
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": f"Error fetching data for {symbol}: {str(e)}"}), 500

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
        symbols = raw_symbols  # Use raw symbols without appending .NS
    except Exception as e:
        return jsonify({"error": f"Error loading symbols: {str(e)}"}), 500

    prices = {}

    for sym in symbols:
        try:
            response = requests.get(f"{GAS_BASE_URL}?symbol={sym}")
            if response.status_code == 200:
                res_data = response.json()
                if isinstance(res_data, list):
                    match = next((item for item in res_data if item.get("symbol", "").upper() == sym.upper()), None)
                    prices[sym] = match or {"companyName": "Not Available", "price": None}
                else:
                    prices[sym] = res_data
            else:
                prices[sym] = {"companyName": "Not Available", "price": None}
        except Exception:
            prices[sym] = {"companyName": "Not Available", "price": None}

    return jsonify(prices)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
