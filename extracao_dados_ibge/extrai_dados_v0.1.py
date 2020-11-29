#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 15:05:18 2020

@author: alvaro

Este código tem o objetivo de fazer download de dados do site do IBGE

http://ftp.dadosabertos.ans.gov.br/FTP/PDA/informacoes_consolidadas_de_beneficiarios/


----------------------------
Versões:
    /       -Versão original
    0.1     - Modificação para não baixar dados do site e abrir direto o arquivo
    
Melhorias: 
    -

"""
import requests as r
from bs4 import BeautifulSoup as bs
import os
import pandas as pd

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
    

def abre_beneficiarios(url):
    """
    Esta função abre direto o arquivo do site de informações consolidadas de 
    beneficiários e abre como pandas um dataframe do pandas

    link:
        http://ftp.dadosabertos.ans.gov.br/FTP/PDA/informacoes_consolidadas_de_beneficiarios/
        
    Parameters
    ----------
    url :   - str
            - Endereço do arquivo que será aberto
    

    Returns
    -------
    df:     - pandas.DataFrame()
            - dataFrame do Pandas contendo os informes de beneficiários de planos 
            de saúde

    """
    df = pd.read_csv(url, compression='zip', sep=';', encoding='iso-8859-1')
    
    return df

def abre_proj_pop(path):
    """
    Esta função abre o arquivo CSV contendo os municípios 
    

    Parameters
    ----------
    path :  - str
            - Endereço do arquivo que será aberto


    Returns
    -------
    df:     - pandas.DataFrame()
            - dataFrame do Pandas contendo os informes de projeção populacional
            por município do Brasil

    """
    ##### Carregar dataframe
    df = pd.read_csv(path, sep=';', encoding='iso-8859-1', 
                     skiprows=3, skipfooter=4)
    
    ##### Criar coluna de cód. IBGE
    df['cod_ibge'] = df['Município'].str[:6]
    # transformar cód. IBGE em int
    temp = df['cod_ibge'].tolist()
    temp[-1] = 0
    df['cod_ibge'] = temp
    df['cod_ibge'] = df['cod_ibge'].astype(int)
    
    ##### Criar coluna de nome de município
    df['nome_municipio'] = df['Município'].str[7:].tolist()
    
    
    return df
    
def modif_beneficiarios(df):
    """
    Esta função modifica os grupos de beneficiários para que coincidam com os 
    grupos etários dos dados de projeção de população por município do IBGE.

    Parameters
    ----------
        df:     - pandas DataFrame
                - Dataframe do Pandas contendo as informações de beneficiários de 
                plano de saúde para as cidades de cada estado.
        
    Returns
    -------
        df_mod  - pandas DataFrame
                - DataFrame do Pandas com o conteúdo de dados modificado em com
                possibilidade de ser colocado em um db
    """
    # Dicionário de unificação de grupos etários
    grupos = {
              '00 a 05 anos': ['00 a 05 anos'], 
              '06 a 10 anos': ['06 a 10 anos'],
              '11 a 15 anos': ['11 a 15 anos'], 
              '16 a 20 anos': ['16 a 20 anos'], 
              '21 a 30 anos': ['21 a 25 anos', '26 a 30 anos'], 
              '31 a 40 anos': ['31 a 35 anos', '36 a 40 anos'], 
              '41 a 50 anos': ['41 a 45 anos', '46 a 50 anos'], 
              '51 a 60 anos': ['51 a 55 anos', '56 a 60 anos'],
              '61 ou mais': ['61 ou mais']
               }
    
    
    df_mod = pd.DataFrame()
    for cod_ibge in df['CD_MUNICIPIO'].unique():
        dic_db = {} # dic que será usado para incluir dados no df modificado
        dic_db['cod_ibge'] = cod_ibge
        dic_db['city'] = df.loc[df['CD_MUNICIPIO'] == cod_ibge, 
                                'NM_MUNICIPIO'].unique()[0]
        dic_db['uf'] = df.loc[df['CD_MUNICIPIO'] == cod_ibge, 
                              'SG_UF'].unique()[0]
        
        # print(dic_db)
        
        df_filtro_ibge = df.query(f'CD_MUNICIPIO == {cod_ibge}')
        for cnpj in df_filtro_ibge['NR_CNPJ'].unique():
            dic_db['cnpj'] = cnpj
            dic_db['cod_oper'] = df_filtro_ibge.loc[df['NR_CNPJ'] == cnpj,
                                                    'CD_OPERADORA'].unique()[0]
            dic_db['operadora'] = df_filtro_ibge.loc[df['NR_CNPJ'] == cnpj,
                                                     'NM_RAZAO_SOCIAL'].unique()[0]
            dic_db['modalidade'] = df_filtro_ibge.loc[df['NR_CNPJ'] == cnpj,
                                                      'MODALIDADE_OPERADORA'].unique()[0]

            df_filtro_cnpj = df_filtro_ibge.query(f'NR_CNPJ == {cnpj}')
            df_grupo_idade = df_filtro_cnpj.groupby('DE_FAIXA_ETARIA')[['QT_BENEFICIARIO_ATIVO', 'QT_BENEFICIARIO_ADERIDO', 'QT_BENEFICIARIO_CANCELADO']].sum()

            for key in list(grupos.keys()):
                clientes = pd.Series(
                                     {
                                      'QT_BENEFICIARIO_ATIVO':0,
                                      'QT_BENEFICIARIO_ADERIDO':0,
                                      'QT_BENEFICIARIO_CANCELADO':0
                                      }
                                     )
                for val in grupos[key]:
                    if val in df_grupo_idade.index:
                        clientes += df_grupo_idade.loc[val]
                
                    for i in range(len(clientes)):
                        dic_db['tipo'] = clientes.index[i]
                        dic_db['qtd'] = clientes[i]
                        
                        df_mod = df_mod.append(dic_db, ignore_index=True)
                

    return df_mod

def main_test():
    """
    Função de teste de novas funções
    Parameters
    ----------    
    None.
    
    Returns
    -------
    None.

    """
    #### Carregar lista de beneficiários
    link_benef = 'https://github.com/alcarnielo/Bootcamp_Alura/blob/main/extracao_dados_ibge/ben202009_AC.zip?raw=true'
    beneficiarios = abre_beneficiarios(link_benef)
    
    #### Carregar lista de municípios e projeção populacional
    link_proj_pop = 'https://raw.githubusercontent.com/alcarnielo/Bootcamp_Alura/main/extracao_dados_ibge/proj_pop_f_etaria_1_2020.csv'
    proj_populacao = abre_proj_pop(link_proj_pop)
    
    #### Modifica o df de beneficiários
    beneficiarios_mod = modif_beneficiarios(beneficiarios)
    print(beneficiarios_mod)
    
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
    # path = '/home/alvaro/Documentos/Alvaro/Estudos_Python/BootCamp_Alura/extracao_dados_ibge'
    # main(path)
    main_test()
    
    