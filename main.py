import pygame
import sys
import random
import math
import os 

# Initialize Pygame
pygame.init()

# Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Window settings
WIDTH, HEIGHT = 1024, 768
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bomb Squad Trail")

# Load background sprite
try:
    menu_background_path = os.path.join(current_dir, "assets", "mission_start_background.png")
    menu_background = pygame.image.load(menu_background_path).convert()
    menu_background = pygame.transform.scale(menu_background, (WIDTH, HEIGHT))
    print(f"Menu background loaded: {menu_background.get_size()}")
except pygame.error as e:
    print(f"Couldn't load menu background: {e}")
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
    # Use background image instead of solid color
    SCREEN.blit(menu_background, (0, 0))
    
    # Only show numbers and options
    draw_text("1. Start Mission", SMALL_FONT, WHITE, SCREEN, 320, 240)
    draw_text("2. Quit Game", SMALL_FONT, WHITE, SCREEN, 320, 280)
    draw_text("3. TBD", SMALL_FONT, WHITE, SCREEN, 320, 320)
    draw_text("4. TBD", SMALL_FONT, WHITE, SCREEN, 320, 360)
    draw_text("5. TBD", SMALL_FONT, WHITE, SCREEN, 320, 400)

def event_screen(event_text):
    SCREEN.fill(NAVY)
    draw_text("Random Event!", FONT, WHITE, SCREEN, 280, 120)
    draw_text(event_text, SMALL_FONT, WHITE, SCREEN, 180, 200)
    draw_text("1. Take the safe route", SMALL_FONT, WHITE, SCREEN, 180, 280)
    draw_text("2. Take a risk", SMALL_FONT, WHITE, SCREEN, 180, 320)

def minigame_screen():
    SCREEN.fill((30, 30, 60))
    draw_text("Bomb Defusal (placeholder)", FONT, WHITE, SCREEN, 180, 180)
    draw_text("Press SPACE to return to travel", SMALL_FONT, WHITE, SCREEN, 230, 400)

def outcome_screen(success):
    SCREEN.fill((10, 50, 10))
    if success:
        draw_text("Mission Success!", FONT, WHITE, SCREEN, 280, 220)
    else:
        draw_text("Mission Failed!", FONT, RED, SCREEN, 280, 220)
    draw_text("Press Q to quit.", SMALL_FONT, WHITE, SCREEN, 330, 300)

# Example event
event_options = [
    "IED detected ahead! How will you respond?",
    "Truck breaks down. What do you do?",
    "Talon robot battery low. Continue or stop to charge?",
]
current_event = ""

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
                    # Random chance for event
                    if random.randint(1, 3) == 1:
                        current_event = random.choice(event_options)
                        state = EVENT
                    else:
                        pass  # No event occurs, continue traveling or add logic here
            elif state == EVENT:
                if event.key == pygame.K_1:
                    # Good choice: +morale, -fuel
                    morale = min(morale + 5, 100)
                    fuel = max(fuel - 10, 0)
                    state = TRAVEL
                elif event.key == pygame.K_2:
                    # Bad choice: -morale, maybe fail
                    morale = max(morale - 10, 0)
                    if morale <= 0:
                        success = False
                        state = OUTCOME
                    else:
                        state = TRAVEL
            elif state == MINIGAME:
                if event.key == pygame.K_SPACE:
                    state = OUTCOME
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
    elif state == OUTCOME:
        outcome_screen(success)

    pygame.display.flip()
    pygame.time.Clock().tick(30)

pygame.quit()
sys.exit()
