import os
import time
import requests
from binance.client import Client

print("=== 長揸大額現貨 Bot 啟動 ===")

# 印IP，等下加去Binance白名單
try:
    ip = requests.get("https://api.ipify.org", timeout=10).text
    print(f"MY RAILWAY IP IS: {ip} - 去Binance API管理加白名單!")
except Exception as e:
    print(f"印唔到IP: {e}")

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
SYMBOL = "BTCUSDT"
print(f"KEY Check: API_KEY={bool(API_KEY)} SECRET={bool(API_SECRET)}")

# 如果冇Key，唔好exit，一直loop等你Set返
if not API_KEY or not API_SECRET:
    while True:
        print("ERROR: BINANCE_API_KEY / SECRET 未Set! 去Railway -> Variables 加返! 10秒後重試...")
        time.sleep(10)

client = Client(API_KEY, API_SECRET)
print("Binance Client 連接成功")

def get_signal():
    # 你之後換返Supertrend邏輯
    return "HOLD"

while True:
    try:
        usdt = float(client.get_asset_balance(asset='USDT')['free'])
        btc = float(client.get_asset_balance(asset='BTC')['free'])
        price = float(client.get_symbol_ticker(symbol=SYMBOL)['price'])
        signal = get_signal()
        print(f"[{time.strftime('%H:%M:%S')}] 訊號:{signal} 價:{price} USDT:{usdt:.2f} BTC:{btc:.5f}")

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
