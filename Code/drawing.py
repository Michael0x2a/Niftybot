#!/usr/bin/env python

import pygame

class Window(object):
    MOODS = {
        'red': (255, 128, 128),
        'blue': (120, 155, 239),
        'green': (109, 209, 105),
        'purple': (205, 102, 192),
        'aqua': (93, 185, 170),
        'orange': (243, 187, 122)
    }

    def __init__(self, caption="Niftybot"):
        pygame.init()
        self.screen = pygame.display.set_mode(
            [0, 0],
            pygame.FULLSCREEN | pygame.NOFRAME)
        self.width, self.height = self.screen.get_size()

        pygame.display.set_caption("Niftybot")
        self.font = pygame.font.SysFont("arial", 120)

    def draw_mood(self, mood):
        self.screen.fill(Window.MOODS[mood])
        return self
    
    def draw_text(self, text):
        text_surface = self.font.render(text, True, (255, 255, 255))
        
        text_width = text_surface.get_width()
        self.screen.blit(
            text_surface,
            (int(self.width / 2) - int(text_width / 2), int(self.height * 0.25))
        )
        
    def heartbeat(self):
        pygame.display.flip()
