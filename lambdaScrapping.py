from difflib import restore
from importlib.resources import contents
from time import sleep
from bs4 import BeautifulSoup
import requests
import csv
import re


def extrair_participantes(paginaPodcast):
    participantes = []

    stringProcurada = re.compile(r"Participantes:")

    title = paginaPodcast.find('p', text=stringProcurada)

    if title == None:
        title = paginaPodcast.find('span', text=stringProcurada)

    if title == None:
        return participantes

    listaParticipantes = title.find_next('ul').find_all('li')
    for convidado in listaParticipantes:
        nomeParticipante = convidado.text.split('–')
        participantes.append(nomeParticipante[0].rstrip())

    return participantes


def extrair_links_podcasts(paginaListaPodcasts):
    linksPodcasts = []
    listaPodcasts = paginaListaPodcasts.find_all('div', class_='cast-item')
    for podcast in listaPodcasts:
        linksPodcasts.append(podcast.find('a', href=True)['href'])

    return linksPodcasts


def cria_dict_podcasters(listaPodcasters):
    dictPodcasters = {}
    for podcaster in listaPodcasters:
        if podcaster in dictPodcasters:
            dictPodcasters[podcaster] += 1
        else:
            dictPodcasters[podcaster] = 1

    return dictPodcasters


def salva_dict_csv(dictPodcasters):
    with open('contagem_podcasters.csv', 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in dictPodcasters.items():
            writer.writerow([key, value])


participantes = []
retorno = []
tempo_delay = 4
rangePaginasPodcasts = range(1, 29)
for numeroPagina in rangePaginasPodcasts:
    urlPodcast = 'https://www.lambda3.com.br/category/podcast/page/%s/' % numeroPagina
    print('**', urlPodcast, '**')
    response = requests.get(urlPodcast)
    sleep(tempo_delay)
    lambdaPage = BeautifulSoup(response.content, 'html.parser')
    listaLinksPodcasts = extrair_links_podcasts(lambdaPage)

    contador = 0
    for link in listaLinksPodcasts:
        contador += 1
        paginaPodcast = requests.get(link)
        sleep(tempo_delay)
        retorno = extrair_participantes(BeautifulSoup(
            paginaPodcast.content, 'html.parser'))

        if len(retorno) > 0:
            print('->', link)
            participantes += retorno
        else:
            print('->', link, '(ERRO: Não foi possível carregar os participantes)')

        print(f'Podcast {contador} de {len(listaLinksPodcasts)}', end='\r')


dictPodcasters = cria_dict_podcasters(participantes)
salva_dict_csv(dictPodcasters)
