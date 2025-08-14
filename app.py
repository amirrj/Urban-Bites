import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='Urban Bites Cafe', layout='wide')
st.title('📊 Urban Bites Sales Dashboard')

@st.cache_data
def load_data():
    data = pd.read_csv('urban_bites_cafe_sales.csv', parse_dates=['OrderDate'])
    data['UnitPrice'] = round(data['UnitPrice'], 2)
    data['TotalPrice'] = round(data['TotalPrice'], 2)
    return data

data = load_data()

# side bar
st.sidebar.header('Filtered Data')
store_filter = st.sidebar.multiselect('Select Store', data['StoreLocation'].unique())
category_filter = st.sidebar.multiselect('Select Category', data['Category'].unique())
date_filter = st.sidebar.date_input('Select Date Range', [data['OrderDate'].min(), data['OrderDate'].max()])

filtered_data = data.copy()
if store_filter:
    filtered_data = filtered_data[filtered_data['StoreLocation'].isin(store_filter)]
if category_filter:
    filtered_data = filtered_data[filtered_data['Category'].isin(category_filter)]
filtered_data = filtered_data[(filtered_data['OrderDate'] >= pd.to_datetime(date_filter[0])) & (filtered_data['OrderDate'] <= pd.to_datetime(date_filter[1]))]


# total metrics
total_sales = filtered_data['TotalPrice'].sum()
total_transactions = len(filtered_data)
avg_basket = filtered_data['Quantity'].mean()
avg_sales = filtered_data['TotalPrice'].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric('💰Total Sales', f'£{total_sales:.2f}')
col2.metric('🛒 Total Transactions', f'{total_transactions}')
col3.metric('📦 Avg Basket Size', f'{avg_basket:.2f}')
col4.metric('💳 Avg Order Value', f'£{avg_sales:.2f}')

# sales over time
sales_over_time = filtered_data.groupby('OrderDate')['TotalPrice'].sum().reset_index()
fig_sales = px.line(sales_over_time,
                    x='OrderDate', y='TotalPrice', title='Sales Over Time')
st.plotly_chart(fig_sales, use_container_width=True)

# Top products
top_products = filtered_data.groupby('Product')['TotalPrice'].sum().sort_values(ascending=False).reset_index()
fig_products = px.bar(top_products, x='Product', y='TotalPrice', title='Top 10 Products', text_auto=True)
st.plotly_chart(fig_products, use_container_width=True)

# store comparison
store_sales = filtered_data.groupby('StoreLocation')['TotalPrice'].sum().reset_index()
fig_stores = px.bar(store_sales, x='StoreLocation', y='TotalPrice', text_auto='True', title='Sales Per Store')
st.plotly_chart(fig_stores, use_container_width=True)

# promotions
promo_by_store = filtered_data.groupby(['StoreLocation', 'Promotion'])['TotalPrice'].sum().reset_index()
promo_by_store['Percent'] = promo_by_store.groupby('StoreLocation')['TotalPrice'].transform(lambda x: (x / x.sum()) * 100)
fig_promo = px.bar(promo_by_store, x='Percent', y='StoreLocation',color='Promotion', orientation='h', barmode='stack',
                   text=promo_by_store['Percent'].map(lambda x: f'{x:.0f}%'), color_discrete_sequence=['royalblue', 'deepskyblue'])
fig_promo.update_layout(xaxis=dict(range=[0, 100]),
                        title={'text': f'Percent Of Sales <span style="color:deepskyblue">With</span> vs <span style="color:royalblue">Without</span> Promotions'})
fig_promo.update_traces(
    insidetextanchor='middle'
)
st.plotly_chart(fig_promo, use_container_width=True)

# sales per hour
hourly_sales = filtered_data.groupby('Hour')['TotalPrice'].sum().reset_index()
fig_hour = px.bar(hourly_sales, x='Hour', y='TotalPrice', title='Sales By Hour of the Day')
fig_hour.update_layout(xaxis=dict(
    tickmode='array',
    tickvals=list(range(7, 20)),
    ticktext=[f'{h}am' if h < 12 else f'{h-12 if h > 12 else 12}pm' for h in range(7, 20)]
))
st.plotly_chart(fig_hour, use_container_width=True)


