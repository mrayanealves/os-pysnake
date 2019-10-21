from typing import List

import pygame
import socket
import pickle


class cube(object):
    rows = 20
    w = 500

    def __init__(self, start, dirnx=1, dirny=0, color=(255, 0, 0)):
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

        pygame.draw.rect(surface, self.color, (i * dis + 1, j * dis + 1, dis - 2, dis - 2))
        if eyes:
            centre = dis // 2
            radius = 3
            circleMiddle = (i * dis + centre - radius, j * dis + 8)
            circleMiddle2 = (i * dis + dis - radius * 2, j * dis + 8)
            pygame.draw.circle(surface, (0, 0, 0), circleMiddle, radius)
            pygame.draw.circle(surface, (0, 0, 0), circleMiddle2, radius)


class snake(object):
    # def __init__(self, body):
    #     self.body = []
    #
    #     for piece in body:
    #         self.body.append(cube(piece.position, color = piece.color))

    def draw(self, surface):
        for i, c in enumerate(self.body):
            if i == 0:
                c.draw(surface, True)
            else:
                c.draw(surface)


def drawGrid(w, rows, surface):
    sizeBtwn = w // rows

    x = 0
    y = 0
    for l in range(rows):
        x = x + sizeBtwn
        y = y + sizeBtwn

        pygame.draw.line(surface, (0, 0, 0), (x, 0), (x, w))
        pygame.draw.line(surface, (0, 0, 0), (0, y), (w, y))


def redrawWindow(surface):
    global rows, width, snakes, snacks
    surface.fill((0, 0, 0))

    for s in snakes:
        s.draw(surface)

    for s in snacks:
        s.draw(surface)

    drawGrid(width, rows, surface)
    pygame.display.update()


if __name__ == '__main__':
    global width, rows, snakes, snacks

    width = 500
    rows = 20

    HOST = 'localhost'
    PORT = 5001

    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket.connect((HOST, PORT))
    socket.send("Hello".encode("utf-8"))

    win = pygame.display.set_mode((width, width))

    data = socket.recv(1024)

    res = pickle.loads(data)

    snacks = []
    snakes = []

    for snack in res[1]:
        snacks.append(cube(snack.pos, color=snack.color))

    for snake in res[0]:
        snakes.append(snake)

    redrawWindow(win)

    while True:
        redrawWindow(win)