import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Window settings
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bomb Squad Trail")

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
    SCREEN.fill(NAVY)
    draw_text("Bomb Squad Trail", FONT, WHITE, SCREEN, 280, 120)
    draw_text("1. Start Mission", SMALL_FONT, WHITE, SCREEN, 320, 240)
    draw_text("2. Quit", SMALL_FONT, WHITE, SCREEN, 320, 280)

def travel_screen():
    SCREEN.fill(BLACK)
    draw_text("Traveling to next mission site...", FONT, WHITE, SCREEN, 150, 120)
    draw_text(f"Fuel: {fuel} | Robot Battery: {robot_battery} | Morale: {morale}", SMALL_FONT, WHITE, SCREEN, 180, 200)
    draw_text("Press SPACE to continue", SMALL_FONT, WHITE, SCREEN, 250, 400)

def event_screen(event_text):
    SCREEN.fill((50, 30, 30))
    draw_text("Incident Occurred!", FONT, RED, SCREEN, 260, 100)
    draw_text(event_text, SMALL_FONT, WHITE, SCREEN, 120, 200)
    draw_text("1. Respond Carefully\n2. Rush In", SMALL_FONT, WHITE, SCREEN, 120, 300)

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
