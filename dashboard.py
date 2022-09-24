import streamlit as st
import pandas as pd
from datetime import datetime
#/Users/tenzinkamtzi/Library/"Mobile Documents"/com~apple~CloudDocs/Zinbari/01_Personal/Tenzin/"Tenzin Python Codes"/Project_Webscraping_Watchlist/Dashboard_Price_Capturer/

import streamlit_authenticator as stauth
import plotly.express as px
import os
import database as db

st.set_page_config(page_title='Dashboard Price Scraper', page_icon=":bar_chart:", layout='wide')

st.write("""
# Dashboard Price Scraper
This is the dashboard of our price scraper. All prices are captured on toppreise.ch.
""")

#--- USER AUTHENTIFICATION
users=db.fetch_all_users()
print(users)
usernames=[user['key'] for user in users]
names=[user['name'] for user in users]
hashed_passwords=[user["password"] for user in users] 


authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    "dashboard_price_scraper", "dashboard", cookie_expiry_days=30)

name,authentication_status, username = authenticator.login("Login","main")

if authentication_status == False:
    st.error("Username/password is incorrect")
if authentication_status == None:
    st.warning("Please enter your username and passwor")
if authentication_status:

    #--- SIDE BAR
    st.sidebar.title(f'Welcome {name}')
    authenticator.logout("Logout",'sidebar')

    filename_prices='db_prices.csv'
    filename_subscribers='db_subscribers.csv'
    filename_products='db_products.csv'
    filepath='/Users/tenzinkamtzi/Library/Mobile Documents/com~apple~CloudDocs/Zinbari/01_Personal/Tenzin/Tenzin Python Codes/Project_Webscraping_Watchlist/'
    df_db_prices=pd.read_csv(filepath + filename_prices)
    df_db_subscribers=pd.read_csv(filepath + filename_subscribers)
    df_db_products=pd.read_csv(filepath + filename_products)

    df_db_prices['Date']=df_db_prices['Date'].str.split('.',expand=True)[0]
    df_db_prices_reconciled=df_db_prices.set_index('Date')
    df_db_prices_reconciled.sort_index(ascending=False,inplace=True)
    #df_db_prices_reconciled=df_db_prices_reconciled.applymap(lambda x: str(int(x)) if abs(x - int(x)) < 1e-6 else str(round(x,2)))

    def convert_id_to_name(product_id):
        product_id=str(product_id)
        df_db_products=pd.read_csv(filepath + filename_products)
        try:
            df_db_products=df_db_products.set_index('product_id')
            product_name=df_db_products.loc[product_id]['product_name']

        except KeyError as ke:
            return print('Product ID not found!')
        return product_name

    #df_db_prices reconiliation, that product id is properly visible
    i=0	
    for column in df_db_prices_reconciled: 
        if df_db_prices_reconciled.columns[i]==column:
            if convert_id_to_name(column) in df_db_prices_reconciled.columns:
                df_db_prices_reconciled.rename(columns={df_db_prices_reconciled.columns[i]:convert_id_to_name(column)}, inplace=True)
            df_db_prices_reconciled.rename(columns={df_db_prices_reconciled.columns[i]:convert_id_to_name(column)+str(column)}, inplace=True)
        i=i+1

    st.write("### i) Individual Dashboard")
    articles=st.multiselect(
    	'Choose articles', list(df_db_prices_reconciled))
    data=df_db_prices_reconciled[articles]
    st.line_chart(data)

    st.write('Check out our last update provided from price scraper')
    filename_log='log_scraping.txt'

    with open(filepath+filename_log) as f:
        lines = f.readlines()
        st.text(lines)

    st.write("### ii) All Prices Reconciled")
    df_db_prices_reconciled

    st.write("""
    ## Appendix: Raw Price Data
    This list shows all prices in CHF captured so far across product article number.
    """)
    df_db_prices

    st.write("""
    ## Appendix: Raw Product Data
    This list shows all products which are scanned for price changes.
    """)
    df_db_products

    st.write("""
    ## Appendix: Raw Subscriber Data
    This is a list of all subscriber registered.
    """)
    df_db_subscribers
