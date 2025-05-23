import random
import pygame
import os

class Event:
    def __init__(self, description, safe_choice, risk_choice, safe_outcomes, risk_outcomes):
        self.description = description
        self.safe_choice = safe_choice
        self.risk_choice = risk_choice
        self.safe_outcomes = safe_outcomes
        self.risk_outcomes = risk_outcomes

class GameEvents:
    def __init__(self):
        self.events = [
            Event(
                description="IED detected ahead! How will you respond?",
                safe_choice="Send in Talon robot to investigate",
                risk_choice="Attempt manual approach",
                safe_outcomes={
                    'morale': 5,
                    'fuel': -5,
                    'robot_battery': -15,
                    'message': "Robot successfully cleared the route. Team confidence increased!"
                },
                risk_outcomes={
                    'morale': -20,
                    'fuel': -10,
                    'robot_battery': 0,
                    'message': "Close call! Team morale decreased significantly."
                }
            ),
            Event(
                description="Truck breaks down. What do you do?",
                safe_choice="Wait for maintenance team",
                risk_choice="Attempt field repair",
                safe_outcomes={
                    'morale': -5,
                    'fuel': -10,
                    'robot_battery': 10,
                    'message': "Maintenance fixed the issue but caused delays."
                },
                risk_outcomes={
                    'morale': -10,
                    'fuel': -20,
                    'robot_battery': 0,
                    'message': "Field repair partially successful but stressed the team."
                }
            ),
            Event(
                description="Talon robot battery low. Continue or stop to charge?",
                safe_choice="Stop to charge",
                risk_choice="Continue mission",
                safe_outcomes={
                    'morale': 5,
                    'fuel': -5,
                    'robot_battery': 50,
                    'message': "Robot fully charged. Team is well prepared."
                },
                risk_outcomes={
                    'morale': -15,
                    'fuel': 0,
                    'robot_battery': -25,
                    'message': "Robot died during crucial moment. Team stressed."
                }
            )
        ]
    
    def get_random_event(self):
        return random.choice(self.events)

    def handle_choice(self, event, is_safe_choice):
        outcomes = event.safe_outcomes if is_safe_choice else event.risk_outcomes
        return outcomes

class IEDMiniGame:
    def __init__(self, screen_width, screen_height, initial_morale=100, initial_battery=100, lives=3):
        self.width = screen_width
        self.height = screen_height
        self.morale = initial_morale
        self.battery = initial_battery
        
        # Resource drain rates
        self.MORALE_DRAIN = 0.1  # Reduced from 0.5
        self.BATTERY_DRAIN = 0.15  # Reduced from 0.3
        
        # Add lives system
        self.lives = lives
        try:
            sprite_path = os.path.join(os.path.dirname(__file__), "assets")
            self.robot_sprite = pygame.image.load(os.path.join(sprite_path, "talon_sprite.png")).convert_alpha()
            self.bombsuit_sprite = pygame.image.load(os.path.join(sprite_path, "bombsuite_sprite.png")).convert_alpha()
            self.robot_sprite = pygame.transform.scale(self.robot_sprite, (60, 60))
            self.bombsuit_sprite = pygame.transform.scale(self.bombsuit_sprite, (60, 60))
            self.life_sprite = pygame.image.load(os.path.join(sprite_path, "hair_gel.png")).convert_alpha()
            self.life_sprite = pygame.transform.scale(self.life_sprite, (30, 30))
        except pygame.error as e:
            print(f"Error loading sprites: {e}")
            self.robot_sprite = pygame.Surface((60, 60))
            self.bombsuit_sprite = pygame.Surface((60, 60))
            self.robot_sprite.fill((100, 100, 255))
            self.bombsuit_sprite.fill((255, 100, 100))
            self.life_sprite = pygame.Surface((30, 30))
            self.life_sprite.fill((255, 215, 0))  # Gold color fallback

        # Movement speed
        self.MOVE_SPEED = 5  # Pixels per movement

        # Initialize game state
        self.current_sprite = "robot"
        self.player_pos = [0, screen_height - 60]
        self.game_over = False
        self.success = False
        self.grid_size = 5
        self.cell_width = screen_width // self.grid_size
        self.cell_height = screen_height // self.grid_size
        self.ied_pos = None
        self.place_ied()

    def update(self):
        if self.game_over:
            return

        # Drain resources based on current sprite
        if self.current_sprite == "robot":
            self.battery -= self.BATTERY_DRAIN
            if self.battery <= 0:
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                    self.success = False
                    print("Out of lives!")
                else:
                    self.battery = 100  # Reset battery
                    print(f"Lost a life! {self.lives} remaining")
        else:  # bombsuit
            self.morale -= self.MORALE_DRAIN
            if self.morale <= 0:
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                    self.success = False
                    print("Out of lives!")
                else:
                    self.morale = 100  # Reset morale
                    print(f"Lost a life! {self.lives} remaining")

    def draw(self, screen):
        # Draw game elements
        screen.fill((30, 30, 60))
        
        # Draw resource bars
        self.draw_resource_bars(screen)
        
        # Draw current sprite
        current_sprite = self.robot_sprite if self.current_sprite == "robot" else self.bombsuit_sprite
        screen.blit(current_sprite, self.player_pos)
        
        # Draw IED hint (gets redder as player gets closer)
        self.draw_proximity_indicator(screen)

        # Draw lives in bottom right corner
        self.draw_lives(screen)

    def draw_resource_bars(self, screen):
        # Battery bar (blue)
        pygame.draw.rect(screen, (50, 50, 50), (20, 20, 200, 20))
        pygame.draw.rect(screen, (0, 0, 255), (20, 20, self.battery * 2, 20))
        
        # Morale bar (green)
        pygame.draw.rect(screen, (50, 50, 50), (20, 50, 200, 20))
        pygame.draw.rect(screen, (0, 255, 0), (20, 50, self.morale * 2, 20))

    def draw_proximity_indicator(self, screen):
        distance = ((self.player_pos[0] - self.ied_pos[0])**2 + 
                   (self.player_pos[1] - self.ied_pos[1])**2)**0.5
        max_distance = (self.width**2 + self.height**2)**0.5
        intensity = int(255 * (1 - distance/max_distance))
        pygame.draw.circle(screen, (intensity, 0, 0), (self.width - 30, 30), 15)

    def draw_lives(self, screen):
        for i in range(self.lives):
            screen.blit(self.life_sprite, 
                       (self.width - 40 - (i * 35), 
                        self.height - 40))

    def move_player(self, dx, dy):
        if self.game_over:
            return

        new_x = self.player_pos[0] + dx * self.MOVE_SPEED
        new_y = self.player_pos[1] + dy * self.MOVE_SPEED
        
        # Check boundaries
        if 0 <= new_x < self.width - 60 and 0 <= new_y < self.height - 60:
            self.player_pos = [new_x, new_y]
            
            # Check if found IED
            if abs(self.player_pos[0] - self.ied_pos[0]) < 30 and \
               abs(self.player_pos[1] - self.ied_pos[1]) < 30:
                self.game_over = True
                self.success = True

    def place_ied(self):
        """Place IED at random location on grid"""
        while True:
            x = random.randint(0, self.grid_size - 1) * self.cell_width
            y = random.randint(0, self.grid_size - 1) * self.cell_height
            if [x, y] != self.player_pos:  # Don't place IED on player
                self.ied_pos = [x, y]
                break