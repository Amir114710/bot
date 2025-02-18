import requests
import pandas as pd
import time

symbol = 'bitcoin'
position = None  # وضعیت معامله (None, 'long', 'short')
prices = []  # لیست برای ذخیره قیمت‌ها

# تابع برای دریافت قیمت‌ها
def fetch_data():
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()[symbol]['usd']
    else:
        print("Error fetching data:", response.status_code)
        return None

# تابع برای محاسبه میانگین متحرک
def calculate_ma(prices, window):
    return pd.Series(prices).rolling(window=window).mean().iloc[-1]

while True:
    latest_price = fetch_data()  # دریافت آخرین قیمت
    if latest_price is not None:
        prices.append(latest_price)  # قیمت را به لیست اضافه کنید
        print(f"آخرین قیمت {symbol}: {latest_price}")

        # محاسبه میانگین متحرک با دوره 10
        if len(prices) >= 10:
            latest_ma = calculate_ma(prices, window=10)
            print(f"میانگین متحرک: {latest_ma}")

            # سیگنال خرید و فروش بر اساس روند
            if latest_price > latest_ma and position != 'long':
                position = 'long'
                print("سیگنال خرید: ورود به معامله خرید")
            elif latest_price < latest_ma and position != 'short':
                position = 'short'
                print("سیگنال فروش: خروج از معامله")

    time.sleep(60)  # توقف برای یک دقیقه