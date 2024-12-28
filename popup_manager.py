import pygame
from constants import *

class PopupManager:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.small_font = pygame.font.Font(None, SMALL_FONT_SIZE)
        
    def show_popup(self, message, sub_message="Press any key to continue"):
        # Create semi-transparent overlay
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Create popup rectangle
        popup_width = 300
        popup_height = 150
        popup_x = (self.screen.get_width() - popup_width) // 2
        popup_y = (self.screen.get_height() - popup_height) // 2
        
        pygame.draw.rect(self.screen, WHITE, 
                        (popup_x, popup_y, popup_width, popup_height))
        pygame.draw.rect(self.screen, BLACK, 
                        (popup_x, popup_y, popup_width, popup_height), 2)
        
        # Render message
        text = self.font.render(message, True, BLACK)
        text_rect = text.get_rect(center=(self.screen.get_width()//2, 
                                        self.screen.get_height()//2))
        self.screen.blit(text, text_rect)
        
        # Render sub-message
        if sub_message:
            sub_text = self.small_font.render(sub_message, True, BLACK)
            sub_text_rect = sub_text.get_rect(center=(self.screen.get_width()//2, 
                                            self.screen.get_height()//2 + 40))
            self.screen.blit(sub_text, sub_text_rect)
        
        pygame.display.flip()
        
        # Wait for key press
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    waiting = False
                    
        return True