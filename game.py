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
                description="IED detected ahead!",
                safe_choice="Send in Talon robot to investigate",
                risk_choice="Attempt manual approach",
                safe_outcomes={"morale": +10, "battery": -5},
                risk_outcomes={"morale": -20, "battery": -10},
            ),
            # Add more events here if needed
        ]

    def get_random_event(self):
        """Return a random Event object from the list"""
        return random.choice(self.events)

    def handle_choice(self, event, is_safe_choice):
        outcomes = event.safe_outcomes if is_safe_choice else event.risk_outcomes
        return outcomes

class IEDMiniGame:
    def __init__(self, screen_width, screen_height, initial_battery=100, lives=3, operator_mode=False):
        self.width = screen_width
        self.height = screen_height
        self.player_pos = [(screen_width // 2) - 60, (screen_height // 2) - 60]
        self.battery = initial_battery
        self.lives = lives
        self.game_over = False
        self.success = False
        self.operator_mode = operator_mode

        # Define movement speed
        self.MOVE_SPEED = 12  # Adjust this value as needed

        # Define battery drain rate
        self.BATTERY_DRAIN = 0.125  # Adjust this value as needed

        # Initialize IED position
        self.ied_pos = None
        self.place_ied()  # Place the IED on the grid

        # Initialize obstacles list
        self.obstacles = []  # List to store falling obstacles

        # Load fonts
        self.game_over_font = pygame.font.SysFont("consolas", 48)
        self.game_over_small_font = pygame.font.SysFont("consolas", 24)  # Define small font for resource bars

        # Load sprites with 30% scaling
        sprite_path = os.path.join(os.path.dirname(__file__), "assets")
        self.robot_sprite = self.load_sprite(os.path.join(sprite_path, "talon_sprite.png"), (0, 0, 255), (120, 120))
        self.ied_sprite = self.load_sprite(os.path.join(sprite_path, "9v_battery.png"), (255, 0, 0), (40, 40))
        self.tnt_sprite = self.load_sprite(os.path.join(sprite_path, "tnt_boom.png"), (255, 0, 0), (50, 50))
        self.doge_sprite = self.load_sprite(os.path.join(sprite_path, "doge_em.png"), (255, 255, 0), (50, 50))
        self.gameover_image = self.load_sprite(os.path.join(sprite_path, "game_over.png"), (0, 0, 0), (self.width, self.height), scale_factor=1)
        self.life_sprite = self.load_sprite(os.path.join(sprite_path, "hair_gel.png"), (255, 255, 0), (60, 60))
        self.celebration_background = self.load_sprite(os.path.join(sprite_path, "celebration_background.png"), (0, 255, 0), (self.width, self.height))  # Add celebration background
        # Add the new background
        self.minigame_background = self.load_sprite(os.path.join(sprite_path, "IED_mini_background.png"), (30, 30, 60), (self.width, self.height), scale_factor=1)
        print(f"IED Minigame started with {self.lives} lives")

    def load_sprite(self, sprite_path, fallback_color, size, scale_factor=1.3):
        """Load and scale a sprite with a fallback color"""
        try:
            sprite = pygame.image.load(sprite_path).convert_alpha()
            scaled_size = (int(size[0] * scale_factor), int(size[1] * scale_factor))
            return pygame.transform.scale(sprite, scaled_size)
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
        """Draw the current game state"""
        if self.game_over:
            if self.success:
                self.draw_victory_screen(screen)
            else:
                self.draw_game_over_screen(screen)
            return

        # Draw minigame background instead of solid color
        screen.blit(self.minigame_background, (0, 0))

        # Draw falling obstacles
        for obstacle in self.obstacles:
            screen.blit(obstacle['sprite'], obstacle['pos'])

        # Draw IED and player sprite
        screen.blit(self.ied_sprite, self.ied_pos)
        screen.blit(self.robot_sprite, self.player_pos)

        # Draw UI elements
        self.draw_resource_bars(screen)
        self.draw_lives(screen)

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
        # Define smaller collision boxes for more precise detection
        player_rect = pygame.Rect(
            self.player_pos[0] + 30,  # Offset to center of sprite
            self.player_pos[1] + 30,  # Offset to center of sprite
            60,  # Smaller collision box
            60   # Smaller collision box
        )
        
        ied_rect = pygame.Rect(
            self.ied_pos[0],
            self.ied_pos[1],
            40,  # Match IED sprite size
            40   # Match IED sprite size
        )
        
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

        # Check for IED collision first
        if self.check_ied_collision():
            return

        # Update obstacle positions
        for obstacle in self.obstacles[:]:
            obstacle['pos'][1] += 1.58203125  # Falling speed of obstacles
            
            # Remove obstacles that are off screen
            if obstacle['pos'][1] > self.height:
                self.obstacles.remove(obstacle)

        # Spawn new obstacles
        if random.randint(1, 40) == 1:  # Increased range from 1-30 to 1-40 to reduce spawn rate by 25%
            self.spawn_obstacle()

        # Check for collisions
        if self.check_collision_with_obstacles():
            self.lose_life()
            return

        # Update battery drain
        self.battery -= self.BATTERY_DRAIN
        if self.battery <= 0:
            print("Game Over: Battery depleted")
            self.lose_life()

    def lose_life(self):
        """Handle losing a life"""
        self.lives -= 1  # Decrement lives first
        print(f"Life lost in minigame. Lives remaining: {self.lives}")
        self.game_over = True
        self.success = False

    def draw_game_over_screen(self, screen):
        """Draw game over screen with final score"""
        screen.blit(self.gameover_image, (0, 0))
        
        # Draw "Game Over" text
        game_over_text = self.game_over_font.render("Game Over", True, (255, 0, 0))
        screen.blit(game_over_text, 
                   (self.width//2 - game_over_text.get_width()//2, 
                    self.height//2 - 100))
        
        # Draw final points
        points_text = self.game_over_font.render(f"Final Score: {self.points}", True, (255, 255, 0))
        screen.blit(points_text,
                   (self.width//2 - points_text.get_width()//2,
                    self.height//2))

    def reset_game(self):
        """Reset the game state for another attempt"""
        self.battery = 100  # Reset battery to full
        self.player_pos = [(self.width // 2) - 60, (self.height // 2) - 60]  # Reset player position
        self.obstacles = []  # Clear all obstacles
        self.place_ied()  # Place a new IED
        self.game_over = False  # Reset game_over flag
        self.success = False  # Reset success flag

    def draw_transition_page(self, screen):
        """Draw the transition page after losing a life"""
        screen.blit(self.gameover_image, (0, 0))
        
        # Draw "Life Lost" text
        life_lost_text = self.game_over_font.render("Life Lost", True, (255, 0, 0))
        screen.blit(life_lost_text, 
                   (self.width // 2 - life_lost_text.get_width() // 2, 
                    self.height // 2 - 100))
        
        # Draw remaining lives centered - show current lives after loss
        remaining_lives = max(0, self.lives)  # Ensure non-negative
        total_width = remaining_lives * 70  # Width of all life sprites together
        start_x = (self.width - total_width) // 2  # Center point
        
        print(f"Drawing transition page with {remaining_lives} lives remaining")
        
        for i in range(remaining_lives):
            screen.blit(self.life_sprite, 
                       (start_x + (i * 70), 
                        self.height // 2 + 50))

    def draw_resource_bars(self, screen):
        """Draw the battery level on the screen"""
        # Draw battery bar
        pygame.draw.rect(screen, (255, 0, 0), (20, 50, 200, 20))  # Red background for battery bar
        pygame.draw.rect(screen, (0, 255, 0), (20, 50, self.battery * 2, 20))  # Green foreground for battery level

        # Add battery label
        battery_text = self.game_over_small_font.render(f"Battery: {self.battery:.0f}%", True, (255, 255, 255))
        screen.blit(battery_text, (20, 25))

    def draw_proximity_indicator(self, screen):
        distance = ((self.player_pos[0] - self.ied_pos[0])**2 + 
                   (self.player_pos[1] - self.ied_pos[1])**2)**0.5
        max_distance = (self.width**2 + self.height**2)**0.5
        intensity = int(255 * (1 - distance/max_distance))
        pygame.draw.circle(screen, (intensity, 0, 0), (self.width - 30, 30), 15)

    def draw_lives(self, screen):
        """Draw the remaining lives during gameplay"""
        for i in range(max(0, self.lives)):
            screen.blit(self.life_sprite, 
                       (self.width - 80 - (i * 70),  # Spacing between sprites
                        20))  # Distance from top

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
        """Place IED at a random location on the screen with minimum distance from player"""
        min_distance = 200  # Minimum pixel distance between IED and player
        while True:
            x = random.randint(0, self.width - 40)
            y = random.randint(0, self.height - 40)
            
            # Calculate distance between proposed IED position and player
            distance = ((x - self.player_pos[0])**2 + (y - self.player_pos[1])**2)**0.5
            
            # Only place IED if it's far enough from player
            if distance >= min_distance:
                self.ied_pos = [x, y]
                print(f"IED placed at ({x}, {y}), distance from player: {distance:.0f}")
                break

    def spawn_obstacle(self):
        """Spawn new falling obstacle at random x position"""
        x = random.randint(0, self.width - 50)
        
        # Only spawn TNT if not in operator mode, both types if in operator mode
        if self.operator_mode:
            obstacle_type = random.choice(['tnt', 'doge'])
        else:
            obstacle_type = 'tnt'
            
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

    def draw_celebration_screen(self, screen):
        """Draw the celebration screen when the player wins"""
        # Scale the celebration background to 75% of the screen size
        scaled_width = int(self.width * 1.00)
        scaled_height = int(self.height * 1.00)
        scaled_bg = pygame.transform.scale(self.celebration_background, (scaled_width, scaled_height))
        x_offset = (self.width - scaled_width) // 2
        y_offset = (self.height - scaled_height) // 2
        screen.blit(scaled_bg, (x_offset, y_offset))

        # Draw "Mission Success" text
        success_text = self.game_over_font.render("Mission Success!", True, (0, 255, 0))
        screen.blit(success_text, 
                   (self.width // 2 - success_text.get_width() // 2, 
                    self.height // 2 - 50))
        
        # Draw "Returning to Travel" text
        return_text = self.game_over_small_font.render("Returning to Travel...", True, (255, 255, 255))
        screen.blit(return_text, 
                   (self.width // 2 - return_text.get_width() // 2, 
                    self.height // 2 + 50))