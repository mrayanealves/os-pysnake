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
import time

lista_sockets = []
lista_adresses = []
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.bind(("localhost",5552))
print("Escutando...")
s.listen(2)

list_snake = []
list_snack = []

class Cube(object):
    rows = 20
    w = 500

    def __init__(self, start, dirnx=1, dirny=0, color=(255, 255, 255)):
        self.pos = tuple(start)
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

class Snake(object):
    
    turns = {}

    def __init__(self, color, pos):
        self.color = color
        self.head = Cube(pos,color=color)
        self.body =[]
        self.body.append(self.head)
        self.dirnx = 0
        self.dirny = 1
        self.lastDirection = 'none'

    def move(self, direction):
        if direction == "none":
            return

        if direction == "left":
            self.dirnx = -1
            self.dirny = 0

        elif direction == "right":
            self.dirnx = 1
            self.dirny = 0

        elif direction == "up":
            self.dirnx = 0
            self.dirny = -1

        elif direction == "down":
            self.dirnx = 0
            self.dirny = 1
    
        if direction != self.lastDirection:
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
            self.lastDirection = direction

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

                
        global list_snack, list_snake, lista_sockets

        for i in range(0, len(list_snack)):
            if list_snack[i].pos[0] == self.head.pos[0] and list_snack[i].pos[1] == self.head.pos[1]:
                self.addCube()
                list_snack.pop(i)

                for k in range (0, len(lista_sockets)):
                    moveMsg = "eat;" + str(list_snake.index(self)) + ";" + str(i) + "\0"
                    lista_sockets[k].sendall(moveMsg.encode())

    def reset(self, pos):
        self.head = Cube(pos)
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
            self.body.append(Cube((tail.pos[0]-1, tail.pos[1]), color=cor))
        elif dx == -1 and dy == 0:
            self.body.append(Cube((tail.pos[0]+1, tail.pos[1]),color=cor))
        elif dx == 0 and dy == 1:
            self.body.append(Cube((tail.pos[0], tail.pos[1]-1),color=cor))
        elif dx == 0 and dy == -1:
            self.body.append(Cube((tail.pos[0], tail.pos[1]+1),color=cor))

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

def randomSnack(rows, items):
    positions = []
    
    for item in items:
        positions.extend(item.body)

    while True:
        x = random.randrange(0, rows)
        y = random.randrange(0, rows)
        if len(list(filter(lambda z: z.pos == (x, y), positions))) > 0:
            continue
        else:
            break

    return (x, y)

def tratarCliente(clientsocket, adress):
    global lista_sockets, list_snake

    while True:
        msg_cliente = clientsocket.recv(1024).decode("utf-8") 
        comandos = msg_cliente.split(';')

        if comandos[0]== "move":
            list_snake[int(comandos[1])].lastDirection = comandos[2]     

        if not msg_cliente: 
            clientsocket.close()  
            
            index = lista_sockets.index(clientsocket)

            lista_sockets.remove(clientsocket)
            list_snake.pop(index)

            if len(list_snake) < 2:
                for snake in list_snake:
                    snake.lastDirection = 'none'

            for i in range(0, len(lista_sockets)):
                disconnectMsg = "disconnect;" + str(index) + "\0"
                lista_sockets[i].sendall(disconnectMsg.encode())

            break

def moverClientes():
    global lista_sockets, list_snake

    while True:
        pygame.time.delay(100)
        
        for i in range(0, len(lista_sockets)):
            for j in range(0, len(list_snake)):
                moveMsg = "move;" + str(j) + ";" + list_snake[j].lastDirection + "\0"
                lista_sockets[i].sendall(moveMsg.encode())

        for j in range(0, len(list_snake)):
            list_snake[j].move(list_snake[j].lastDirection)


def criarSnacks():
    global lista_sockets, list_snack, list_snake

    while True:
        pygame.time.delay(5000)

        if len(list_snake) > 1:
            list_snack.append(Cube(randomSnack(20, list_snake), color=(0, 255, 0)))
            
            for i in range(0, len(lista_sockets)):
                snackMsg = "snack;" + list_snack[len(list_snack) -1].toJSON() + "\0"
                lista_sockets[i].sendall(snackMsg.encode())


def main():
    t = threading.Thread(target=moverClientes)
    t.daemon = True # vai acabar a thread quando fecharmos o programa
    t.start()

    t = threading.Thread(target=criarSnacks)
    t.daemon = True # vai acabar a thread quando fecharmos o programa
    t.start()

    while True:
        clientsocket, adress = s.accept()
        print("Servidor recebeu concexao de {}".format(adress))
        list_snake.append(Snake((random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255)), (10, 11)))

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

        for clientesConectados in lista_sockets:
            novoClienteMsg = "new_client;" + str(len(list_snake) - 1) + ";" + list_snake[len(list_snake) - 1].toJSON() + "\0"
            clientesConectados.sendall(bytes(novoClienteMsg, "utf-8"))
        
        lista_sockets.append(clientsocket)
        lista_adresses.append(adress)

        t = threading.Thread(target=tratarCliente,args=(clientsocket, adress))
        t.daemon = True # vai acabar a thread quando fecharmos o programa
        t.start()

main()