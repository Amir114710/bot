import requests
import pandas as pd
import time
import threading

api_key = 'YOUR_API_KEY'  # کلید API خود را در اینجا قرار دهید
symbol = 'BTC'  # نماد ارز دیجیتال (BTC برای بیت‌کوین)
position = None  # وضعیت معامله (None, 'long', 'short')
prices = []  # لیست برای ذخیره قیمت‌ها

# تابع برای دریافت قیمت فعلی از CoinMarketCap
def fetch_price():
    url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol={symbol}&convert=USD'
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # بررسی وضعیت پاسخ
        data = response.json()
        return data['data'][symbol]['quote']['USD']['price']  # قیمت فعلی
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

# تابع برای محاسبه میانگین متحرک
def calculate_ma(prices, window):
    return pd.Series(prices).rolling(window=window).mean().iloc[-1]

# تابع برای محاسبه RSI
def calculate_rsi(prices, window=14):
    delta = pd.Series(prices).diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

# تابع برای محاسبه MACD
def calculate_macd(prices, short_window=12, long_window=26, signal_window=9):
    short_ema = pd.Series(prices).ewm(span=short_window, adjust=False).mean()
    long_ema = pd.Series(prices).ewm(span=long_window, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span=signal_window, adjust=False).mean()
    return macd.iloc[-1], signal_line.iloc[-1]

# تابع برای محاسبه Stochastic Oscillator
def calculate_stochastic(prices, window=14):
    lowest_low = pd.Series(prices).rolling(window=window).min()
    highest_high = pd.Series(prices).rolling(window=window).max()
    stochastic_k = 100 * ((prices[-1] - lowest_low.iloc[-1]) / (highest_high.iloc[-1] - lowest_low.iloc[-1]))
    return stochastic_k

# تابع برای محاسبه باند بولینگر
def calculate_bollinger_bands(prices, window=20, num_std=2):
    sma = calculate_ma(prices, window)
    std = pd.Series(prices).rolling(window=window).std().iloc[-1]
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    return upper_band, lower_band

# تابع برای جمع‌آوری قیمت‌ها
def collect_prices():
    while len(prices) < 30:
        price = fetch_price()
        if price is not None:
            prices.append(price)
            print(f"قیمت جدید اضافه شد: {price}")
        time.sleep(60)  # هر ۱ دقیقه یک‌بار قیمت جدید بگیرید

# تابع برای تولید سیگنال‌ها
def generate_signals():
    global position  # استفاده از متغیر جهانی
    while True:
        if len(prices) >= 30:
            short_ma = calculate_ma(prices, window=10)  # میانگین متحرک کوتاه‌مدت
            long_ma = calculate_ma(prices, window=30)   # میانگین متحرک بلندمدت
            latest_price = prices[-1]  # آخرین قیمت

            # محاسبه RSI
            if len(prices) >= 14:
                rsi = calculate_rsi(prices)  # محاسبه RSI

                # محاسبه MACD
                if len(prices) >= 26:
                    macd, signal_line = calculate_macd(prices)

                # محاسبه Stochastic
                stochastic_k = calculate_stochastic(prices)

                # محاسبه باند بولینگر
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
                    if (short_ma > long_ma and rsi < 30 and latest_price <= lower_band and macd > signal_line and stochastic_k < 20 and position != 'long'):
                        position = 'long'
                        print("سیگنال خرید: ورود به معامله خرید")

                    # سیگنال فروش
                    elif (short_ma < long_ma and rsi > 70 and latest_price >= upper_band and macd < signal_line and stochastic_k > 80 and position != 'short'):
                        position = 'short'
                        print("سیگنال فروش: خروج از معامله")

        time.sleep(3600)  # توقف برای ۱ ساعت (۳۶۰۰ ثانیه)

# شروع جمع‌آوری قیمت‌ها
price_thread = threading.Thread(target=collect_prices)
price_thread.start()

# تولید سیگنال‌ها
generate_signals()