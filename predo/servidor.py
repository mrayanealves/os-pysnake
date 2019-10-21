import socket
import threading
import socketserver
import math
import random
import pygame
import tkinter as tk
from tkinter import messagebox
import queue
import json

class cube(object):
    rows = 20
    w = 500

    def __init__(self, start, dirnx=1, dirny=0, color=(255, 255, 255)):
        self.pos = start
        self.dirnx = 1
        self.dirny = 0
        self.color = color

    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)

    def draw(self, surface, eyes=False):
        dis = self.w // self.rows
        i = self.pos[0]
        j = self.pos[1]

        pygame.draw.rect(surface, self.color, (i*dis+1, j*dis+1, dis-2, dis-2))
        if eyes:
            centre = dis//2
            radius = 3
            circleMiddle = (i*dis+centre-radius, j*dis+8)
            circleMiddle2 = (i*dis + dis - radius*2, j*dis+8)
            pygame.draw.circle(surface, (255, 255, 255), circleMiddle, radius)
            pygame.draw.circle(surface, (255, 255, 255), circleMiddle2, radius)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)

class snake(object):
    
    turns = {}

    def __init__(self, color, pos):
        self.color = color
        self.head = cube(pos,color=color)
        self.body =[]
        self.body.append(self.head)
        self.dirnx = 0
        self.dirny = 1

    def move(self):
        global receber_direcoes
   
        keys = receber_direcoes
        if not keys: 
            return

        print("keys: " + keys)

        if keys == "2e":
            self.dirnx = -1
            self.dirny = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        elif keys == "2d":
            self.dirnx = 1
            self.dirny = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        elif keys == "2c":
            self.dirnx = 0
            self.dirny = -1
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        elif keys == "2b":
            self.dirnx = 0
            self.dirny = 1
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        for i, c in enumerate(self.body):
            p = c.pos[:]
            if p in self.turns:
                turn = self.turns[p]
                c.move(turn[0], turn[1])
                if i == len(self.body)-1:
                    self.turns.pop(p)
            else:
                if c.dirnx == -1 and c.pos[0] <= 0:
                    c.pos = (c.rows-1, c.pos[1])
                elif c.dirnx == 1 and c.pos[0] >= c.rows-1:
                    c.pos = (0, c.pos[1])
                elif c.dirny == 1 and c.pos[1] >= c.rows-1:
                    c.pos = (c.pos[0], 0)
                elif c.dirny == -1 and c.pos[1] <= 0:
                    c.pos = (c.pos[0], c.rows-1)
                else:
                    c.move(c.dirnx, c.dirny)
        receber_direcoes = ""
    def reset(self, pos):
        self.head = cube(pos)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1

    def addCube(self):

        cor = self.color

        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny

        if dx == 1 and dy == 0:
            self.body.append(cube((tail.pos[0]-1, tail.pos[1]), color=cor))
        elif dx == -1 and dy == 0:
            self.body.append(cube((tail.pos[0]+1, tail.pos[1]),color=cor))
        elif dx == 0 and dy == 1:
            self.body.append(cube((tail.pos[0], tail.pos[1]-1),color=cor))
        elif dx == 0 and dy == -1:
            self.body.append(cube((tail.pos[0], tail.pos[1]+1),color=cor))

        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy

    def draw(self, surface):
        for i, c in enumerate(self.body):
            if i == 0:
                c.draw(surface, True)
            else:
                c.draw(surface)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)

def randomSnack(rows, item):

    positions = item.body

    while True:
        x = random.randrange(rows)
        y = random.randrange(rows)
        if len(list(filter(lambda z: z.pos == (x, y), positions))) > 0:
            continue
        else:
            break

    return (x, y)

def tratarCliente(clientsocket, adress):
    
    while True:
        msg_cliente = clientsocket.recv(1024).decode("utf-8") 

        for i in range(0,len(lista_sockets)):
            if(adress != lista_adresses[i]): 
                lista_sockets[i].send(bytes(msg_cliente,"utf-8"))        
                print(msg_cliente)

        if not msg_cliente: 
            clientsocket.close()  
            lista_sockets.remove(clientsocket)
            break

global receber_direcoes
global snack
lista_sockets = []
lista_adresses = []
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.bind(("localhost",5551))
print("Escutando...")
s.listen(2)

list_snake = []
list_snack = []

while True:
    clientsocket, adress = s.accept()
    print("Servidor recebeu concexao de {}".format(adress))
    list_snake.append(snake((255, 0, 250), (10, 11)))
    list_snack.append(cube(randomSnack(200, list_snake[0]), color=(0, 255, 0)))

    lista_sockets.append(clientsocket)
    lista_adresses.append(adress)

    msg_snakes = "start;"+"snakes"

    for snake in list_snake:
        msg_snakes += ";" + snake.toJSON()

    print(msg_snakes)

    clientsocket.sendall(bytes(msg_snakes,"utf-8"))
    clientsocket.recv(1024).decode("utf-8")
    msg_snacks = "start;"+"snacks"

    for snacks in list_snack:
        msg_snacks += ";" + snacks.toJSON()

    clientsocket.sendall(bytes(msg_snacks,"utf-8"))
    print(msg_snacks)
    clientsocket.recv(1024).decode("utf-8")
    msg_id = "start;id;"+ str(len(list_snake) - 1)

    print(msg_id)
    clientsocket.sendall(bytes(msg_id,"utf-8"))
    
    t = threading.Thread(target=tratarCliente,args=(clientsocket, adress))
    t.daemon = True # vai acabar a thread quando fecharmos o programa
    t.start()
    




    
    
