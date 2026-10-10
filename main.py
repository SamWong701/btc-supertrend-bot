import os, time, threading, requests
import pandas as pd
from flask import Flask

# --- 1. Railway 防斷線心跳 ---
app = Flask(__name__)
@app.route('/')
def home(): return "Spot $5000 5% Re-Harvest Running"

print(f"=== 現貨 $5000 | 5%食盡重複收割啟動 ===", flush=True)

def run_web():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
threading.Thread(target=run_web, daemon=True).start()

# --- 2. 策略參數 ---
CAPITAL = 5000
BIG_WAVE_PCT = 5.0
LOCK_FALL_PCT = 2.0
SYMBOL = "BTCUSDT"
INTERVAL = "1h"
EMA_PERIOD = 20

def get_df():
    url = f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval={INTERVAL}&limit=200"
    r = requests.get(url, timeout=10).json()
    df = pd.DataFrame(r, columns=['t','o','h','l','c','v','ct','qav','tbv','tb','tq','i'])
    for c in ['o','h','l','c','v']:
        df[c] = df[c].astype(float)
    return df

def calc(df):
    df['ema20'] = df['c'].ewm(span=EMA_PERIOD, adjust=False).mean()
    df['ema20_slope'] = df['ema20'].diff(3)
    df['true_range'] = pd.concat([
        df['h'] - df['l'],
        (df['h'] - df['c'].shift()).abs(),
        (df['l'] - df['c'].shift()).abs()
    ], axis=1).max(axis=1)
    df['atr'] = df['true_range'].rolling(10).mean()
    df['atr_avg'] = df['atr'].rolling(50).mean()
    df['vol_avg'] = df['v'].rolling(20).mean()
    return df

in_pos = False
buy_price = highest = confirm = 0

while True:
    try:
        df = calc(get_df())
        price = df['c'].iloc[-1]
        ema20 = df['ema20'].iloc[-1]
        slope = df['ema20_slope'].iloc[-1]
        atr, atr_avg = df['atr'].iloc[-1], df['atr_avg'].iloc[-1]
        vol, vol_avg = df['v'].iloc[-1], df['vol_avg'].iloc[-1]

        vol_expand = atr > atr_avg * 1.4
        big_vol = vol > vol_avg * 1.8
        cond = (price > ema20) and vol_expand and big_vol and (slope > 0)

        if not in_pos:
            confirm = confirm + 1 if cond else 0
            print(f"觀望 | 價:{price:.0f} | EMA20:{ema20:.0f} | 擴張:{vol_expand} 量爆:{big_vol} | 確認 {confirm}/2", flush=True)

            if confirm >= 2:
                in_pos, buy_price, highest, confirm = True, price, price, 0
                print(f">>> ✅ 買入訊號觸發！模擬下單 ${CAPITAL} @ {price:.0f}", flush=True)
                print(f">>> 目標 +{BIG_WAVE_PCT}% = ${price*(1+BIG_WAVE_PCT/100):.0f} | 回落 {LOCK_FALL_PCT}% 鎖定", flush=True)
        else:
            if price > highest: highest = price
            profit_pct = (price - buy_price) / buy_price * 100
            fall_pct = (highest - price) / highest * 100
            print(f"持倉 | 入:{buy_price:.0f} 現:{price:.0f} | 賺:{profit_pct:.2f}% | 最高:{highest:.0f} 回落:{fall_pct:.2f}%", flush=True)

            if profit_pct >= BIG_WAVE_PCT and fall_pct >= LOCK_FALL_PCT:
                earn = CAPITAL * profit_pct / 100
                in_pos, buy_price, highest = False, 0, 0
                print(f">>> 💰 鎖定賣出 @ {price:.0f} | 獲利 +{profit_pct:.2f}% 賺取 ${earn:.2f}", flush=True)

        time.sleep(300)
    except Exception as e:
        print(f"Error: {e}", flush=True)
        time.sleep(30)
