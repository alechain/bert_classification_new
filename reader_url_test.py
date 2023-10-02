# ... (other imports)
from scrapy.http import Request
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from urllib.parse import urlparse
from scrapy.utils.response import open_in_browser
from scrapy.crawler import CrawlerProcess
from urllib import parse
from os import path
from scrapy.http.response.html import HtmlResponse
import multiprocessing
from typing import List
from bs4 import BeautifulSoup
import json  # Add this line to import the json module
import os
from sklearn.feature_extraction.text import CountVectorizer
from bs4 import BeautifulSoup
import re
import os
import joblib
from typing import Pattern, Optional, List, Tuple


# este es el texto que tiene que aparecer en las notas, antes del texto de la nota
#MARCADOR_COMIENZO_INTERESANTE="<div class=\"article-main-content article-text \">"
# este es el texto que tiene que aparecer en las notas, despues del texto de la nota
#MARCADOR_FIN_INTERESANTE="</div></article>"
#
# extractor_de_parte_de_html_que_interesa = re.compile(re.escape(MARCADOR_COMIENZO_INTERESANTE) + "(.+)" + re.escape(MARCADOR_FIN_INTERESANTE))



class NewsSpider(CrawlSpider):
    name = "url_reader"
    rules = (
        # Ejemplo de regla de scrapping:
        # solo bajar las paginas cuya url incluye "/secciones", pero no aquellas cuya url include "/catamarca12" o "/dialogo".
        # Ud. tiene que modificar esta regla para bajar solo indice + noticias de pagina 12.
        # scrappy normaliza las urls para no descargarlas 2 veces la misma pagina con distinta url.
        Rule(LinkExtractor(
               deny_domains=['auth.pagina12.com.ar'], canonicalize=True,
               deny_extensions=['7z', '7zip', 'apk', 'bz2', 'cdr,' 'dmg', 'ico,' 'iso,' 'tar', 'tar.gz','pdf','docx', 'jpg', 'png', 'css', 'js']),
               callback='parse_response', follow=True),
     )
     
    # configuracion de scrappy, ver https://docs.scrapy.org/en/latest/topics/settings.html
    # la var de clase debe llamarse "custom settings"
    custom_settings = {
      # mentir el user agent
     'USER_AGENT': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
     'LOG_ENABLED': True,
     'LOG_LEVEL': 'INFO',
      # no descargar paginas mas alla de 1 link desde la pagina de origen
     'DEPTH_LIMIT': 2,
      # ignorar robots.txt (que feo eh)
     'ROBOTSTXT_OBEY': False,
      # esperar entre 0.5*DOWNLOAD_DELAY y 1.5*DOWNLOAD_DELAY segundo entre descargas
     'DOWNLOAD_DELAY': 1,
     'RANDOMIZE_DOWNLOAD_DELAY': True
    }


    def start_requests(self):
        urls_folder_path = '/Users/achain/Documents/github/web-mining/url_tot'

        # Loop through the files in the folder
        for filename in os.listdir(urls_folder_path):
            if filename.endswith('.txt'):
                file_path = os.path.join(urls_folder_path, filename)
                with open(file_path, 'r') as urls_file:
                    prefix = None
                    if filename.startswith('eco'):
                        prefix = 'eco'
                    elif filename.startswith('socie'):
                        prefix = 'socie'
                    elif filename.startswith('el-pai'):
                        prefix = 'el-pai'
                    elif filename.startswith('el-mun'):
                        prefix = 'el-mun'

                    if prefix:
                        save_path = os.path.join('/Users/achain/Documents/github/web-mining/pages', prefix)
                        os.makedirs(save_path, exist_ok=True)

                        for url in urls_file:
                            yield scrapy.Request(url=url.strip(), meta={'save_path': save_path}, callback=self.parse_response)

    def parse_response(self, response):
        article_content = response.text
        filename = response.url.split('/')[-1] + '.html'
        save_path = response.meta.get('save_path')

        with open(os.path.join(save_path, filename), 'w', encoding='utf-8') as file:
            file.write(article_content)

        yield {
            'url': response.url,
            'content': article_content
        }

if __name__ == "__main__":
    process = CrawlerProcess(settings={
        # You can add additional settings here if needed
    })

    # Start the spider by passing the NewsSpider class
    process.crawl(NewsSpider)

    # Execute the spider
    process.start()