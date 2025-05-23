import pygame
import sys
import random
import math
import os
from game import GameEvents, IEDMiniGame

# Initialize Pygame
pygame.init()
game_events = GameEvents()

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
    # Draw background instead of filling with BLACK
    SCREEN.blit(background, (0, 0))
    
    # Update and draw truck first
    update_truck()
    draw_truck(SCREEN)
    
    # Draw text on top
    draw_text("Traveling to next mission site...", FONT, WHITE, SCREEN, 150, 120)
    draw_text(f"Fuel: {fuel} | Robot Battery: {robot_battery} | Morale: {morale}", 
              SMALL_FONT, WHITE, SCREEN, 180, 200)
    draw_text("Press SPACE to continue", SMALL_FONT, WHITE, SCREEN, 250, 400)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NAVY = (0, 30, 60)
RED = (220, 40, 40)

# Fonts
FONT = pygame.font.SysFont("consolas", 28)
SMALL_FONT = pygame.font.SysFont("consolas", 20)

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

def menu_screen():
    # Clear screen first
    SCREEN.fill(BLACK)
    
    # Make sure menu_background exists and is loaded
    if menu_background:
        SCREEN.blit(menu_background, (0, 0))
    
    # Add debug print
    # print(f"Current game state: {state}")
    
    # Make text more visible - adjust color if needed
    text_color = WHITE
    draw_text("1. Start Mission", SMALL_FONT, text_color, SCREEN, WIDTH//2 - 100, HEIGHT//2)
    draw_text("2. Quit Game", SMALL_FONT, text_color, SCREEN, WIDTH//2 - 100, HEIGHT//2 + 40)
    draw_text("3. TBD", SMALL_FONT, text_color, SCREEN, WIDTH//2 - 100, HEIGHT//2 + 80)
    draw_text("4. TBD", SMALL_FONT, text_color, SCREEN, WIDTH//2 - 100, HEIGHT//2 + 120)
    draw_text("5. TBD", SMALL_FONT, text_color, SCREEN, WIDTH//2 - 100, HEIGHT//2 + 160)

def event_screen(event):
    SCREEN.fill(NAVY)
    draw_text("Random Event!", FONT, WHITE, SCREEN, 280, 120)
    draw_text(event.description, SMALL_FONT, WHITE, SCREEN, 180, 200)  # Use event.description
    draw_text(f"1. {event.safe_choice}", SMALL_FONT, WHITE, SCREEN, 180, 280)  # Use event.safe_choice
    draw_text(f"2. {event.risk_choice}", SMALL_FONT, WHITE, SCREEN, 180, 320)  # Use event.risk_choice

def minigame_screen():
    global ied_game, state, morale, robot_battery, success
    
    if ied_game is None:
        ied_game = IEDMiniGame(WIDTH, HEIGHT, morale, robot_battery)
    
    # Update game state
    ied_game.update()
    
    # Draw game
    ied_game.draw(SCREEN)
    
    # Display controls
    draw_text("Arrow keys to move, SPACE to switch operator", 
             SMALL_FONT, WHITE, SCREEN, 180, HEIGHT - 40)
    
    if ied_game.game_over:
        if ied_game.success:
            morale = ied_game.morale
            robot_battery = ied_game.battery
            success = True
        else:
            success = False
        state = OUTCOME
        ied_game = None  # Reset for next time

def outcome_screen(success):
    if success:
        # Victory screen for completing IED minigame
        SCREEN.fill((0, 50, 0))  # Dark green background
        draw_text("HOYAHHH NAVY EOD!!!", FONT, WHITE, SCREEN, WIDTH//2 - 200, HEIGHT//2 - 50)
        draw_text("LLTB", FONT, WHITE, SCREEN, WIDTH//2 - 50, HEIGHT//2 + 50)
        draw_text("Press Q to continue", SMALL_FONT, WHITE, SCREEN, WIDTH//2 - 100, HEIGHT - 100)
    else:
        # Load and display game over background
        try:
            gameover_path = os.path.join(current_dir, "assets", "game_over.png")
            gameover_image = pygame.image.load(gameover_path).convert()
            gameover_image = pygame.transform.scale(gameover_image, (WIDTH, HEIGHT))
            SCREEN.blit(gameover_image, (0, 0))
        except pygame.error as e:
            print(f"Error loading game over image: {e}")
            SCREEN.fill((50, 0, 0))  # Fallback to red background
            
        draw_text("Game Over", FONT, RED, SCREEN, WIDTH//2 - 100, HEIGHT//2 - 50)
        draw_text("Initial Success or Total Failure", FONT, WHITE, SCREEN, WIDTH//2 - 250, HEIGHT//2 + 50)
        draw_text("Press Q to quit", SMALL_FONT, WHITE, SCREEN, WIDTH//2 - 100, HEIGHT - 100)

current_event = None

# Main loop
running = True
success = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if state == MENU:
                if event.key == pygame.K_1:
                    state = TRAVEL
                elif event.key == pygame.K_2:
                    running = False
                elif event.key == pygame.K_3:
                    pass  # TBD - Placeholder for future feature
                elif event.key == pygame.K_4:
                    pass  # TBD - Placeholder for future feature
                elif event.key == pygame.K_5:
                    pass  # TBD - Placeholder for future feature
            elif state == TRAVEL:
                if event.key == pygame.K_SPACE:
                    if random.randint(1, 3) == 1:
                        current_event = game_events.get_random_event()  # Get Event object instead of string
                        state = EVENT
                    else:
                        pass
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
                elif event.key == pygame.K_2:
                    # Risky choice - Initialize minigame
                    outcomes = game_events.handle_choice(current_event, False)
                    if current_event.description.startswith("IED detected"):
                        state = MINIGAME  # Transition to minigame instead of TRAVEL
                    else:
                        morale = max(morale + outcomes['morale'], 0)
                        fuel = max(fuel + outcomes['fuel'], 0)
                        robot_battery = max(min(robot_battery + outcomes['robot_battery'], 100), 0)
                        if morale <= 0:
                            success = False
                            state = OUTCOME
                        else:
                            state = TRAVEL
            elif state == MINIGAME:
                keys = pygame.key.get_pressed()  # Get all currently pressed keys
                if keys[pygame.K_LEFT]:
                    ied_game.move_player(-1, 0)
                if keys[pygame.K_RIGHT]:
                    ied_game.move_player(1, 0)
                if keys[pygame.K_UP]:
                    ied_game.move_player(0, -1)
                if keys[pygame.K_DOWN]:
                    ied_game.move_player(0, 1)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    ied_game.switch_sprite()
            elif state == OUTCOME:
                if event.key == pygame.K_q:
                    running = False

    # Draw current screen
    if state == MENU:
        menu_screen()
    elif state == TRAVEL:
        travel_screen()
    elif state == EVENT:
        event_screen(current_event)
    elif state == MINIGAME:
        minigame_screen()
        if ied_game and ied_game.game_over:
            if ied_game.success:
                pygame.time.delay(2000)  # Show victory screen for 2 seconds
                state = TRAVEL
            else:
                pygame.time.delay(3000)  # Show game over screen longer
                success = False
                state = OUTCOME
    elif state == OUTCOME:
        outcome_screen(success)
        # Only continue if successful, otherwise quit
        if success and event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            state = TRAVEL
        elif not success and event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            running = False

    pygame.display.flip()
    pygame.time.Clock().tick(30)

pygame.quit()
sys.exit()
