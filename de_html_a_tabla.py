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
from tokenizers import tokenizador, tokenizador_con_stemming

STOPWORDS_FILE = "stopwords_es.txt"
STOPWORDS_FILE_SIN_ACENTOS = "stopwords_es_sin_acentos.txt"
# Este es el path COMPLETO del directorio que contiene a 1 subdirectorio por cada categoria; adentro de esos subdirs estan los html
DIR_BASE_CATEGORIAS = "/home/fernando/lanacion"

# este es el texto que tiene que aparecer en las notas, antes del texto de la nota
MARCADOR_COMIENZO_INTERESANTE="<p class=\"capital\">"
# este es el texto que tiene que aparecer en las notas, despues del texto de la nota
MARCADOR_FIN_INTERESANTE="<div class=\"banner middle-3 b-desktop"
extractor_de_parte_de_html_que_interesa = re.compile(re.escape(MARCADOR_COMIENZO_INTERESANTE) + "(.+)" + re.escape(MARCADOR_FIN_INTERESANTE))



# cantidad minima de docs que tienen que tener a un token para conservarlo.
MIN_DF=3
# cantidad maxima de docs que tienen que tener a un token para conservarlo.
MAX_DF=0.8

# numero minimo y maximo de tokens consecutivos que se consideran
MIN_NGRAMS=1
MAX_NGRAMS=2

VECTORS_FILE = "vectores.joblib"
TARGETS_FILE = "targets.joblib"
FEATURE_NAMES_FILE = "features.joblib"


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
        return None


def leer_archivo(path:str) -> str:
    return open(path,"rt").read()

def leer_stopwords(path:str) -> List[str]:
    with open(path,"rt") as stopwords_file:
        return [stopword for stopword in [stopword.strip().lower() for stopword in stopwords_file] if len(stopword)>0 ]


def htmls_y_target(dir_de_1_categoria:str) -> Tuple[List[str],List[str]]:
    """
    Lee todos los archivos html en el directorio, y retorna un par([lista de html],[lista de categoria]).
    El nombre del directorio se usa como categoria.
    :param dir_de_1_categoria: Path completo del directorio de donde leer archivos html.
    :return: un par([lista de html],[lista de categorias]) donde a cada html le corresponde la misma categoria, asignada en base al nombre del directorio..
    """
    htmls = []
    for archivo_html in os.listdir(dir_de_1_categoria):
        path_completo_html = os.path.join(dir_de_1_categoria, archivo_html)
        if os.path.isfile(path_completo_html):
            texto = pasar_html_a_texto(leer_archivo(path_completo_html))
            if texto is not None:
                htmls.append(texto)
            else:
                print("CUIDADO! No fue posible extraer el texto de la nota del archivo {}".format(path_completo_html))
    target_class = [dir_por_categoria] * len(htmls)
    return htmls, target_class


if __name__ == "__main__":

    todos_lost_htmls = []
    todos_los_targets = []

    # armar una lista con todos los suddirectorios de DIR_BASE_CATEGORIAS
    un_dir_por_categoria = [subdir for subdir in os.listdir(DIR_BASE_CATEGORIAS) if os.path.isdir(os.path.join(DIR_BASE_CATEGORIAS, subdir))]
    # recorrer c/u de los subdirectorios dentro de DIR_BASE_CATEGORIAS, y extraer el texto de c/ archivo html en cada subdirectorio. La categoria asignada
    # a cada html sera el nombre del subdirectorio que lo contiene.
    for dir_por_categoria in un_dir_por_categoria:
        htmls, targets  = htmls_y_target(os.path.join(DIR_BASE_CATEGORIAS, dir_por_categoria))
        todos_lost_htmls.extend(htmls)
        todos_los_targets.extend(targets)

    mi_lista_stopwords = leer_stopwords(STOPWORDS_FILE_SIN_ACENTOS)
    mi_tokenizer = tokenizador()
    vectorizer = CountVectorizer(stop_words=mi_lista_stopwords, tokenizer=mi_tokenizer,
                                 lowercase=True, strip_accents='unicode', decode_error='ignore',
                                 ngram_range=(MIN_NGRAMS, MAX_NGRAMS), min_df=MIN_DF, max_df=MAX_DF)

    # fit = tokenizar y codificar documentos como filas
    todos_lost_vectores = vectorizer.fit_transform(todos_lost_htmls)
    # guardar vectores de docs y la correspondiente categoria asignada a cada doc.
    joblib.dump(todos_lost_vectores, VECTORS_FILE)
    joblib.dump(todos_los_targets, TARGETS_FILE)
    print("Finalizado, el dataset está en {} y {}.".format(VECTORS_FILE, TARGETS_FILE))
    nombres_features = vectorizer.get_feature_names()
    joblib.dump(nombres_features, FEATURE_NAMES_FILE)
    print("El nombre de cada columna de features esta en {}.".format(FEATURE_NAMES_FILE))
