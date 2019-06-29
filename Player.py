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
from PeerToPeer import Par

class Player(threading.Thread):
    ''' Classe do jogador
    Essa classe representa o jogador local
    
    :attribute ERRORS: dicionário com os códigos de erro e strings equivalentes
    :attribute HELP: dicionário com comandos e ajuda
    '''
    ERRORS = {503: 'A sala acessada não está online'}
    HELP = {'!nickname <nickname>': 'muda o nome do usuário',
            '!sair <mensagem>': 'envia uma mensagem de despedida e desconecta'}
    def __init__ (self, name: str, port = 4400, ip = 'localhost', **kwargs):
        '''Método construtor
        :parameter name: nome de usuário
        :parameter port: número da porta local
        :parameter ip: endereço ip local
        :kwarg limite: limite de participantes na sala
        '''
        threading.Thread.__init__(self)
        self.__name = name
        self.__entrada = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__entrada.bind((port, ip))
        self.__pares = []
        self.limite = kwargs.get('limite', 0)
        self.conexoes = 0
        self.__servidor = None
    
    @property
    def name(self):
        return self.__name
    
    @name.setter
    def name(self, username):
        self.__name = username
    
    def iniciar_sala (self):
        ''' Inicia o socket self.__entrada
        
        Aguarda por conexões no socket de entrada
        '''
        self.__servidor = self
        self.__entrada.listen()
        self.start()
        while True:
            par, endereco = self.__entrada.accept()
            if self.limite and self.conexoes < self.limite:
                par.send(json.dumps({'conn': True}).encode())
                self.__pares.append(Par(par))
            else:
                par.send(json.dumps({'conn': False}).encode())
    
    def run(self):
        while True:
            msg = input("{}: ".format(self.name))
    
    def conectar_sala (self, ip_destino: str, porta_destino: int):
        ''' Método de conexão a sala existente
        
        Estabelece a conexão com a sala existente no endereço (porta_destino,
        ip_destino).
        
        :ip_destino: endereço ip de destino
        :parameter porta_destino: número da porta de destino
        '''
        try:
            servidor = (ip_destino, porta_destino)
            self.__entrada.connect(servidor)
        except:
            self.display_erro(503)
            return False
        else:
            dados = self.__entrada.recv(1024)
            conexao_aceita = json.loads(dados.decode())['conn']
            if conexao_aceita:
                print('Use o comando !help para obter ajuda')
            else:
                print('Aconteceu um problema com a sua conexão')

    def __iter__ (self):
        return iter(self.__pares)
    
    def __contains__(self, username: str):
        '''Método de verificação de nomes de usuários
        
        Verifica se algum dos usuários possui como nome o valor de username
        
        :parameter username: nome de usuário a ser verificado
        '''
        return not any(par.name == username for par in self.__pares)
    
    @property
    def servidor(self):
        ''' Verifica se o usuário é o criador da sala
        '''
        return self.__servidor == self
    
    def desconectar (self, goodbye_msg: str, par: Par):
        ''' Método do cabeçaho desconectar
        
        :parameter goodbye_msg: mensagem de despedida
        '''
        pass
    
    def texto (self, msg: str, par: Par):
        ''' Método referente ao cabeçalho 'texto'
        
        Exibe a mensagem do par
        
        :parameter mensagem: mensagem a ser impressa na tela
        :parameter par: remetente
        '''
        print ("{0}: {1}".format(Par.name, msg))
    
    def display_erro(self, code: int):
        ''' Exibe para o usuário uma mensagem de erro
        
        :parameter code: código da mensagem de erro
        '''
        print(Player.ERRORS[code])
    
    def nickname (self, nickname: str, par: Par):
        ''' Método referente ao cabeçlaho 'nickname'
        
        Faz a mudança de nome de usuário do par
        
        :parameter nickname: novo nome de usuário
        :parameter par: usuário
        '''
        if not nickname in self:
            par.name = nickname
        else:
            par.enviar_mensagem('Nome de usuário indisponível')
    
    def helper (self):
        ''' Método de ajuda
        
        Exibe para o usuário os comandos disponíveis junto com suas descrições
        '''
        
        if self.servidor:
            pass