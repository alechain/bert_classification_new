# -*- coding: utf-8 -*-
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





class NewsSpider(CrawlSpider):

    name = 'crawler_pagina12'
    # solo descargar paginas desde estos dominios
    allowed_domains = ('www.pagina12.com.ar','pagina12.com.ar')
    
    rules = (
        # Ejemplo de regla de scrapping:
        # solo bajar las paginas cuya url incluye "/secciones", pero no aquellas cuya url include "/catamarca12" o "/dialogo".
        # Ud. tiene que modificar esta regla para bajar solo indice + noticias de pagina 12.
        # scrappy normaliza las urls para no descargarlas 2 veces la misma pagina con distinta url.
        Rule(LinkExtractor(allow=r'.+/secciones/(eco|socied|el.{0,1}pa|el.{0,1}mun).+',deny='.+(/catamarca12|/dialogo|/soci%).+',
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
     'DEPTH_LIMIT': 50,
      # ignorar robots.txt (que feo eh)
     'ROBOTSTXT_OBEY': False,
      # esperar entre 0.5*DOWNLOAD_DELAY y 1.5*DOWNLOAD_DELAY segundo entre descargas
     'DOWNLOAD_DELAY': 1,
     'RANDOMIZE_DOWNLOAD_DELAY': True
    }

    def __init__(self, save_pages_in_dir='/Users/achain/Documents/github/web-mining/url_tot', *args, **kwargs):
          super().__init__(*args, **kwargs)
          # guardar el directorio en donde vamos a descargar las paginas
          self.basedir = save_pages_in_dir
    

    def parse_response(self, response: HtmlResponse):
        """
        Este metodo es llamado por cada url que descarga Scrappy.
        response.url contiene la url de la pagina,
        response.body contiene los bytes del contenido de la pagina.
        """
        # el nombre de archivo es lo que esta luego de la ultima "/"
        html_filename = path.join(self.basedir, parse.quote(response.url[response.url.rfind("/") + 1:]))
        if not html_filename.endswith(".html"):
            html_filename += ".html"
        print("URL:", response.url, "Pagina guardada en:", html_filename)
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.body, 'html.parser')
        
        # Find the script containing the desired data
        script_tag = soup.find('script', string=lambda text: text and "ItemList" in text)
        
        if script_tag:
            script_content = script_tag.string
            start_index = script_content.index('[')
            end_index = script_content.rindex(']')
            json_data = script_content[start_index:end_index + 1]
            
            # Parse the JSON data
            parsed_json = json.loads(json_data)
            
            # Extract the "url" values from each dictionary
            urls = [item["url"] for item in parsed_json]
            
            # Print the extracted URLs
            for url in urls:
                print("URL:", url)
            
            # Save the URLs to a file if needed
            with open(html_filename.replace('.html', '_urls.txt'), 'w') as urls_file:
                urls_file.write('\n'.join(urls))
        
        # Save the HTML content to the file
        #with open(html_filename, "wt") as html_file:
        #    html_file.write(response.body.decode("utf-8"))

          

def start_crawler(page_number:int, save_pages_in_dir:str, start_urls:List[str]):
    crawler = CrawlerProcess()
    crawler.crawl(NewsSpider, save_pages_in_dir = save_pages_in_dir, start_urls = start_urls)
    crawler.start()


if __name__ == "__main__":
   for page_number in range(1,3):
         # Ejecutar al crawler en un proceso separado, sino al 
         # volver a arrancar con la prox pagina de indice de noticias,
         # el crawler de scrappy da error. Esto es un fix para un problema particular de scrappy.
         #process = multiprocessing.Process(target=start_crawler, args=(page_number, "/Users/achain/Documents/github/web-mining/pages", ['http://www.pagina12.com.ar/']))
         process = multiprocessing.Process(target=start_crawler, args=(page_number,  "/Users/achain/Documents/github/web-mining/url_tot", ['http://www.pagina12.com.ar/']))

         process.start()
         process.join()

