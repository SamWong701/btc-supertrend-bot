import time
import requests
import pandas as pd
from flask import Flask
import os
import threading

# 建立一個極簡的 Web 伺服器給 Railway 做 Healthcheck
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

print("Supertrend Bot Starting... Web + Loop Version", flush=True)

def get_btc_data():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=100"
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=['open_time','open','high','low','close','vol','close_time','qav','trades','taker_base','taker_quote','ignore'])
    df['close'] = df['close'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    return df

def bot_loop():
    while True:
        try:
            df = get_btc_data()
            price = df['close'].iloc[-1]
            print(f"BTC Price: {price} - Bot is running OK", flush=True)
            time.sleep(60)
        except Exception as e:
            print(f"Error: {e}, retry in 10s", flush=True)
            time.sleep(10)

if __name__ == '__main__':
    # 用獨立執行緒（Thread）同時跑網頁伺服器同埋交易循環
    t = threading.Thread(target=bot_loop)
    t.daemon = True
    t.start()
    
    # 啟動 Flask 伺服器應付 Railway 檢查
    run_flask()
