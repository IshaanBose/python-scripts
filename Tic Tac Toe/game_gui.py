import pygame
from pygame.locals import *
import os
from tkinter import Tk

COLOURS = {'black' : (0, 0, 0), 'white' : (255, 255, 255), 'green':(0, 255, 0), 'mustard yellow':(255, 208, 0), 
            'light pink': (255, 122, 251), 'red': (255, 0, 0), 'dark blue': (2, 68, 173)}
DWIDTH, DHEIGHT = 500, 500
root = Tk()
X = int(root.winfo_screenwidth() * 0.2)
Y = int(root.winfo_screenheight() * 0.2)
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (X, Y) # to place window at (x, y) position
DISPLAY = pygame.display.set_mode((DWIDTH, DHEIGHT), HWSURFACE | DOUBLEBUF)
pygame.display.set_caption('Tic Tac Toe')
pygame.init()

class StartMenu():
    def __init__(self):
        self._running = False
        self._display = None
    
    def on_init(self):
        self._display = pygame.Surface((DWIDTH, DHEIGHT))
        
        self._running = True
        
        self.draw_menu()
        DISPLAY.blit(self._display, (0, 0))
    
    def draw_menu(self):
        self._display.fill(COLOURS['white'])
        
        title_font = pygame.font.SysFont('sourcesansprosemibold', 70) # for title
        title = title_font.render('Tic Tac Toe', True, COLOURS['black'])
        title_rect = title.get_rect()
        title_rect.center = (DWIDTH // 2, DHEIGHT // 6)
        
        label_font = pygame.font.SysFont('sourcesanspro', 25)
        difficulty = label_font.render('Difficulty:', True, COLOURS['black'])
        mode = label_font.render('Mode:', True, COLOURS['black'])
        
        self._display.blit(title, title_rect)
        self._display.blit(difficulty, (20, (DHEIGHT // 6) + 110))
        self._display.blit(mode, (20, (DHEIGHT // 6) + 200))
    
    def on_event(self, event):
        if event.type == QUIT:
            self._running = False
    
    def on_cleanup(self):
        pygame.quit()
    
    def on_execute(self):
        self.on_init()
        
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            pygame.display.update()
        self.on_cleanup()