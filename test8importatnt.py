import requests
import pandas as pd
import numpy as np
import time

symbol = 'bitcoin'
position = None  # وضعیت معامله (None, 'long', 'short')
prices = []  # لیست برای ذخیره قیمت‌ها

# تابع برای دریافت داده‌های ساعتی
def fetch_hourly_data():
    url = f'https://api.coingecko.com/api/v3/coins/{symbol}/market_chart?vs_currency=usd&days=1'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['prices']
    else:
        print(f"Error fetching hourly data: {response.status_code} - {response.text}")
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

# تابع برای محاسبه باند بولینگر
def calculate_bollinger_bands(prices, window=20, num_std=2):
    sma = calculate_ma(prices, window)
    std = pd.Series(prices).rolling(window=window).std().iloc[-1]
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    return upper_band, lower_band

# حلقه اصلی
while True:
    hourly_data = fetch_hourly_data()
    if hourly_data is not None and len(hourly_data) > 0:
        prices = [price[1] for price in hourly_data]

        if len(prices) >= 30:
            short_ma = calculate_ma(prices, window=10)  # میانگین متحرک کوتاه‌مدت
            long_ma = calculate_ma(prices, window=30)   # میانگین متحرک بلندمدت
            latest_price = prices[-1]  # آخرین قیمت

            # محاسبه RSI
            if len(prices) >= 14:
                rsi = calculate_rsi(prices)  # محاسبه RSI
            
            # محاسبه باند بولینگر
            if len(prices) >= 20:
                upper_band, lower_band = calculate_bollinger_bands(prices)

                print(f"آخرین قیمت {symbol}: {latest_price}")
                print(f"میانگین متحرک کوتاه‌مدت: {short_ma}")
                print(f"میانگین متحرک بلندمدت: {long_ma}")
                print(f"RSI: {rsi}")
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

    time.sleep(3600)  # توقف برای یک ساعت