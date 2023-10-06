

# -*- coding: utf-8 -*-
"""
Este script transforma un grupo de paginas html, agrupadas en directorios, a 1 directorio por categoria, en un dataset para entrenar.
Espera que haya 1 directorio por categoria dentro del directorio padre cuyo path esta en la variable DIR_BASE_CATEGORIAS. Usa el nombre del directorio como nombre de la categoria.
"""
from sklearn.feature_extraction.text import CountVectorizer
from bs4 import BeautifulSoup
import re
import os
import joblib
from typing import Pattern, Optional, List, Tuple
import json

# Este es el path COMPLETO del directorio que contiene a 1 subdirectorio por cada categoria; adentro de esos subdirs estan los html
#hay que ir cambiando el final por eco, el-pai , socie, el-mun

# este es el texto que tiene que aparecer en las notas, antes del texto de la nota
MARCADOR_COMIENZO_INTERESANTE="class=\"article-text\""
# este es el texto que tiene que aparecer en las notas, despues del texto de la nota
MARCADOR_FIN_INTERESANTE="div class=\"share"
extractor_de_parte_de_html_que_interesa = re.compile(re.escape(MARCADOR_COMIENZO_INTERESANTE) + "(.+)" + re.escape(MARCADOR_FIN_INTERESANTE))


def extraer_parte_que_interesa_de_html(regex:Pattern, texto:str) -> Optional[str]:
    """
    Usa una expresion regular con 1 grupo de captura para extraer una parte de un texto.
    :param regex:
    :param texto:
    :return: El texto extraido. Si no pudo extraer nada, retorna None.
    """
    #quitar todos los fines de linea para que la regex funcione sin importar como estaba dividido el html
    match = regex.search(texto.replace("\n",""))
    return match.group(1) if match is not None else None


def pasar_html_a_texto(html_doc:str) -> Optional[str]:
    """
    Recibe el HTML de una nota, corta una parte del html usando la regex 'extractor_de_parte_de_html_que_interesa', y y retorna el texto de esa parte, descartando todos los tags de html.
    :param html_doc:  HTML de una nota
    :return: El texto extraido de la nota, o None si no encontro texto para extraer.
    """
    html_que_interesa = extraer_parte_que_interesa_de_html(extractor_de_parte_de_html_que_interesa, html_doc)
    if html_que_interesa is not None:
        # beautifulsoup hace todo el trabajo de ignorar los tags de html y convertir las entidades (p.ej. &ntilde;) a letras (p.ej. ñ)
        extractor_html = BeautifulSoup(html_que_interesa, 'html.parser')
        texto = extractor_html.get_text(separator=" ", strip=True)
        return texto
    else:
        return "error"
    

def leer_archivo(path:str) -> str:
    return open(path,"rt").read()
# Define the categories and their corresponding directories
categories = ["eco", "el-pai", "socie", "el-mun"]

# Loop through each category
for category in categories:
    # Define the directory for the current category
    DIR_BASE_CATEGORIAS = f'/Users/achain/Documents/github/bert_classification_new/pages/{category}'


    htmls = []
    for archivo_html in os.listdir(DIR_BASE_CATEGORIAS):
        path_completo_html = os.path.join(DIR_BASE_CATEGORIAS, archivo_html)
        try:
             with open(path_completo_html,"r", encoding="UTF-8") as fecha:
                        html_content = fecha.read()
                        # Parse the HTML content
                        soup = BeautifulSoup(html_content, 'html.parser')
                        # Find all <script> tags with type="application/ld+json"
                        script_tags = soup.find_all('script', type='application/ld+json')
                        date_published = None
                        # Loop through the script tags and look for the one with "datePublished"
                        for script_tag in script_tags:
                            try:
                                # Parse the JSON data within the <script> tag
                                data = json.loads(script_tag.string)

                                # Check if the JSON data has a "datePublished" key
                                if 'datePublished' in data:
                                    date_published = data['datePublished']
                                    break
                            except json.JSONDecodeError:
                                pass  
        except Exception as e:
                print("Error while processing {}: {}".format(path_completo_html, str(e)))

        if os.path.isfile(path_completo_html):
            try:
                with open(path_completo_html, "r", encoding="UTF-8") as file:

                    texto = pasar_html_a_texto(file.read())
                    if texto is not None:
                        htmls.append(texto)
                        with open(f'/Users/achain/Documents/github/bert_classification_new/pages/{category}_content_plain/{date_published}{archivo_html}.txt', 'w', encoding='utf-8') as file:
                            file.write(texto)  # Save the article content
                    else:
                        print("CUIDADO! No fue posible extraer el texto de la nota del archivo {}".format(path_completo_html))
            except Exception as e:
                print("Error while processing {}: {}".format(path_completo_html, str(e)))
