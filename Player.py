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
    '''
    ERRORS = {503: 'A sala acessada não está online'}
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
        self.__entrada.bind((ip, port))
        self.__pares = []
        self.__limite = kwargs.get('limite', 0)
        self.conexoes = 0
        self.__admin = None
    
    @property
    def limite(self):
        return self.__limite
    
    @limite.setter
    def limite(self, limite: int):
        self.__limite = limite
    
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
        self.__admin = self
        self.__entrada.listen()
        self.start()
        self.__esperar()

    def conectar_sala (self, ip_destino: str, porta_destino: int):
        ''' Método de conexão a sala existente
        
        Estabelece a conexão com a sala existente no endereço (porta_destino,
        ip_destino).
        
        :ip_destino: endereço ip de destino
        :parameter porta_destino: número da porta de destino
        '''
        try:
            servidor = socket.socket()
            servidor.bind((self.__entrada.getsockname()[0], 0))
            servidor.connect((ip_destino, porta_destino))
            self.__entrada.listen()
        except:
            self.display_erro(503)
        else:
            conexao_aceita = json.loads(servidor.recv(1024).decode())['conn']
            if conexao_aceita:
                print('Use o comando !help para obter ajuda')
                mine = {'address': self.__entrada.getsockname()}
                servidor.send(json.dumps(mine).encode())
                settings = json.loads(servidor.recv(1024).decode())
                self.limite = settings['limite']
                self.__admin = Par(servidor, self)
                self.__pares.append(self.__admin)
                self.start()
                self.__esperar()
            else:
                print('Aconteceu um problema com a sua conexão')
    
    def __esperar(self):
        ''' Método de espera
        '''
        while self.__admin is not None:
            par, endereco = self.__entrada.accept()
            if self.limite and self.conexoes >= self.limite:
                par.send(json.dumps({'conn': False}).encode())
            elif self.admin:
                par.send(json.dumps({'conn': True}).encode())
                address = json.loads(par.recv(1024).decode())['address']
                par.send(json.dumps({'limite': self.limite}).encode())
                for p in self.__pares:
                    p.enviar_mensagem(new_peer = address)
                cliente = Par(par, self)
                cliente.enviar_mensagem(nickname = self.name)
                self.__pares.append(cliente)
                self.conexoes += 1
                print("{} conectado.".format(self.__pares[-1].name))
            else:
                par.send(json.dumps({'conn': True}).encode())
                p = Par(par, self)
                p.enviar_mensagem(nickname = self.name)
                self.__pares.append(p)
                
    
    def run(self):
        self.broadcast(nickname = self.__name)
        while True:
            user_input = input("{}: ".format(self.name))                
            self.broadcast(**tokenizar_comandos(user_input))
    
    def new_peer(self, address, par: Par):
        ''' Cria uma nova conexão a partir do endereço fornecido pelo admin
        '''
        if par is self.__admin:
            novo_par = socket.socket()
            novo_par.bind(('localhost', 0))
            novo_par.connect(tuple(address))
            conexao_aceita = json.loads(novo_par.recv(1024).decode())
            if conexao_aceita:
                self.__pares.append(Par(novo_par, self))
            else:
                print("Não conseguiu se conectar a um dos pares")
            
    
    def broadcast (self, **comandos):
        ''' Faz o broadcast dos comandos para todos os pares
        
        :comandos: dicionário de comandos
        ''' 
        for par in self:
            par.enviar_mensagem(**comandos)

    def __iter__ (self):
        return iter(self.__pares)
    
    def __contains__(self, address: tuple):
        '''Método de verificação de nomes de usuários
        
        Verifica se algum dos usuários possui como nome o valor de username
        
        :parameter address: tupla contendo ip e porta
        '''
        return any(par.address == address for par in self.__pares)
    
    @property
    def admin(self):
        ''' Verifica se o usuário é o criador da sala
        '''
        return self.__admin == self
    
    def sair (self, goodbye_msg: str, par: Par):
        ''' Método do cabeçaho desconectar
        
        :parameter goodbye_msg: mensagem de despedida
        '''
        self.texto(goodbye_msg, par)
        self.desconectar(par)
    
    def texto (self, msg: str, par: Par):
        ''' Método referente ao cabeçalho 'texto'
        
        Exibe a mensagem do par
        
        :parameter mensagem: mensagem a ser impressa na tela
        :parameter par: remetente
        '''
        nome = par.name
        if par is self.__admin: nome = "[ADMIN]{}".format(nome)
        print ("{0}: {1}".format(par.name, msg))
    
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
        if not any(p.name == nickname for p in self.__pares):
            print("{} mudou seu nome para {}".format(par.name, nickname))
            par.name = nickname
        else:
            par.enviar_mensagem('Nome de usuário indisponível')
    
    def helper (self):
        ''' Método de ajuda
        
        Exibe para o usuário os comandos disponíveis junto com suas descrições
        '''
        pass
    
    def __clear(self, confirmation, reconfirmation):
        if confirmation ==  reconfirmation:
            self.__entrada.close()
    
    def desconectar (self, par: Par):
        ''' Método de desconexão de um par.
        
        :parameter par: Par desconectado
        '''
        print('{} saiu.'.format(par.name))
        self.__pares.remove(par)

def tokenizar_comandos(string):
    ''' Trata os comandos do usuário
    
    Trata as strings inseridas pelo usuário, identificando comandos iniciados
    por "!" e criando um dicionário com os comandos específicos.
    
    :parameter string: input do usuário
    :returns dicio: dicionário de comandos
    '''
    tokens = string.split(' ')
    parametros = []
    limite = len(tokens)
    i = 0
    dicio = {}
    while i < limite:
        comando = ''
        if tokens[i].startswith('!'):
            comando = tokens[i].strip('!')
            parametros = []
            i+=1
            
        while not tokens[i].startswith('!'):
            parametros.append(tokens[i])
            i += 1
            if i>= limite: break
        
        if not comando: comando = 'texto'
        dicio[comando] = ' '.join(parametros)
        
    return dicio