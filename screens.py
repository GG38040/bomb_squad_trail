import pygame
import math  # Add this import
from utils import draw_text
from game import IEDMiniGame  # Add this import at the top

class ScreenBase:
    def __init__(self, width, height, asset_loader, font_manager, music_manager):
        self.width = width
        self.height = height
        self.asset_loader = asset_loader
        self.font_manager = font_manager
        self.music_manager = music_manager

class MenuScreen(ScreenBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background = self.asset_loader.load_image(
            "mission_start_background.png", 
            (self.width, self.height)
        )
        self.code_input = ""
        self.code_font = pygame.font.SysFont("consolas", 24)
        self.input_active = False
        self.input_rect = pygame.Rect(self.width - 150, 20, 130, 32)
        
    def handle_input(self, event):
        """Handle code input"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
            else:
                self.input_active = False
        
        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                self.input_active = False
            elif event.key == pygame.K_BACKSPACE:
                self.code_input = self.code_input[:-1]
            else:
                if len(self.code_input) < 4 and event.unicode.isnumeric():
                    self.code_input += event.unicode
    
    def draw(self, surface, game_data):  # Added game_data parameter
        """Draw the menu screen"""
        if self.background:
            surface.blit(self.background, (0, 0))
            
        # Draw menu options
        text_color = (255, 255, 255)
        menu_items = [
            "1. Start Mission",
            "2. Quit Game",
            "3. TBD",
            "4. TBD",
            "5. TBD"
        ]
        
        for i, text in enumerate(menu_items):
            draw_text(
                surface,
                text,
                self.font_manager.get_font('small'),
                text_color,
                self.width // 2,
                self.height // 2 + (i * 40)
            )
        
        # Draw code input box
        color = (255, 255, 255) if self.input_active else (128, 128, 128)
        pygame.draw.rect(surface, color, self.input_rect, 2)
        
        # Draw masked code input (show asterisks)
        masked_input = "*" * len(self.code_input)
        text_surface = self.code_font.render(masked_input, True, (255, 255, 255))
        surface.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))

class TravelScreen(ScreenBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background = self.asset_loader.load_image(
            "traveling_background.png", 
            (self.width, self.height)
        )
        self.truck = self.asset_loader.load_image(
            "mrap_truck_right_facing.png",
            (240, 160)  # Reduced size for better visibility
        )
        self.truck_x = -240  # Match new truck width
        self.truck_y = self.height // 2 - 80  # Adjusted for better vertical position
        self.bounce_offset = 0
        self.bounce_speed = 0.005  # Reduced for smoother animation
        
    def update(self):
        """Update truck position and animation"""
        self.truck_x += 3  # Slightly increased speed
        if self.truck_x > self.width:
            self.truck_x = -240
            
        self.bounce_offset = math.sin(pygame.time.get_ticks() * self.bounce_speed) * 5
        
    def draw(self, surface, game_data):
        """Draw the travel screen"""
        # Draw background
        if self.background:
            surface.blit(self.background, (0, 0))
        
        # Draw truck with bounce effect
        if self.truck:
            surface.blit(
                self.truck, 
                (self.truck_x, self.truck_y + self.bounce_offset)
            )
        
        # Draw status text
        status_text = (f"Fuel: {game_data['fuel']} | "
                      f"Battery: {game_data['battery']} | "
                      f"Morale: {game_data['morale']}")
        
        draw_text(
            surface,
            "Traveling to next mission site...",
            self.font_manager.get_font('regular'),
            (255, 255, 255),
            self.width // 2,
            120
        )
        
        draw_text(
            surface,
            status_text,
            self.font_manager.get_font('small'),
            (255, 255, 255),
            self.width // 2,
            200
        )
        
        # Draw points only in bottom right corner
        points_text = f"Points: {game_data['points']}"
        draw_text(
            surface,
            points_text,
            self.font_manager.get_font('large'),
            (255, 255, 0),  # Yellow color
            self.width - 100,
            self.height - 50
        )

class MinigameScreen(ScreenBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ied_game = None
        
    def init_game(self, battery, lives, operator_mode=False):
        """Initialize the IED minigame with current lives count and operator mode"""
        self.ied_game = IEDMiniGame(
            self.width, 
            self.height, 
            battery, 
            lives,
            operator_mode
        )
        print(f"Minigame initialized with battery: {battery}, lives: {lives}, operator mode: {operator_mode}")
        
    def update(self):
        """Update minigame state"""
        if self.ied_game:
            self.ied_game.update()
            
    def draw(self, surface, game_data):
        """Draw minigame state"""
        if self.ied_game:
            self.ied_game.draw(surface)
            # Points should not be displayed in minigame
            
    def handle_input(self, events):
        """Handle minigame input"""
        if not self.ied_game:
            return
            
        keys = pygame.key.get_pressed()
        # Support both WASD and arrow keys
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        
        if dx != 0 or dy != 0:
            self.ied_game.move_player(dx, dy)

class OutcomeScreen(ScreenBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background = self.asset_loader.load_image(
            "game_over.png", 
            (self.width, self.height)
        )
    
    def draw(self, surface, game_data):
        """Draw the game over screen with styled text"""
        if self.background:
            surface.blit(self.background, (0, 0))
        
        # Draw "GAME OVER" in large red letters
        game_over_text = "GAME OVER"
        draw_text(
            surface,
            game_over_text,
            self.font_manager.get_font('title'),  # Using largest font
            (255, 0, 0),  # Red color
            self.width // 2,
            self.height // 3
        )
        
        # Draw points in yellow between texts
        points_text = f"Final Score: {game_data['points']}"
        draw_text(
            surface,
            points_text,
            self.font_manager.get_font('large'),
            (255, 255, 0),  # Yellow color
            self.width // 2,
            self.height // 2
        )
        
        # Draw "Initial Success or Total Failure" below
        motto_text = "Initial Success or Total Failure"
        draw_text(
            surface,
            motto_text,
            self.font_manager.get_font('regular'),
            (255, 255, 255),  # White color
            self.width // 2,
            (self.height // 3) * 2
        )