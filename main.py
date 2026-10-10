import os
import time
from binance.client import Client
from binance.exceptions import BinanceAPIException

# --- 1. 讀取環境變數與初始化 ---
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
SYMBOL = "BTCUSDT"

if not API_KEY or not API_SECRET:
    print("Error: BINANCE_API_KEY 或 BINANCE_API_SECRET 未設定！請去 Railway Variables 介面加回！")
    time.sleep(10)
    exit(1)

# 初始化幣安客戶端（正式主網）
client = Client(API_KEY, API_SECRET)

def get_signal():
    """
    請在此處實現你的 Supertrend / EMA 策略邏輯。
    目前預設為示範，回傳 'HOLD'、'BUY' 或 'SELL'。
    """
    # 範例邏輯：你可以替換為你的 Pine Script 邏輯或技術指標計算
    return "HOLD"

print("=== 長渣大額現貨 Bot 啟動成功 ===")

# --- 2. 主循環（每小時檢查一次） ---
while True:
    try:
        # 取得帳戶餘額
        usdt_balance = float(client.get_asset_balance(asset='USDT')['free'])
        btc_balance = float(client.get_asset_balance(asset='BTC')['free'])
        
        # 取得當前 BTC 價格
        ticker = client.get_symbol_ticker(symbol=SYMBOL)
        price = float(ticker['price'])
        
        # 取得交易信號
        signal = get_signal()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 訊號: {signal} | 價錢: {price} | USDT: {usdt_balance:.2f} | BTC: {btc_balance:.4f}")

        # --- 3. 買入邏輯（長渣大額：使用可用 USDT 的 95% 買入） ---
        if signal == "BUY" and usdt_balance > 20:
            # 計算可買入的 USDT 金額（保留 5% 作手續費緩衝）
            quote_qty = round(usdt_balance * 0.95, 2)
            order = client.order_market_buy(symbol=SYMBOL, quoteOrderQty=quote_qty)
            print(f"買入成功！成交詳情: {order}")

        # --- 4. 賣出邏輯（當持倉 BTC 價值大於 20 USDT 時全數清倉） ---
        elif signal == "SELL" and (btc_balance * price) > 20:
            # 幣安 BTC 通常精確到小數後 5 位（視乎 LOT_SIZE 而定）
            quantity = round(btc_balance, 5)
            order = client.order_market_sell(symbol=SYMBOL, quantity=quantity)
            print(f"賣出成功！成交詳情: {order}")
            
        else:
            print("目前條件未達成，不作操作。")

    except BinanceAPIException as e:
        print(f"幣安 API 錯誤: {e}")
    except Exception as e:
        print(f"發生未預期的錯誤: {e}")

    # 每小時（3600秒）檢查一次，適合長渣策略
    time.sleep(3600)
