#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 15:05:18 2020

@author: alvaro

Este código tem o objetivo de fazer download de dados do site do IBGE

http://ftp.dadosabertos.ans.gov.br/FTP/PDA/informacoes_consolidadas_de_beneficiarios/


----------------------------
Melhorias: 
    -

"""
import requests as r
from bs4 import BeautifulSoup as bs
import os

## abrir a página e obter os links de cada arquivo que se deseja baixar


def pega_complemento(link):
    """
    Esta função busca abre o link desejado da página de FTP do IBGE e retorna o
complemento de acesso das paginas seguintes

    Parameters
    ----------
    link :  - str
            - Link da página que se quer extrair os complementos

    Returns
    -------
    a_list: - list
            - Lista de str contendo os complementos das páginas seguintes para 
            navegação. Para acessar o complemento da página contido em a_list
            deve-se:
                a_list[x]['href']
            tal que 'x' é a posição do elemento na lista
    """
    
    site = r.get(link)

    if site.status_code == r.codes.OK:
        soup = bs(site.content, 'html.parser')
        a_list = soup.find_all('a')
    
    return a_list
  

def download_arquivo(url, path):
    """
    Esta função baixa o arquivo do endereço desejado (url) e o salva no 
    caminho de rede especificado em "path".
    ref.:
        https://pythoncafe.com.br/post/baixando-arquivos-da-internet/

    Parameters
    ----------
    url :   - str
            - endereço do elemento que se deseja baixar
    path :  - str
            - Caminho da rede no qual se deseja salvar o arquivo.

    Returns
    -------
    None.

    """
    link = r.get(url)
    if link.status_code == r.codes.OK:
        with open(path, 'wb') as n_file:
            print('Iniciando download ...')
            n_file.write(link.content)
        print('Download concluido!')
        print('Arquivo salvo em: %s'%path)
    else:
        link.raise_for_status()
    
    
    
def main(path):
    """
    Função principal que navega até a página que contém o link desejado a 
partir das informações consolidads de benefíciários e baixa o conteúdo para um
caminho desejado.

    Parameters
    ----------
    path:   - str
            - Caminho da rede onde deseja se salvar os arquivos baixados

    Returns
    -------
    None.

    """
    link = 'http://ftp.dadosabertos.ans.gov.br/FTP/PDA/informacoes_consolidadas_de_beneficiarios/'
    a_periodo = pega_complemento(link)
    
    for i in range(5,len(a_periodo)):
        compl_1 = a_periodo[i]['href'] #pega o complemento do link
        n_link = link + compl_1
        
        a_file = pega_complemento(n_link)
        
        # Criar a pasta para armazenar os arquivos contidos no link do comp_1
        try:
            os.mkdir(compl_1)
        except FileExistsError:
            print('FileExistsError: Pasta "%s" já existe!'%compl_1)
            
        # Navegar até a pasta em que serão armazenados os dados baixados
        n_path = path+'/'+compl_1
        os.chdir(n_path)
        
        for j in range(5,len(a_file)):
            compl_2 = a_file[j]['href']
            fl_link = n_link + compl_2
            
            #caminho da rede em que será salvo o novo arquivo
            f_path = n_path+compl_2
            download_arquivo(fl_link, f_path)
        
        # Retornar à pasta raiz "path"
        os.chdir(path)
            
    
if __name__ == '__main__':
    path = '/home/alvaro/Documentos/Alvaro/Estudos_Python/BootCamp_Alura/extracao_dados_ibge'
    main(path)
    
    