from flask import Flask, jsonify
import yfinance as yf
from flask_cors import CORS
import os  # ✅ this should be at the top

app = Flask(__name__)
CORS(app)  # allows Flutter (different origin) to call this API

@app.route("/price/<symbol>")
def get_price(symbol):
    try:
        # Fetch the data for the symbol using yfinance
        stock = yf.Ticker(symbol.upper())
        data = stock.history(period="1d")  # Get latest data
        ltp = float(data["Close"].iloc[-1])  # Latest price (close price for the day)
        return jsonify({"symbol": symbol.upper(), "ltp": ltp})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/prices")
def get_prices():
    symbols = ["TCS", "INFY", "RELIANCE"]
    prices = {}
    for sym in symbols:
        try:
            # Fetch the data for the symbol using yfinance
            stock = yf.Ticker(sym)
            data = stock.history(period="1d")
            prices[sym] = float(data["Close"].iloc[-1])
        except:
            prices[sym] = None
    return jsonify(prices)



# ✅ Only one main block, correctly indented
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
