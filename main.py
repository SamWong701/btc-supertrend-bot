import os
import time
import requests
from binance.client import Client

# --- 1. 印IP，方便你去Binance加白名單 ---
try:
    ip = requests.get("https://api.ipify.org", timeout=5).text
    print(f"MY RAILWAY IP IS: {ip} - 請加去Binance白名單!")
except:
    print("印唔到IP")

# --- 2. 讀Key ---
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
SYMBOL = "BTCUSDT"

if not API_KEY or not API_SECRET:
    print("Error: BINANCE_API_KEY / SECRET 未Set！去Railway Variables度加！")
    # 唔好直接死，等佢重試
    time.sleep(10)

client = Client(API_KEY, API_SECRET)

def get_signal():
    try:
        klines = client.get_klines(symbol=SYMBOL, interval=Client.KLINE_INTERVAL_1DAY, limit=30)
        closes = [float(k[4]) for k in klines]
        ma20 = sum(closes[-20:]) / 20
        return "BUY" if closes[-1] > ma20 else "SELL"
    except Exception as e:
        print(f"get_signal Error: {e}")
        return "HOLD"

print("=== 長揸大額現貨 Bot 啟動 ===")

while True:
    try:
        usdt = float(client.get_asset_balance(asset='USDT')['free'])
        btc = float(client.get_asset_balance(asset='BTC')['free'])
        price = float(client.get_symbol_ticker(symbol=SYMBOL)['price'])
        signal = get_signal()
        print(f"訊號:{signal} 價:{price} USDT:{usdt} BTC:{btc}")

        if signal == "BUY" and usdt > 20:
            client.order_market_buy(symbol=SYMBOL, quoteOrderQty=round(usdt*0.95,2))
            print("買入成功")
        elif signal == "SELL" and btc*price > 20:
            client.order_market_sell(symbol=SYMBOL, quantity=round(btc,5))
            print("賣出成功")
        else:
            print("不操作")

    except Exception as e:
        print(f"Error: {e}")

    time.sleep(3600)
