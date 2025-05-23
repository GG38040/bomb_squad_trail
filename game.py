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
            # Double the sprite size
            self.robot_sprite = pygame.transform.scale(self.robot_sprite, (120, 120))  # Changed from 60 to 120
            self.bombsuit_sprite = pygame.transform.scale(self.bombsuit_sprite, (120, 120))  # Changed from 60 to 120
            self.life_sprite = pygame.image.load(os.path.join(sprite_path, "hair_gel.png")).convert_alpha()
            self.life_sprite = pygame.transform.scale(self.life_sprite, (30, 30))
        except pygame.error as e:
            print(f"Error loading sprites: {e}")
            self.robot_sprite = pygame.Surface((120, 120))  # Changed size here too
            self.bombsuit_sprite = pygame.Surface((120, 120))
            self.robot_sprite.fill((100, 100, 255))
            self.bombsuit_sprite.fill((255, 100, 100))
            self.life_sprite = pygame.Surface((30, 30))
            self.life_sprite.fill((255, 215, 0))  # Gold color fallback

        # Load additional sprites
        try:
            self.ied_sprite = pygame.image.load(os.path.join(sprite_path, "9v_battery.png")).convert_alpha()
            self.ied_sprite = pygame.transform.scale(self.ied_sprite, (40, 40))
            
            self.tnt_sprite = pygame.image.load(os.path.join(sprite_path, "tnt_boom.png")).convert_alpha()
            self.tnt_sprite = pygame.transform.scale(self.tnt_sprite, (50, 50))
            
            self.doge_sprite = pygame.image.load(os.path.join(sprite_path, "doge_em.png")).convert_alpha()
            self.doge_sprite = pygame.transform.scale(self.doge_sprite, (50, 50))
            
            self.gameover_image = pygame.image.load(os.path.join(sprite_path, "game_over.png")).convert_alpha()
            self.gameover_image = pygame.transform.scale(self.gameover_image, (self.width, self.height))
            # Add game over font
            self.game_over_font = pygame.font.SysFont("consolas", 48)
            self.game_over_small_font = pygame.font.SysFont("consolas", 36)
        except pygame.error as e:
            print(f"Error loading additional sprites: {e}")

        # Increase movement speed for better control
        self.MOVE_SPEED = 10  # Increased from 5 to 10

        # Initialize game state
        self.current_sprite = "robot"  # Initial sprite
        self.player_pos = [0, screen_height - 60]
        self.game_over = False
        self.success = False
        self.grid_size = 5
        self.cell_width = screen_width // self.grid_size
        self.cell_height = screen_height // self.grid_size
        self.ied_pos = None
        self.place_ied()

        # Falling obstacles setup
        self.obstacles = []
        self.obstacle_speed = 5
        self.spawn_timer = 0
        self.spawn_delay = 60  # Frames between obstacle spawns

    def switch_sprite(self):
        """Switch between robot and bombsuit sprites"""
        if self.current_sprite == "robot":
            self.current_sprite = "bombsuit"
            print("Switched to bombsuit")
        else:
            self.current_sprite = "robot"
            print("Switched to robot")
        
        # Reset position when switching to prevent getting stuck
        self.player_pos = [self.player_pos[0], self.player_pos[1]]

    def check_collision_with_obstacles(self):
        """Check if player has collided with any falling obstacles"""
        player_rect = pygame.Rect(self.player_pos[0], self.player_pos[1], 120, 120)
        
        for obstacle in self.obstacles:
            obstacle_rect = pygame.Rect(obstacle['pos'][0], obstacle['pos'][1], 50, 50)
            if player_rect.colliderect(obstacle_rect):
                self.game_over = True
                self.success = False
                return True
        return False

    def update(self):
        if self.game_over:
            return

        # Update obstacle positions
        for obstacle in self.obstacles[:]:
            obstacle['pos'][1] += 5  # Speed of falling obstacles
            
            # Remove obstacles that are off screen
            if obstacle['pos'][1] > self.height:
                self.obstacles.remove(obstacle)

        # Spawn new obstacles
        if random.randint(1, 60) == 1:  # Adjust frequency of obstacles
            obstacle_type = random.choice(['tnt', 'doge'])
            sprite = self.tnt_sprite if obstacle_type == 'tnt' else self.doge_sprite
            self.obstacles.append({
                'type': obstacle_type,
                'pos': [random.randint(0, self.width - 50), -50],
                'sprite': sprite
            })

        # Check for collisions
        if self.check_collision_with_obstacles():
            return

        # Update resource drain
        if self.current_sprite == "robot":
            self.battery -= self.BATTERY_DRAIN
            if self.battery <= 0:
                self.game_over = True
                self.success = False
        else:
            self.morale -= self.MORALE_DRAIN
            if self.morale <= 0:
                self.game_over = True
                self.success = False

    def draw(self, screen):
        if self.game_over:
            if self.success:
                # Victory screen - only show when IED is found
                self.draw_victory_screen(screen)
            else:
                # Game over screen - show when collision with obstacles or resources depleted
                self.draw_game_over_screen(screen)
            return
            
        # Draw normal game screen
        screen.fill((30, 30, 60))
        
        # Draw IED target
        screen.blit(self.ied_sprite, self.ied_pos)
        
        # Draw falling obstacles
        for obstacle in self.obstacles:
            screen.blit(obstacle['sprite'], obstacle['pos'])
        
        # Draw player sprite
        current_sprite = self.robot_sprite if self.current_sprite == "robot" else self.bombsuit_sprite
        screen.blit(current_sprite, self.player_pos)
        
        # Draw UI elements
        self.draw_resource_bars(screen)
        self.draw_lives(screen)

    def draw_game_over_screen(self, screen):
        """Draw game over screen with text"""
        # Draw the game over background image
        screen.blit(self.gameover_image, (0, 0))
        
        # Draw "Game Over" text
        game_over_text = self.game_over_font.render("Game Over", True, (255, 0, 0))
        screen.blit(game_over_text, 
                   (self.width//2 - game_over_text.get_width()//2, 
                    self.height//2 - game_over_text.get_height()))
        
        # Draw motto text
        motto_text = self.game_over_small_font.render("Initial Success or Total Failure", True, (255, 255, 255))
        screen.blit(motto_text, 
                   (self.width//2 - motto_text.get_width()//2, 
                    self.height//2 + motto_text.get_height()))

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

    def spawn_obstacle(self):
        """Spawn new falling obstacle at random x position"""
        x = random.randint(0, self.width - 50)
        obstacle_type = random.choice(['tnt', 'doge'])
        self.obstacles.append({
            'type': obstacle_type,
            'pos': [x, -50],
            'sprite': self.tnt_sprite if obstacle_type == 'tnt' else self.doge_sprite
        })

    def draw_victory_screen(self, screen):
        """Draw victory message"""
        font = pygame.font.SysFont("consolas", 48)
        text1 = font.render("HOYAHHH NAVY EOD!!!", True, (255, 255, 0))
        text2 = font.render("LLTB", True, (255, 255, 0))
        
        screen.blit(text1, (self.width//2 - text1.get_width()//2, self.height//2 - 50))
        screen.blit(text2, (self.width//2 - text2.get_width()//2, self.height//2 + 50))

    def check_collision(self, pos1, pos2):
        """Check if two positions are close enough to collide"""
        return (abs(pos1[0] - pos2[0]) < 40 and 
                abs(pos1[1] - pos2[1]) < 40)