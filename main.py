import pygame
import sys
import random
import math
import os
from game import GameEvents, IEDMiniGame

# Initialize Pygame
pygame.init()
game_events = GameEvents()

# Add these near the top of the file after pygame.init()
pygame.mixer.init()

# Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Window settings
WIDTH, HEIGHT = 1024, 768
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bomb Squad Trail")

# Load background sprite
try:
    menu_background_path = os.path.join(current_dir, "assets", "mission_start_background.png")
    print(f"Attempting to load menu background from: {menu_background_path}")
    menu_background = pygame.image.load(menu_background_path).convert()
    menu_background = pygame.transform.scale(menu_background, (WIDTH, HEIGHT))
    print(f"Menu background loaded successfully: {menu_background.get_size()}")
except pygame.error as e:
    print(f"ERROR loading menu background: {e}")
    print(f"Attempted path: {menu_background_path}")
    menu_background = pygame.Surface((WIDTH, HEIGHT))
    menu_background.fill(NAVY)

try:
    background_path = os.path.join(current_dir, "assets", "traveling_background.png")
    background = pygame.image.load(background_path).convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    print(f"Background loaded: {background.get_size()}")
except pygame.error as e:
    print(f"Couldn't load background: {e}")
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(BLACK)

# Truck settings
TRUCK_WIDTH = 480
TRUCK_HEIGHT = 320
truck_x = -TRUCK_WIDTH
truck_y = HEIGHT // 2
TRUCK_SPEED = 2
bounce_offset = 0
bounce_speed = 0.01

# Load truck sprite
try:
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    truck_path = os.path.join(current_dir, "assets", "mrap_truck_right_facing.png")
    truck_sprite = pygame.image.load(truck_path).convert_alpha()
    truck_sprite = pygame.transform.scale(truck_sprite, (TRUCK_WIDTH, TRUCK_HEIGHT))
    print(f"Truck sprite loaded: {truck_sprite.get_size()}")  # Add here
except pygame.error as e:
    print(f"Couldn't load truck sprite from {truck_path}: {e}")
    truck_sprite = pygame.Surface((TRUCK_WIDTH, TRUCK_HEIGHT))
    truck_sprite.fill((100, 100, 100))

# Replace the existing truck surface creation with:
truck = truck_sprite

def update_truck():
    global truck_x, truck_y, bounce_offset
    # Move truck right
    truck_x += TRUCK_SPEED
    
    # Bounce effect
    bounce_offset = math.sin(pygame.time.get_ticks() * bounce_speed) * 10
    
    # Reset truck position when it goes off screen
    if truck_x > WIDTH:
        truck_x = -TRUCK_WIDTH

def draw_truck(surface):
    # Draw truck at current position with bounce offset
    surface.blit(truck, (truck_x, truck_y + bounce_offset))

