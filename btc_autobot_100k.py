import os
import hmac
import hashlib
import time
import requests
import urllib.parse

# API 키를 환경변수에서 불러오기
api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")

symbol = "BTCUSDT"
quantity = 0.0002
profit_target = 1.03
stop_loss = 0.98

def create_signature(query_string, secret):
    return hmac.new(secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

def place_order(side, quantity, symbol):
    url = "https://api.binance.com/api/v3/order"
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
        "timestamp": timestamp
    }
    query_string = urllib.parse.urlencode(params)
    signature = create_signature(query_string, secret_key)
    headers = {
        "X-MBX-APIKEY": api_key
    }
    full_url = f"{url}?{query_string}&signature={signature}"
    response = requests.post(full_url, headers=headers)
    return response.json()

def get_current_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    response = requests.get(url)
    data = response.json()

    if 'price' not in data:
        print("API 응답 오류:", data)
        return None

    return float(data['price'])

buy_price = get_current_price(symbol)
if buy_price:
    buy_result = place_order("BUY", quantity, symbol)
    print("매수 완료:", buy_result)

    while True:
        time.sleep(60)
        current_price = get_current_price(symbol)
        if not current_price:
            continue

        if current_price >= buy_price * profit_target:
            sell_result = place_order("SELL", quantity, symbol)
            print("익절 매도:", sell_result)
            break

        elif current_price <= buy_price * stop_loss:
            sell_result = place_order("SELL", quantity, symbol)
            print("손절 매도:", sell_result)
            break
else:
    print("현재 가격을 불러오지 못해 매수를 진행하지 않습니다.")
