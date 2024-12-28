import pygame
from constants import *

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {
            'move': pygame.mixer.Sound(MOVE_SOUND),
            'capture': pygame.mixer.Sound(CAPTURE_SOUND),
            'castle': pygame.mixer.Sound(CASTLE_SOUND),
            'checkmate': pygame.mixer.Sound(CHECKMATE_SOUND),
            'draw': pygame.mixer.Sound(DRAW_SOUND)
        }
        
    def play_move(self, is_capture=False, is_castle=False):
        if is_castle:
            self.sounds['castle'].play()
        elif is_capture:
            self.sounds['capture'].play()
        else:
            self.sounds['move'].play()
            
    def play_game_end(self, is_checkmate=False):
        if is_checkmate:
            self.sounds['checkmate'].play()
        else:
            self.sounds['draw'].play()