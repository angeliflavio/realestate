# Crawler for immobiliare.it

from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import datetime
import time
import argparse

# location from command argument
ap = argparse.ArgumentParser()
ap.add_argument('-l','--location',required=True,help='search location')
args = vars(ap.parse_args())
location = args['location']

# crawling procedure CASA.IT
df_casa = pd.DataFrame()
pagine = pd.DataFrame()
i = 1
annunci_prev = 0
last_page = False
while True:
    print('\n--------\nPage {}'.format(i))
    time.sleep(5)
    try:
        page = requests.get('https://www.casa.it/vendita/residenziale/{}?page={}'.format(location, i))
        soup = BeautifulSoup(page.content, 'html.parser')
        annunci = soup.find_all('article')
        pagine = pagine.append({'Pagina':i,
                                'Nr Annunci':len(annunci)}, ignore_index=True)
        if (len(annunci) < annunci_prev):
            last_page = True
        annunci_prev = len(annunci)
        print('Numero annunci {}'.format(len(annunci)))
    except:
        print('Page {} not found'.format(i))
        break
    if len(annunci)==0:
        break
    for annuncio in annunci:
        indirizzo = annuncio.find_all('a')[0].get_text()
        print(indirizzo)
        link = 'https://www.casa.it' + annuncio.find_all('a')[0]['href']
        print(link)
        descrizione = annuncio.find_all('p',{'decription'})[0].get_text()
        print(descrizione)
        try:
            dettagli = annuncio.find_all('div',{'features'})[0]
            prezzo = dettagli.find_all('p')[0].get_text().split('Tua')[0]
            print(prezzo)
            superficie = dettagli.find_all('li')[0].get_text()
            print(superficie)
            locali = dettagli.find_all('li')[1].get_text()
            print(locali)
        except:
            prezzo = ''
            superficie = ''
            locali = ''
        #agenzia = annuncio.find('a',{'sp'})['title']
        #print(agenzia)
        df_casa = df_casa.append({'indirizzo': indirizzo,
                                'link': link,
                                'prezzo': prezzo,
                                'locali': locali,
                                #'agenzia': agenzia,
                                'superficie': superficie,
                                'descrizione': descrizione}, ignore_index = True)
    if last_page is True:
        break
    i += 1
    
df_casa['superficie'] = df_casa['superficie'].str.replace(' mq','')   
df_casa['locali'] = df_casa['locali'].str.strip()
df_casa['fonte'] = 'https://www.casa.it'
df_casa['location'] = location



# info about crawled data
print(pagine)
print('-----------')
print(df_casa.shape)  

file_name = 'prezzi/' + location + '_' + datetime.date.today().strftime("%Y%m%d") + '_casa.csv'
df_casa.to_csv(file_name, encoding = 'utf-8-sig', sep = ';')
