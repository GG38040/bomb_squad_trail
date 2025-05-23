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
        self.player_pos = [(screen_width // 2) - 60, (screen_height // 2) - 60]
        self.current_sprite = "robot"  # Default to Talon robot
        self.morale = initial_morale
        self.battery = initial_battery
        self.lives = lives
        self.game_over = False  # Initialize game_over to False
        self.success = False  # Initialize success to False

        # Define movement speed
        self.MOVE_SPEED = 6  # Increased by 20% (originally 5)

        # Define resource drain rates
        self.BATTERY_DRAIN = 1  # Battery drain per update cycle when using the robot
        self.MORALE_DRAIN = 1   # Morale drain per update cycle when using the bomb suit

        # Initialize IED position
        self.ied_pos = None
        self.place_ied()  # Place the IED on the grid

        # Initialize obstacles list
        self.obstacles = []  # List to store falling obstacles

        # Fonts for game over and victory screens
        self.game_over_font = pygame.font.SysFont("consolas", 48)
        self.game_over_small_font = pygame.font.SysFont("consolas", 24)

        # Load sprites
        sprite_path = os.path.join(os.path.dirname(__file__), "assets")
        self.robot_sprite = self.load_sprite(os.path.join(sprite_path, "talon_sprite.png"), (0, 0, 255), (120, 120))
        self.bombsuit_sprite = self.load_sprite(os.path.join(sprite_path, "bombsuite_sprite.png"), (0, 255, 0), (120, 120))
        self.ied_sprite = self.load_sprite(os.path.join(sprite_path, "9v_battery.png"), (255, 0, 0), (40, 40))
        self.life_sprite = self.load_sprite(os.path.join(sprite_path, "hair_gel.png"), (255, 255, 0), (30, 30))
        self.tnt_sprite = self.load_sprite(os.path.join(sprite_path, "tnt_boom.png"), (255, 0, 0), (50, 50))
        self.doge_sprite = self.load_sprite(os.path.join(sprite_path, "doge_em.png"), (255, 255, 0), (50, 50))
        self.gameover_image = self.load_sprite(os.path.join(sprite_path, "game_over.png"), (0, 0, 0), (self.width, self.height))

    def load_sprite(self, sprite_path, fallback_color, size):
        try:
            sprite = pygame.image.load(sprite_path).convert_alpha()
            return pygame.transform.scale(sprite, size)
        except FileNotFoundError:
            print(f"Warning: Missing sprite file at {sprite_path}")
            sprite = pygame.Surface(size)
            sprite.fill(fallback_color)
            return sprite

    def switch_sprite(self):
        """Switch between robot and bomb suit sprites"""
        if self.current_sprite == "robot":
            self.current_sprite = "bombsuit"
            print("Switched to Bomb Suit - Watch your morale!")
        else:
            self.current_sprite = "robot"
            print("Switched to Talon Robot - Watch your battery!")

    def draw(self, screen):
        """Draw the current sprite at the player's position"""
        if self.current_sprite == "robot":
            screen.blit(self.robot_sprite, self.player_pos)
        else:
            screen.blit(self.bombsuit_sprite, self.player_pos)

    def check_collision_with_obstacles(self):
        """Check if player has collided with any falling obstacles"""
        player_rect = pygame.Rect(self.player_pos[0], self.player_pos[1], 120, 120)
        
        for obstacle in self.obstacles:
            obstacle_rect = pygame.Rect(obstacle['pos'][0], obstacle['pos'][1], 50, 50)
            if player_rect.colliderect(obstacle_rect):
                print(f"Collision detected with obstacle at {obstacle['pos']}")
                self.game_over = True
                self.success = False
                return True
        return False

    def check_ied_collision(self):
        """Check if player has found the IED"""
        player_rect = pygame.Rect(self.player_pos[0], self.player_pos[1], 120, 120)
        ied_rect = pygame.Rect(self.ied_pos[0], self.ied_pos[1], 40, 40)
        
        if player_rect.colliderect(ied_rect):
            print(f"IED found at {self.ied_pos}")
            self.game_over = True
            self.success = True
            return True
        return False

    def update(self):
        """Update the game state"""
        if self.game_over:
            return

        # Example logic for game over condition
        if self.morale <= 0 or self.battery <= 0:
            print("Game Over: Resource depletion")
            self.game_over = True
            self.success = False

        # Check for IED collision first
        if self.check_ied_collision():
            return

        # Update obstacle positions
        for obstacle in self.obstacles[:]:
            obstacle['pos'][1] += 1.58203125  # Falling speed of obstacles
            
            # Remove obstacles that are off screen
            if obstacle['pos'][1] > self.height:
                print(f"Obstacle removed: {obstacle}")
                self.obstacles.remove(obstacle)

        # Spawn new obstacles
        if random.randint(1, 40) == 1:  # Increased range from 1-30 to 1-40 to reduce spawn rate by 25%
            self.spawn_obstacle()

        # Check for collisions
        if self.check_collision_with_obstacles():
            return

        # Update resource drain
        if self.current_sprite == "robot":
            self.battery -= self.BATTERY_DRAIN * 0.125  # Reduce drain rate by 50%
            if self.battery <= 0:
                print("Game Over: Battery depleted")
                self.game_over = True
                self.success = False
        else:
            self.morale -= self.MORALE_DRAIN * 0.25  # Keep morale drain rate as is
            if self.morale <= 0:
                print("Game Over: Morale depleted")
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
        """Move the player and check for collisions"""
        if self.game_over:
            return

        new_x = self.player_pos[0] + dx * self.MOVE_SPEED
        new_y = self.player_pos[1] + dy * self.MOVE_SPEED
        
        # Check boundaries
        if 0 <= new_x < self.width - 120 and 0 <= new_y < self.height - 120:
            self.player_pos = [new_x, new_y]
            print(f"Player moved to {self.player_pos}")
            
            # Check IED collision immediately after movement
            if self.check_ied_collision():
                return
            
            # Check for obstacle collisions
            if self.check_collision_with_obstacles():
                return

    def place_ied(self):
        """Place IED at a random location on the screen"""
        while True:
            x = random.randint(0, self.width - 40)
            y = random.randint(0, self.height - 40)
            if [x, y] != self.player_pos:  # Ensure IED is not placed on the player
                self.ied_pos = [x, y]
                break

    def spawn_obstacle(self):
        """Spawn new falling obstacle at random x position"""
        x = random.randint(0, self.width - 50)
        obstacle_type = random.choice(['tnt', 'doge'])
        sprite = self.tnt_sprite if obstacle_type == 'tnt' else self.doge_sprite
        self.obstacles.append({
            'type': obstacle_type,
            'pos': [x, -50],
            'sprite': sprite
        })
        print(f"Spawned obstacle: {obstacle_type} at x={x}")

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