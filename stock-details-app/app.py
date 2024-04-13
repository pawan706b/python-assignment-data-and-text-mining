import streamlit as st
import pandas as pd
import requests

# Set the title of the application
st.title('Stock Details App')

# API URLs and API key
COINS_LIST_URL = 'https://api.coingecko.com/api/v3/coins/list'
COIN_MARKET_CHART_URL = 'https://api.coingecko.com/api/v3/coins/{id}/market_chart'
API_KEY = 'CG-vVvkNLMHKhJgiEPeP2YfDnAZ'

# Headers to include in requests
headers = {
    'accept': 'application/json',
    'Authorization': f'Bearer {API_KEY}'
}

# Function to fetch available cryptocurrencies
def fetch_available_coins():
    response = requests.get(COINS_LIST_URL, headers=headers)
    if response == 200:
        print(pd.DataFrame((response.json())))
        return pd.DataFrame(response.json())
    else:
        st.error('Failed to load coin list.')
        return pd.DataFrame()

coin_list = fetch_available_coins()

# User input for cryptocurrency name
coin_name = st.text_input("Enter a coin name", "bitcoin").lower().strip()

if  not coin_list.empty and coin_name in coin_list['id'].values:
    coin_id = coin_name
    response = requests.get(COIN_MARKET_CHART_URL.format(id=coin_id), params={'vs_currency': 'usd', 'days': '365'}, headers=headers)
    if response == 200:
        price_data = response.json().get('prices', [])
        if price_data:
            data = pd.DataFrame(price_data, columns=['timestamp', 'price'])
            data['date'] = pd.to_datetime(data['timestamp'], unit='ms')
            data.set_index('date', inplace=True)
            st.line_chart(data['price'])

            # Calculate and display max and min price
            max_price = data['price'].max()
            min_price = data['price'].min()
            max_date = data[data['price'] == max_price].index.strftime('%Y-%m-%d')[0]
            min_date = data[data['price'] == min_price].index.strftime('%Y-%m-%d')[0]

            st.write(f"Maximum price: ${max_price:.2f} on {max_date}")
            st.write(f"Maximum price date: {max_date}")
            st.write(f"Minimum price: ${max_price:.2f} on {max_date}")
            st.write(f"Minimum price date: {min_date}")
        else:
            st.error("No price data available for this coin.")
    else:
        st.error("Failed to fetch data for the selected coin.")
else:
    st.error(f"The coin name '{coin_name}' is not recognized.")