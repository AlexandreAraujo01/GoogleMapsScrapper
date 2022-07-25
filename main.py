"scrapping on google maps"
import configparser
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd




class GoogleMapsEnricher:
    "Class to Scrap"
    def __init__(self,localization,keyword):
        opts = Options()
        opts.add_argument("--headless") 
        # opts.add_argument("--log-level=3")
        opts.add_experimental_option('excludeSwitches', ['enable-logging'])

        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        # setting the keyword to search
        # self.keyword = self.config['DEFAULT']['keyword'].replace(' ','+')
        self.keyword = keyword.replace(' ','+')
        # setting the localization to search
        # self.localization = self.config['DEFAULT']['localization'].replace(' ','+')
        self.localization = localization.replace(' ','+')
        self.url = self.config['DEFAULT']['url']
        # google dont use spaces need to replace for "+"
        self.parameters = f'{self.localization}+{self.keyword}'
        self.html = None
        self.driver = webdriver.Chrome(options=opts)

    def get_html_text(self):
        "function that takes the parameters and query on google maps"
        url = f'{self.url}{self.parameters}'
        self.driver.get(url)
        # getting the page_source to scrap
        html = self.driver.page_source
        self.html = html

    def get_company_site(self,name):
        "get the site of the current company"
        name = name.replace(" ","+")
        url = f"https://www.google.com/search?q={name}+site"
        self.driver.get(url)
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        result = soup.select_one('cite').text
        return result

    def html_soup(self):
        "function that takes the html's page source and extract the current informations"
        soup = BeautifulSoup(self.html, 'html.parser')
        divs = soup.select('div div a[aria-label]')
        nomes = []
        enderecos = []
        estrelas = []
        qtd_avaliacoes = []
        aberturas = []
        sites = []
        for _,empresa in enumerate(divs):
            try:
                nome = empresa['aria-label']
                site = self.get_company_site(nome).split(" ")[0]
                print(site)
                empresa_div = empresa.parent.select_one("div[aria-label]")
                spans = empresa_div.select("div div div div div div div span")
                endereço = spans[17].text
                estrela = spans[3].text
                qtd_avaliacao = estrela.split('(')[1].replace(')','')
                abertura = spans[25].text
                nomes.append(nome)
                enderecos.append(endereço)
                estrelas.append(estrela)
                qtd_avaliacoes.append(qtd_avaliacao)
                aberturas.append(abertura)
                sites.append(site)        
                # print(nome,endereço,abertura,estrela,qtd_avaliacao)
            except:
                continue
        dictionary = {"name": nomes, "adress": enderecos , "stars_rating": estrelas,
                    "number_of_peoople_rating": qtd_avaliacoes,
                    "openning_on": aberturas,"domain": sites
                    }
        self.driver.quit()
        return dictionary

    def soup_to_csv(self,dictionary):
        "bla bla bla"
        # function that takes the extract's informations and make a csv
        dataframe = pd.DataFrame(dictionary)
        dataframe.to_csv(
            f'{self.localization.replace("+"," ")} {self.keyword.replace("+"," ")}.csv',
             index=False,encoding="utf-8")


if __name__ == "__main__":
    df = pd.read_csv("exemplo.csv",encoding="utf-8")
    for c in range(len(df)):
        local = df.loc[c,["localization"]][0]
        keyword = df.loc[c,["keyword"]][0]
        print(f"scrapando.. {local}-{keyword}")
        c1 = GoogleMapsEnricher(local,keyword)
        c1.get_html_text()
        c1.soup_to_csv(c1.html_soup())

