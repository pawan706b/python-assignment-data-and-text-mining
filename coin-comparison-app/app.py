import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import time

# Set the title of the application
st.title('Coin Comparison App')

API_COINS_LIST_URL = 'https://api.coingecko.com/api/v3/coins/list'
API_COIN_MARKET_CHART_URL = 'https://api.coingecko.com/api/v3/coins/{id}/market_chart'
API_KEY = 'CG-vVvkNLMHKhJgiEPeP2YfDnAZ'

headers = {
	'accept': 'application/json',
	'Authorization': f'Bearer {API_KEY}'
}

def fetch_coins_list():
	response = requests.get(API_COINS_LIST_URL, headers=headers)
	if response.status_code == 200:
		return pd.DataFrame(response.json())
	elif response.status_code == 429:
		time.sleep(2)
	else:
		st.error(f'Failed to fetch coin list. Status Code: {response.status_code}')
		return pd.DataFrame()
	return pd.DataFrame()

coins_list_df = fetch_coins_list()

if not coins_list_df.empty:
	first_coin = st.text_input("Enter the first coin name", value="bitcoin").lower().strip()
	second_coin = st.text_input("Enter the second coin name", value="ethereum").lower().strip()

	time_frame = st.selectbox("Select time frame", options=["7", "30", "365", "1825"], 
							  format_func=lambda x: f"{int(x)//365} year" if int(x) > 30 else f"{x} days")

	def fetch_coin_data(coin_id, days):
		params = {
			'vs_currency': 'usd',
			'days': days,
			'interval': 'daily'
		}
		response = requests.get(API_COIN_MARKET_CHART_URL.format(id=coin_id), params=params, headers=headers)
		if response.status_code == 200:
			data = response.json()
			df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
			df['volume'] = pd.DataFrame(data['total_volumes'])[1]
			df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
			df.set_index('date', inplace=True)
			return df
		else:
			st.error(f'Failed to fetch data for {coin_id}. Status Code: {response.status_code}')
			return pd.DataFrame()

	if first_coin in coins_list_df['id'].values and second_coin in coins_list_df['id'].values:
		first_coin_data = fetch_coin_data(first_coin, time_frame)
		second_coin_data = fetch_coin_data(second_coin, time_frame)

		if not first_coin_data.empty and not second_coin_data.empty:
			price_fig = go.Figure()
			price_fig.add_trace(go.Scatter(x=first_coin_data.index, y=first_coin_data['price'], mode='lines', name=f'{first_coin.capitalize()} Price', line=dict(color='blue')))
			price_fig.add_trace(go.Scatter(x=second_coin_data.index, y=second_coin_data['price'], mode='lines', name=f'{second_coin.capitalize()} Price', line=dict(color='red')))
			price_fig.update_layout(title='Price Comparison', yaxis_title='Price in USD', xaxis_title='Date')
			st.plotly_chart(price_fig)