import ccxt
import pandas as pd
import time

# تنظیمات اولیه
api_key = 'YOUR_API_KEY'
secret_key = 'YOUR_SECRET_KEY'
exchange = ccxt.binance({
})
symbol = 'BTC/USDT'
timeframe = '1h'
position = None  # وضعیت معامله (None, 'long', 'short')

def fetch_data():
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
        return pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    except ccxt.NetworkError as e:
        print(f"Network error: {e}")
    except ccxt.ExchangeError as e:
        print(f"Exchange error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def calculate_indicators(df):
    df['sma'] = df['close'].rolling(window=14).mean()
    return df

def check_signals(df):
    global position
    latest_candle = df.iloc[-1]
    previous_candle = df.iloc[-2]

    # سیگنال خرید
    if previous_candle['close'] < previous_candle['sma'] and latest_candle['close'] > latest_candle['sma'] and position != 'long':
        position = 'long'
        print("سیگنال ورود: ورود به معامله خرید")
        exchange.create_market_buy_order(symbol, 0.001)  # مقدار را بر اساس نیاز خود تنظیم کنید

    # سیگنال فروش
    elif previous_candle['close'] > previous_candle['sma'] and latest_candle['close'] < latest_candle['sma'] and position != 'short':
        position = 'short'
        print("سیگنال خروج: خروج از معامله")
        exchange.create_market_sell_order(symbol, 0.001)  # مقدار را بر اساس نیاز خود تنظیم کنید

while True:
    data = fetch_data()
    if data is not None:
        data = calculate_indicators(data)
        check_signals(data)

    time.sleep(60)  # توقف برای یک دقیقه