import pygame
from game import Game

pygame.init()


LARGURA = 900
ALTURA = 650
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption('TURBOX  Racing 🏎️')


jogo = Game(tela, LARGURA, ALTURA)
jogo.rodar()


pygame.quit()



