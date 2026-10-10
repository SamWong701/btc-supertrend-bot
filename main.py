import os, time, requests
import pandas as pd
from binance.client import Client

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
SYMBOL = "BTCUSDT"

client = Client(API_KEY, API_SECRET)

try:
    print("MY RAILWAY IP IS:", requests.get("https://ifconfig.me", timeout=5).text)
except: pass

def get_signal():
    klines = client.get_klines(symbol=SYMBOL, interval=Client.KLINE_INTERVAL_1DAY, limit=50)
    closes = [float(k[4]) for k in klines]
    ma20 = sum(closes[-20:])/20
    return "BUY" if closes[-1] > ma20 else "SELL"

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
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(3600)
