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
ap.add_argument('-l','--location',required=True,
                help='search location', nargs='+')
args = vars(ap.parse_args())
locations = args['location']

# crawling procedure IMMOBILIARE.IT
def CrawlImmobiliareIt(location):
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
    df_immobiliare['data'] = datetime.date.today()

    # info about crawled data
    print('-----------')
    print(df_immobiliare.shape)
    
    return(df_immobiliare)




# crawling procedure CASA.IT
def CrawlCasaIt(location):
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
            try:
                descrizione = annuncio.find_all('p',{'decription'})[0].get_text()
                print(descrizione)
            except:
                descrizione=''
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
    df_casa['location'] = location.upper()
    df_casa['data'] = datetime.date.today()

    # info about crawled data
    print(pagine)
    print('-----------')
    print(df_casa.shape)  

    return(df_casa)



# loop through the locations
for location in locations:
    df1 = CrawlImmobiliareIt(location=location)
    df2 = CrawlCasaIt(location=location)
    # merge the two dataframes
    df_re = pd.concat([df1, df2], ignore_index=True, sort=False)
    # df_re['euro/mq'] = df_re['prezzo'] / df_re['superficie']
    file_name = 'dsh_re/prezzi/' + location + '_' + datetime.date.today().strftime("%Y%m%d") + '.csv'
    print('---------------\nFile name: {}'.format(file_name))
    print('Records: {}'.format(df_re.shape[0]))
    df_re.to_csv(file_name, encoding = 'utf-8-sig', sep = ';', index = False) 