# Modify your travel_screen function
def travel_screen():
    global points
    
    # Ensure traveling music is playing and other music is stopped
    if MUSIC_LOADED:
        if state == TRAVEL:  # Only play music if we're actually in travel state
            current_track = pygame.mixer.music.get_pos()
            if current_track == -1:  # No music playing
                change_music('travel')
    
    # Draw background
    SCREEN.blit(background, (0, 0))
    
    # Update and draw truck
    update_truck()
    draw_truck(SCREEN)
    
    # Draw text on top
    draw_text("Traveling to next mission site...", FONT, WHITE, SCREEN, 150, 120)
    draw_text(f"Fuel: {fuel} | Robot Battery: {robot_battery} | Morale: {morale}", 
              SMALL_FONT, WHITE, SCREEN, 180, 200)
    # draw_text("Press SPACE to continue", SMALL_FONT, WHITE, SCREEN, 250, 400)
    
    # --- Real-time points update ---
    if game_start_ticks is not None:
        elapsed_ms = pygame.time.get_ticks() - game_start_ticks
        points = elapsed_ms // 1000  # 1 point per second

    # Display points in the middle, large and yellow
    points_text = f"Points: {points}"
    rendered = POINTS_FONT.render(points_text, True, POINTS_COLOR)
    SCREEN.blit(rendered, (WIDTH // 2 - rendered.get_width() // 2, HEIGHT - 100))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NAVY = (0, 30, 60)
RED = (220, 40, 40)

# Fonts
FONT = pygame.font.SysFont("consolas", 28)
SMALL_FONT = pygame.font.SysFont("consolas", 20)
POINTS_FONT = pygame.font.SysFont("consolas", 40)  # Twice as large as SMALL_FONT
POINTS_COLOR = (255, 255, 0)  # Bright yellow

# Game states
MENU = 'menu'
TRAVEL = 'travel'
EVENT = 'event'
MINIGAME = 'minigame'
OUTCOME = 'outcome'

# Set initial state
state = MENU
ied_game = None  # Add this line

# Resources
team = ["Bomb Tech", "Driver", "Robot Operator", "Team Leader"]
fuel = 100
robot_battery = 100
morale = 100

def draw_text(text, font, color, surface, x, y):
    lines = text.split('\n')
    for i, line in enumerate(lines):
        txt = font.render(line, True, color)
        surface.blit(txt, (x, y + i * font.get_height()))

# Load music files
try:
    mission_start_music = os.path.join(current_dir, "assets", "mission_start_whimsical_grand.ogg")
    traveling_music = os.path.join(current_dir, "assets", "traveling_western.ogg")
    minigame_music = os.path.join(current_dir, "assets", "ied_minigame_dangerzone.ogg")
    gameover_music = os.path.join(current_dir, "assets", "game_over_anchors_aweigh.ogg")
    
    MUSIC_TRACKS = {
        'menu': mission_start_music,
        'travel': traveling_music,
        'minigame': minigame_music,
        'gameover': gameover_music
    }
    
    # Initially load menu music
    pygame.mixer.music.load(MUSIC_TRACKS['menu'])
    pygame.mixer.music.set_volume(0.5)
    print("Music tracks loaded successfully")
    MUSIC_LOADED = True
except pygame.error as e:
    print(f"Error loading music: {e}")
    MUSIC_LOADED = False

def change_music(track_key):
    """Switch to a different music track"""
    if MUSIC_LOADED:
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            pygame.mixer.music.load(MUSIC_TRACKS[track_key])
            pygame.mixer.music.play(-1)  # Loop indefinitely
            print(f"Changed music to {track_key} track")
        except pygame.error as e:
            print(f"Error changing music: {e}")

def menu_screen():
    global current_music_playing
    
    # Only try to play music if it was successfully loaded
    if MUSIC_LOADED and not pygame.mixer.music.get_busy():
        try:
            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
            print("Started playing menu music")
        except pygame.error as e:
            print(f"Error playing menu music: {e}")
    
    # Clear screen first
    SCREEN.fill(BLACK)
    
    # Make sure menu_background exists and is loaded
    if menu_background:
        SCREEN.blit(menu_background, (0, 0))
    
    # Make text more visible - adjust color if needed
    text_color = WHITE
    draw_text("1. Start Mission", SMALL_FONT, text_color, SCREEN, WIDTH//2 - 100, HEIGHT//2)
    draw_text("2. Quit Game", SMALL_FONT, text_color, SCREEN, WIDTH//2 - 100, HEIGHT//2 + 40)
    draw_text("3. TBD", SMALL_FONT, text_color, SCREEN, WIDTH//2 - 100, HEIGHT//2 + 80)
    draw_text("4. TBD", SMALL_FONT, text_color, SCREEN, WIDTH//2 - 100, HEIGHT//2 + 120)
    draw_text("5. TBD", SMALL_FONT, text_color, SCREEN, WIDTH//2 - 100, HEIGHT//2 + 160)

def event_screen(event):
    """Display the event screen"""
    SCREEN.fill((0, 0, 0))  # Clear the screen with a black background

    # Access the description attribute of the Event object
    draw_text(event.description, SMALL_FONT, WHITE, SCREEN, 180, 200)

    # Display safe and risky choices
    draw_text("1. " + event.safe_choice, SMALL_FONT, WHITE, SCREEN, 180, 300)
    # Comment out risky choice display
    # draw_text("2. " + event.risk_choice, SMALL_FONT, WHITE, SCREEN, 180, 350)

    pygame.display.flip()

def minigame_screen():
    global ied_game, state, robot_battery, success, points, travel_start_ticks

    if ied_game is None:
        ied_game = IEDMiniGame(WIDTH, HEIGHT, robot_battery)
        # No need to change music here since it's handled in state transition

    # If the game is over, handle different scenarios
    if ied_game.game_over:
        if ied_game.success:
            # Success handling...
            pass
        else:
            if ied_game.lives > 0:
                # Lost a life but still have lives remaining
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                print(f"Life lost. Lives remaining: {ied_game.lives}")
                ied_game.draw_transition_page(SCREEN)
                pygame.display.flip()
                pygame.time.delay(2000)
                state = TRAVEL
                travel_start_ticks = pygame.time.get_ticks()
                
                # Create new IED game instance with current lives
                current_lives = ied_game.lives  # Store current lives
                ied_game = IEDMiniGame(WIDTH, HEIGHT, robot_battery)
                ied_game.lives = current_lives  # Restore lives count
                
                change_music('travel')
            else:
                # No lives remaining - Game Over
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                change_music('gameover')
                print("No lives remaining. Game Over.")
                success = False
                state = OUTCOME
                if game_start_ticks is not None:
                    elapsed_ms = pygame.time.get_ticks() - game_start_ticks
                    points = elapsed_ms // 1000
                ied_game = None
        return

    # Update and draw the minigame
    ied_game.update()
    ied_game.draw(SCREEN)

def outcome_screen(success):
    if success:
        pass
    else:
        # Ensure game over music is playing
        if MUSIC_LOADED and not pygame.mixer.music.get_busy():
            change_music('gameover')
            
        try:
            gameover_path = os.path.join(current_dir, "assets", "game_over.png")
            gameover_image = pygame.image.load(gameover_path).convert()
            gameover_image = pygame.transform.scale(gameover_image, (WIDTH, HEIGHT))
            SCREEN.blit(gameover_image, (0, 0))
        except pygame.error as e:
            print(f"Error loading game over image: {e}")
            SCREEN.fill((50, 0, 0))  # Fallback to red background

        # Larger, bolder Game Over text
        big_bold_font = pygame.font.SysFont("consolas", 80, bold=True)
        game_over_text = big_bold_font.render("Game Over", True, RED)
        SCREEN.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 180))

        # Initial Success or Total Failure text
        draw_text("Initial Success or Total Failure", FONT, WHITE, SCREEN, WIDTH // 2 - 250, HEIGHT // 2 - 50)

        # Bold yellow points text
        bold_points_font = pygame.font.SysFont("consolas", 40, bold=True)
        points_text = f"Points: {points}"
        rendered_points = bold_points_font.render(points_text, True, POINTS_COLOR)
        points_y = HEIGHT - 100
        SCREEN.blit(rendered_points, (WIDTH // 2 - rendered_points.get_width() // 2, points_y))

        # Move "Press Q to quit" halfway between the above two
        failure_y = HEIGHT // 2 - 50 + FONT.get_height()
        halfway_y = failure_y + (points_y - failure_y) // 2
        quit_text = SMALL_FONT.render("Press Q to quit", True, WHITE)
        SCREEN.blit(quit_text, (WIDTH // 2 - quit_text.get_width() // 2, halfway_y))

current_event = None
game_start_ticks = None  # Track when the game starts
points = 0               # Player's points
travel_start_ticks = None

# Main loop
running = True
success = True
while running:
    # Handle events first
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if state == MENU:
                if event.key == pygame.K_1:
                    change_music('travel')  # Start travel music
                    state = TRAVEL
                    travel_start_ticks = pygame.time.get_ticks()
                    game_start_ticks = pygame.time.get_ticks()
                    points = 0
                elif event.key == pygame.K_2:
                    running = False
                elif event.key == pygame.K_3:
                    pass  # TBD - Placeholder for future feature
                elif event.key == pygame.K_4:
                    pass  # TBD - Placeholder for future feature
                elif event.key == pygame.K_5:
                    pass  # TBD - Placeholder for future feature
            elif state == EVENT:
                if event.key == pygame.K_1:
                    # Safe choice - Initialize minigame
                    outcomes = game_events.handle_choice(current_event, True)
                    if current_event.description.startswith("IED detected"):
                        state = MINIGAME  # Transition to minigame instead of TRAVEL
                    else:
                        morale = min(morale + outcomes['morale'], 100)
                        fuel = max(fuel + outcomes['fuel'], 0)
                        robot_battery = max(min(robot_battery + outcomes['robot_battery'], 100), 0)
                        state = TRAVEL
                # Comment out risky choice logic
                # elif event.key == pygame.K_2:
                #     # Risky choice - Initialize minigame
                #     outcomes = game_events.handle_choice(current_event, False)
                #     if current_event.description.startswith("IED detected"):
                #         state = MINIGAME  # Transition to minigame instead of TRAVEL
                #     else:
                #         morale = max(morale + outcomes['morale'], 0)
                #         fuel = max(fuel + outcomes['fuel'], 0)
                #         robot_battery = max(min(robot_battery + outcomes['robot_battery'], 100), 0)
                #         if morale <= 0:
                #             success = False
                #             state = OUTCOME
                #         else:
                #             state = TRAVEL
            elif state == OUTCOME:
                if event.key == pygame.K_q:
                    running = False
            elif state == MINIGAME:
                # Process events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            ied_game.switch_sprite()  # Call the switch_sprite method

                # Get keyboard state for movement
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    ied_game.move_player(-1, 0)
                if keys[pygame.K_RIGHT]:
                    ied_game.move_player(1, 0)
                if keys[pygame.K_UP]:
                    ied_game.move_player(0, -1)
                if keys[pygame.K_DOWN]:
                    ied_game.move_player(0, 1)

                # Update and draw the minigame
                minigame_screen()
    
    # Draw current screen
    if state == MENU:
        menu_screen()
    elif state == TRAVEL:
        # Check for automatic transition after 3 seconds
        if travel_start_ticks is not None:
            elapsed_travel = (pygame.time.get_ticks() - travel_start_ticks) / 1000
            if elapsed_travel >= 3:
                # Clean transition to minigame state and music
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                state = MINIGAME
                travel_start_ticks = None  # Reset timer
                # Start minigame music immediately when transitioning
                change_music('minigame')
        travel_screen()
    elif state == MINIGAME:
        minigame_screen()
    elif state == OUTCOME:
        outcome_screen(success)

    pygame.display.flip()
    pygame.time.Clock().tick(60)  # Increased to 60 FPS for smoother movement

pygame.mixer.music.stop()
pygame.mixer.quit()
pygame.quit()
sys.exit()

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
