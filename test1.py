import requests
import pandas as pd
import time

# تنظیمات اولیه
symbol = 'bitcoin'
position = None  # وضعیت معامله (None, 'long', 'short')

def fetch_data():
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()[symbol]['usd']
    else:
        print("Error fetching data:", response.status_code)
        return None

def check_signals(current_price):
    global position

    # یک استراتژی ساده: خرید زیر 20000 و فروش بالای 30000
    if current_price < 20000 and position != 'long':
        position = 'long'
        print("سیگنال ورود: ورود به معامله خرید")
        # اینجا می‌توانید کد خرید را اضافه کنید

    elif current_price > 30000 and position != 'short':
        position = 'short'
        print("سیگنال خروج: خروج از معامله")
        # اینجا می‌توانید کد فروش را اضافه کنید

while True:
    current_price = fetch_data()
    if current_price is not None:
        print(f"Current price of {symbol}: ${current_price}")
        check_signals(current_price)

    time.sleep(60)  # توقف برای یک دقیقه

