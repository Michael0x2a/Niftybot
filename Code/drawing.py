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
        self.font = pygame.font.SysFont("arial", 90, False, False)

    def draw_mood(self, mood):
        self.screen.fill(Window.MOODS[mood])
        return self
    
    def draw_text(self, *texts):
        start_height = int(self.height * 0.25)
        for index, text in enumerate(texts):
            text_surface = self.font.render(text, True, (255, 255, 255))
            text_width = text_surface.get_width()
            self.screen.blit(
                text_surface,
                (int(self.width / 2) - int(text_width / 2), index * 100 + start_height))

    def draw_button(self, button):
        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            button.rect,
            5)
        self.screen.blit(
            button.text_surface,
            button.text_rect)

    def draw_filled_button(self, button):
        pygame.draw.rect(
            self.screen,
            (255, 255, 255),
            button.rect)
        
    def heartbeat(self):
        pygame.display.flip()

class Button(object):
    def __init__(self, text, position, font_size=80):
        self.text = text
        self.font_size = font_size
        self.font = pygame.font.SysFont("arial", font_size)
        self.text_surface = self.font.render(self.text, True, (255, 255, 255))
        self.width, self.height = self.text_surface.get_size()
        x, y = position

        self.text_rect = pygame.Rect((x - self.width/2, y), (self.width, self.height))

        self.width = max(300, self.width)
        box_x = x - self.width / 2
        self.rect = pygame.Rect((box_x, y), (self.width, self.height))

    def is_pressed(self, pos):
        return self.rect.collidepoint(pos)

def make_buttons(window, *text):
    num = len(text)
    fontsize = 40
    delta = window.width / float(num + 1)
    button_offset = int(window.height * 0.6)
    x_coords = [int(delta * (i + 1)) for i in range(num)]
    buttons = [Button(t, (xpos, button_offset)) for (t, xpos) in zip(text, x_coords)]
    return buttons

