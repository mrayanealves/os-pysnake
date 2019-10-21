import math
import random
import pygame
import tkinter as tk
from tkinter import messagebox
import socket
import threading
import queue
import json

receber_direcoes = ""
own_snake_id = ""
list_snake = []
list_snack = []


class Cube(object):
    rows = 20
    w = 500

    def __init__(self, pos, dirnx=1, dirny=0, color=(255, 255, 255)):
        self.pos = pos
        self.dirnx = 1
        self.dirny = 0
        self.color = color

    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)

    def draw(self, surface, eyes=False):
        dis = self.w // self.rows
        i = int(self.pos[0])
        j = int(self.pos[1])

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

    def __init__(self, color, head, body, dirnx, dirny):
        # print(color, head, body, dirnx, dirny)
        self.color = color
        self.head = Cube(**json.loads(json.dumps(head)))
        self.body =[]
        self.body.append(self.head)
        self.dirnx = dirnx
        self.dirny = dirny

    def move(self, direction):
        # for event in pygame.event.get():
        #     if event.type == pygame.QUIT:
        #         pygame.quit()

        #     keys = pygame.key.get_pressed()

        if direction == "left":
            self.dirnx = -1
            self.dirny = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        elif direction == "right":
            self.dirnx = 1
            self.dirny = 0
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        elif direction == "up":
            self.dirnx = 0
            self.dirny = -1
            self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        elif direction == "down":
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
            self.body.append(Cube((tail.pos[0]+1, tail.pos[1]), color=cor))
        elif dx == 0 and dy == 1:
            self.body.append(Cube((tail.pos[0], tail.pos[1]-1), color=cor))
        elif dx == 0 and dy == -1:
            self.body.append(Cube((tail.pos[0], tail.pos[1]+1), color=cor))

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

def redrawWindow(surface):
    global rows, width, list_snake, list_snack
    surface.fill((0, 0, 0))
    for snack in list_snack:
        snack.draw(surface)
    for snake in list_snake:
        snake.draw(surface)
    #drawGrid(width, rows, surface)
    pygame.display.update()


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


def message_box(subject, content):
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    messagebox.showinfo(subject, content)
    try:
        root.destroy()
    except:
        pass


def recvMsg(socket1, surface):
    while True:
        msg = socket1.recv(1024)

        # print(msg.decode("utf-8"))
        mensagem = msg.decode("utf-8")
        comandos = mensagem.split(';')
        if (comandos[0]== "move"):
            list_snake[comandos[1]].move(comandos[2])
        elif (comandos[0]== "eat"):
            list_snake[comandos[1]].addCube()
        if not msg:
            break

        redrawWindow(surface)

def main():
    global width, rows
    global receber_direcoes , list_snake, list_snack, own_snake_id

    width = 500
    rows = 20

    socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket1.connect(("localhost", 5551))

    msg = socket1.recv(1024).decode("utf-8")
    list_msg = msg.split(';')

    if list_msg[0] == "start" and list_msg[1] == "snakes":
        for snake in list_msg[2:]:
            # print(**json.loads(snake))
            list_snake.append(Snake(**json.loads(snake)))
    socket1.sendall(b"ok")
    msg1 = socket1.recv(1024).decode("utf-8")
    list_msg = msg1.split(';')

    if list_msg[0] == "start" and list_msg[1] == "snacks":
        for snack in list_msg[2:]:
            list_snack.append(Cube((10,10)))
    socket1.sendall(b"ok")
    msg = socket1.recv(1024).decode("utf-8")
    list_msg = msg.split(';')

    if list_msg[0] == "start" and list_msg[1] == "id":
        own_snake_id = list_msg[2]

    surface = pygame.display.set_mode((width, width))
    # s = snake((255, 0, 250), (10, 10))
    # s2 = snake2((0, 255, 0), (10, 11))
    # snack = cube(randomSnack(rows, s), color=(0, 255, 0))
    flag = True

    clock = pygame.time.Clock()

    t = threading.Thread(target=recvMsg, args=(socket1,surface))
    t.daemon = True  
    print("thread criada")
    t.start()
   
    while flag:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            keys = pygame.key.get_pressed()

            for key in keys:
                if keys[pygame.K_LEFT]:

                elif keys[pygame.K_RIGHT]:

                elif keys[pygame.K_UP]:

                elif keys[pygame.K_DOWN]:
    pass



main()
