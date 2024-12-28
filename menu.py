import pygame
from constants import *

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.Font(None, FONT_SIZE)
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.running = True
        self.font = pygame.font.Font(None, FONT_SIZE)
        
        # Calculate button positions
        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2
        
        self.ai_button = Button(
            center_x - BUTTON_WIDTH // 2,
            center_y - BUTTON_HEIGHT,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Play vs AI",
            WHITE,
            (200, 200, 200)
        )
        
        self.friend_button = Button(
            center_x - BUTTON_WIDTH // 2,
            center_y + BUTTON_HEIGHT,
            BUTTON_WIDTH,
            BUTTON_HEIGHT,
            "Play vs Friend",
            WHITE,
            (200, 200, 200)
        )
        
    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                    
                if self.ai_button.handle_event(event):
                    return "AI"
                if self.friend_button.handle_event(event):
                    return "FRIEND"
            
            self.screen.fill(LIGHT_SQUARE)
            
            # Draw title
            title = self.font.render("Chess Game", True, BLACK)
            title_rect = title.get_rect(center=(self.screen.get_width()//2, 100))
            self.screen.blit(title, title_rect)
            
            # Draw buttons
            self.ai_button.draw(self.screen)
            self.friend_button.draw(self.screen)
            
            pygame.display.flip()