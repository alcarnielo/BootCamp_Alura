#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  7 07:22:17 2020

@author: alvaro

    Esse programa tem o objetivo de abrir um arquivo no formato zip e lê-lo na 
forma de dataFrame do Pandas

versões:
    0.000 - Versão original
"""
import pandas as pd
import os, zipfile

def descompacta(path_orig, fl_name, path_dest, cria_pasta=False):
    """
    Esta função tem o objetivo de descompactar arquivos do "path_orig" para o
path_dest.

    Parameters
    ----------
    path_orig:  - str
                - str com o caminho de rede que contém o arquivo que se deseja 
                descompactar
                Nota:
                    O caminho path origem é o caminho de uma pasta de rede e 
                    não do arquivo ".zip"

    fl_name:    - str
                - str contendo o nome do arquivo que se deseja descompactar
                
    path_dest:  - str
                - str com o caminho de destino do arquivo que será extraido
                Nota:
                    no caminho destino será criada uma pasta onde será salvo o
                    conteúdo do arquivo compactado

    Returns
    -------
    None.
    ref.:
          http://oitavobit.com.br/lendo-extraindo-e-acrescentando-arquivos-zip-com-python/#:~:text=Extraindo%20(descompactando)%20arquivos%20ZIP%20com%20o%20Python&text=Voc%C3%AA%20tamb%C3%A9m%20pode%20extrair%20um,pasta%20'c%3A%5Cdestino'. 
    """
    # Navegar até o arquivo que se deseja descompactar
    os.chdir(path_orig)
    # Ler arquivo zip
    try:
        fl_zip = zipfile.ZipFile(fl_name)
        # listar arquivos compactados em fl_zip
        fl_zip_list = fl_zip.namelist()
        print(fl_zip_list)
        os.chdir(path_dest)     # muda para pasta destino
        
        # criar pasta de destino do arquivo zip
        if cria_pasta:
            folder_name = path_orig.split('/')[-1].split('.')[0] # pega o último elemento do caminho origem e utiliza ele sem ".zip"
            os.mkdir(folder_name)   # cria pasta para os arquivos que serão descompactados
            os.chdir(folder_name)   # muda para a pasta criada
        
        fl_zip.extractall()     # extrai os arquivos 
        fl_zip.close()          # fecha o arquivo zip
    except zipfile.BadZipFile:
        print('Arquivo não é zip')
    

def main(path):
    
    os.chdir(path)
    # listar as pastas dentro do diretório que se deseja navegar
    folder = os.listdir()
    # navegar pelas pastas do diretório
    for i in range(len(folder)):
        os.chdir(folder[i])
        # listar os arquivos dentro da pasta folder[i]
        fl_list = os.listdir()
        # descompactar os arquivos
        for j in range(len(fl_list)):
            descompacta('.', fl_list[j], '.')
        # retorna à pasta original [path]
        os.chdir(path)

if __name__ == '__main__':
    path = '/home/alvaro/Documentos/Alvaro/Estudos_Python/BootCamp_Alura/extracao_dados_ibge'
    main(path)
    