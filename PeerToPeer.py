# -*- coding: utf-8 -*-
"""
Universidade Federal de Pernambuco (UFPE) (http://www.ufpe.br)
Centro de Informática (CIn) (http://www.cin.ufpe.br)
Bacharelado em Sistemas de Informacao
IF 969 - Algoritmos e Estruturas de Dados
Authors: Adriana Alves dos Santos (aas8) and Luana Mayara Santos Ribeiro (lmsr)
The MIT License (MIT)
Copyright(c) 2019

"""

import threading
import socket
import json
from Player import Player

class Par (threading.Thread):
    def __init__ (self, socket: socket.socket, servidor: Player):
        ''' Método construtor da classe Par
        
        :parameter socket: socket pelo qual o par se comunica
        :parameter servidor: servidor
        '''
        threading.Thread.__init__(self)
        self.__socket = socket
        self.__servidor = servidor
        self.__name = ''
        
        self.start()
    
    @property
    def name (self):
        '''
        getter to nome de usuário
        
        :returns self.__name:
        '''
        return self.__name
    
    @name.setter
    def name(self, username: str):
        '''
        setter do nome de usuário
        
        :parameter username: novo nome 
        '''
        self.__name = username
    
    def run (self):
        ''' Método principal da Thread
        
        Monitora o socket a espera de mensagens do par. Quando uma mensagem é
        recebida, trata a mensagem de acordo com cada um dos cabeçalhos.
        '''
        self.enviar_mensagem('Conexão Aceita!')
        while True:
            try:
                dados = self.__socket.recv(1024)
            except:
                continue
            else:
                if dados:
                    self.receber_mensagem(dados)
                    _json = json.loads(dados.decode())
                    for header in _json:
                        getattr(self.__servidor, header)(_json[header], self)
                else:
                    break
        self.desconectar()
    
    def enviar_mensagem (self, mensagem = '', **comandos):
        ''' Método de envio de mensagens
        
        Recebe um dicionário e envia um JSON para o par
        
        :parameter mensagem: mensagem a ser enviada e exibida para o Par
        :parameters mensagens: dicionário que comandos a serem enviados
        '''
        if mensagem:
            comandos['texto'] = mensagem
        dados = json.dumps(comandos)
        self.__socket.send(dados.encode())