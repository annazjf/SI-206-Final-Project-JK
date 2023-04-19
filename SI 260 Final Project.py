import requests

params = {
  'access_key': '8b41de70f2608beb142d04362029660e'
}

api_result = requests.get('https://api.marketstack.com/v1/tickers/aapl/eod', params)

api_response = api_result.json()

for stock_data in api_response['data']:
    print(stock_data['date'])