# Script to crawl the website https://www.mercato-immobiliare.info/

import pandas as pd
import requests
import datetime
from bs4 import BeautifulSoup
import re
import time
import random


def name_to_url(name):
    '''
    convert region/city/province to url format
    e.g.: Emilia Romagna --> Emilia-Romagna
    '''
    return(re.sub(" |'",'-',name))


def clean_prices(df):
    '''
    clean rent/purchase prices removing the unit of measure 
    e.g.: € 1.000 /m² --> 1000
    '''
    df.vendita=df.vendita.str.extract("€ (.+) /m²").str.replace('.','').astype('int')
    df.affitto=df.affitto.str.extract("€ (.+) /m²/mese").str.replace(',','.').astype('float')


# get italian regions
regions=pd.read_html('https://www.mercato-immobiliare.info',thousands='.',decimal=',')[0]
regions['data']=datetime.date.today()
regions.to_csv('prezzi/regions.csv')


# loop through the regions and get:  
# 1. table with prices by province
# 2. table with prices by property type
provinces_prices=pd.DataFrame()   # dataframe with prices by province
regions_types=pd.DataFrame()      # dataframe with prices by property type
for r in regions.regione:
    try:
        t=pd.read_html('https://www.mercato-immobiliare.info/'+name_to_url(r)+'.html')
        table_prices=t[0]
        table_prices['regione']=r
        table_prices['data']=datetime.date.today()
        provinces_prices=provinces_prices.append(table_prices,ignore_index=True)
        table_types=t[1]
        table_types['regione']=r
        table_types['data']=datetime.date.today()
        regions_types=regions_types.append(table_types,ignore_index=True)
        print(r+' OK')
    except:
        print(r,' not working!')
# clean prices removing the unit of measure
clean_prices(provinces_prices)
clean_prices(regions_types)
# save dataframes as csv files
provinces_prices.to_csv('prezzi/provinces_prices.csv')
regions_types.to_csv('prezzi/regions_types.csv')

    
# loop through the provinces and get:
# 1. table with prices by city
# 2. table with prices by property type
cities_prices=pd.DataFrame()        # dataframe with prices by city
provinces_types=pd.DataFrame()      # dataframe with prices by property type
for index,row in provinces_prices.iterrows():
    prov=row['provincia']
    reg=row['regione']
    try:
        t=pd.read_html('https://www.mercato-immobiliare.info/'+name_to_url(reg)+'/'+name_to_url(prov)+'.html')
        table_prices=t[0]
        table_prices['regione']=reg
        table_prices['provincia']=prov
        table_prices['data']=datetime.date.today()
        cities_prices=cities_prices.append(table_prices,ignore_index=True)
        table_types=t[1]
        table_types['regione']=reg
        table_types['provincia']=prov
        table_types['data']=datetime.date.today()
        provinces_types=provinces_types.append(table_types,ignore_index=True)
        print(reg,prov+' OK')
    except:
        print(prov,' not working!')
# clean prices removing the unit of measure
clean_prices(cities_prices)
clean_prices(provinces_types)
# save dataframes as csv files
cities_prices.to_csv('prezzi/cities_prices.csv')
provinces_types.to_csv('prezzi/provinces_types.csv')


        
# loop through the cities and get:
# 1. table with prices by property type
cities_types=pd.DataFrame()         # dataframe with prices by property type
for index,row in cities_prices.iterrows():
    com=row['comune']
    prov=row['provincia']
    reg=row['regione']
    try:
        table_types=pd.read_html('https://www.mercato-immobiliare.info/'+name_to_url(reg)+'/'+name_to_url(prov)+'/'+name_to_url(com)+'.html',match='tipologia')[0]
        table_types['regione']=reg
        table_types['provincia']=prov
        table_types['comune']=com
        table_types['data']=datetime.date.today()
        cities_types=cities_types.append(table_types,ignore_index=True)
        print(reg,prov,com+' OK')
    except:
        print(com,' not working!')
# clean prices removing the unit of measure
clean_prices(cities_types)
# save dataframes as csv files
cities_types.to_csv('prezzi/cities_types.csv')
    


    
