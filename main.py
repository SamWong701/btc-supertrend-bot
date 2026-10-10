import time
import requests
import pandas as pd

print("Supertrend Bot Starting... No Telegram Version", flush=True)

# 簡單攞BTC價 + Supertrend logic (唔使任何Token)
def get_btc_data():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=100"
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=['open_time','open','high','low','close','vol','close_time','qav','trades','taker_base','taker_quote','ignore'])
    df['close'] = df['close'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    return df

while True:
    try:
        df = get_btc_data()
        price = df['close'].iloc[-1]
        print(f"BTC Price: {price} - Bot is running OK", flush=True)
        time.sleep(60)
    except Exception as e:
        print(f"Error: {e}, retry in 10s", flush=True)
        time.sleep(10)
