import requests
import pandas as pd
import time

symbol = 'bitcoin'
position = None  # وضعیت معامله (None, 'long', 'short')
prices = []  # لیست برای ذخیره قیمت‌ها

# تابع برای دریافت داده‌های قیمت برای 1 روز گذشته
def fetch_historical_data():
    url = f'https://api.coingecko.com/api/v3/coins/{symbol}/market_chart?vs_currency=usd&days=1'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['prices']
    else:
        print(f"Error fetching historical data: {response.status_code} - {response.text}")
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

while True:
    historical_data = fetch_historical_data()  # دریافت داده‌های تاریخی
    if historical_data is not None and len(historical_data) > 0:
        # استخراج قیمت‌ها از داده‌های قیمت
        prices = [price[1] for price in historical_data]  # قیمت بسته شدن

        # محاسبه میانگین متحرک
        if len(prices) >= 20:
            short_ma = calculate_ma(prices, window=10)  # میانگین متحرک کوتاه‌مدت
            long_ma = calculate_ma(prices, window=20)   # میانگین متحرک بلندمدت
            latest_price = prices[-1]  # آخرین قیمت

            # محاسبه RSI
            if len(prices) >= 14:
                rsi = calculate_rsi(prices)  # محاسبه RSI

                print(f"آخرین قیمت {symbol}: {latest_price}")
                print(f"میانگین متحرک کوتاه‌مدت: {short_ma}")
                print(f"میانگین متحرک بلندمدت: {long_ma}")
                print(f"RSI: {rsi}")

                # سیگنال خرید و فروش بر اساس تقاطع میانگین‌ها و RSI
                if short_ma > long_ma and position != 'long' and rsi < 30:
                    position = 'long'
                    print("سیگنال خرید: ورود به معامله خرید")
                elif short_ma < long_ma and position != 'short' and rsi > 70:
                    position = 'short'
                    print("سیگنال فروش: خروج از معامله")

    time.sleep(60)  # توقف برای یک دقیقه