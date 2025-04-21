from flask import Flask, jsonify
from nsepython import nse_eq
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allows Flutter (different origin) to call this API

@app.route("/price/<symbol>")
def get_price(symbol):
    try:
        data = nse_eq(symbol.upper())
        ltp = float(data["priceInfo"]["lastPrice"])
        return jsonify({"symbol": symbol.upper(), "ltp": ltp})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Example: /prices?symbols=TCS,INFY,RELIANCE
@app.route("/prices")
def get_prices():
    symbols = ["TCS", "INFY", "RELIANCE"]
    prices = {}
    for sym in symbols:
        try:
            data = nse_eq(sym)
            prices[sym] = float(data["priceInfo"]["lastPrice"])
        except:
            prices[sym] = None
    return jsonify(prices)

if __name__ == "__main__":
    app.run(debug=True)

