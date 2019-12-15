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

# crawling procedure IMMOBILIARE.IT
df_immobiliare = pd.DataFrame()
i = 1
while True:
    print('Page {}'.format(i))
    time.sleep(5)
    try:
        page = requests.get('https://www.immobiliare.it/vendita-case/{}/?pag={}'.format(location,i))
        soup = BeautifulSoup(page.content, 'html.parser')
        annunci = soup.find_all('div', {'class':'listing-item_body'})
        print('Nr annunci {}'.format(len(annunci)))
    except:
        print('Page {} not found'.format(i))
        break
    if len(annunci)==0:
        break
    for annuncio in annunci:
        titolo = annuncio.find_all('p', {'class':'titolo text-primary'})[0]
        titolo_testo = titolo.get_text()
        link = titolo.find('a')['href']
        print(titolo_testo)
        print(link)
        dettagli_annuncio = annuncio.find('ul', {'class':'listing-features list-piped'})
        prezzo = dettagli_annuncio.find_all('li')[0].get_text().replace('\n','').strip()
        print(prezzo)
        try:
            locali = dettagli_annuncio.find_all('li')[1].get_text()
        except:
            locali = ''
        print(locali)
        try:
            superficie = dettagli_annuncio.find_all('li')[2].get_text()
        except:
            superficie = ''
        print(superficie)
        try:
            bagni = dettagli_annuncio.find_all('li')[3].get_text()
        except:
            bagni = ''
        print(bagni)
        descrizione = annuncio.find_all('div', {'class':'descrizione'})[0].get_text().replace('\n','').strip()
        print(descrizione)
        df_immobiliare = df_immobiliare.append({'titolo': titolo_testo,
                                                'link': link,
                                                'prezzo': prezzo,
                                                'locali': locali,
                                                'bagni': bagni,
                                                'superficie': superficie,
                                                'descrizione': descrizione}, ignore_index = True)
    i += 1
       
df_immobiliare.titolo = df_immobiliare.titolo.str.replace('\n','')
df_immobiliare.superficie = df_immobiliare.superficie.str.replace('m2superficie','').str.strip()
df_immobiliare['fonte'] = 'https://www.immobiliare.it'
df_immobiliare['location'] = location.upper()

# info about crawled data
print('-----------')
print(df_immobiliare.shape)
file_name = 'prezzi/' + location + '_' + datetime.date.today().strftime("%Y%m%d") + '_immobiliare.csv'
df_immobiliare.to_csv(file_name, encoding = 'utf-8-sig', sep = ';')


