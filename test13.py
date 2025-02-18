import requests
import pandas as pd
import time
import threading

api_key = '3be2dcc2-3f67-45db-8fbc-3f47d56e0027'  # کلید API خود را در اینجا قرار دهید
symbol = 'BTC'  # نماد ارز دیجیتال (BTC برای بیت‌کوین)
position = None  # وضعیت معامله (None, 'long', 'short')
prices = []  # لیست برای ذخیره قیمت‌ها

def fetch_price():
    url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol}&convert=USD'
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data['data'][symbol]['quote']['USD']['price']
    except Exception as e:
        print(f"Error: {e}")
    return None

def calculate_ma(prices, window):
    return pd.Series(prices).rolling(window=window).mean().iloc[-1]

def calculate_rsi(prices, window=14):
    delta = pd.Series(prices).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def calculate_macd(prices, short_window=12, long_window=26, signal_window=9):
    short_ema = pd.Series(prices).ewm(span=short_window, adjust=False).mean()
    long_ema = pd.Series(prices).ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_window, adjust=False).mean()
    return macd.iloc[-1], signal_line.iloc[-1]

def calculate_stochastic(prices, window=14):
    lowest_low = pd.Series(prices).rolling(window=window).min()
    highest_high = pd.Series(prices).rolling(window=window).max()
    stochastic_k = 100 * ((prices[-1] - lowest_low.iloc[-1]) / (highest_high.iloc[-1] - lowest_low.iloc[-1]))
    return stochastic_k

def calculate_bollinger_bands(prices, window=20, num_std=2):
    sma = calculate_ma(prices, window)
    std = pd.Series(prices).rolling(window=window).std().iloc[-1]
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    return upper_band, lower_band

def collect_prices():
    while True:
        price = fetch_price()
        if price is not None:
            prices.append(price)
            if len(prices) > 30:
                prices.pop(0)
            print(f"قیمت جدید اضافه شد: {price}")
        time.sleep(60)

def generate_signals():
    global position
    while True:
        if len(prices) >= 30:
            short_ma = calculate_ma(prices, window=10)
            long_ma = calculate_ma(prices, window=30)
            latest_price = prices[-1]

            if len(prices) >= 14:
                rsi = calculate_rsi(prices)

                if len(prices) >= 26:
                    macd, signal_line = calculate_macd(prices)

                stochastic_k = calculate_stochastic(prices)

                if len(prices) >= 20:
                    upper_band, lower_band = calculate_bollinger_bands(prices)

                    print(f"آخرین قیمت {symbol}: {latest_price}")
                    print(f"میانگین متحرک کوتاه‌مدت: {short_ma}")
                    print(f"میانگین متحرک بلندمدت: {long_ma}")
                    print(f"RSI: {rsi}")
                    print(f"MACD: {macd}, خط سیگنال: {signal_line}")
                    print(f"Stochastic K: {stochastic_k}")
                    print(f"باند بولینگر: بالا = {upper_band}, پایین = {lower_band}")
                    print(f"وضعیت فعلی: {position}")

                    # سیگنال خرید
                    if (short_ma > long_ma and rsi < 30 and latest_price <= lower_band and position != 'long'):
                        position = 'long'
                        print("سیگنال خرید: ورود به معامله خرید")

                    # سیگنال فروش
                    elif (short_ma < long_ma and rsi > 70 and latest_price >= upper_band and position != 'short'):
                        position = 'short'
                        print("سیگنال فروش: خروج از معامله")

        time.sleep(3600)

# شروع جمع‌آوری قیمت‌ها
price_thread = threading.Thread(target=collect_prices)
price_thread.start()

# تولید سیگنال‌ها
generate_signals()