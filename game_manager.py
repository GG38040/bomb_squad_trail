import pygame
from states import GameState
from screens import MenuScreen, TravelScreen, MinigameScreen, OutcomeScreen
from game import IEDMiniGame


class GameManager:
    def __init__(
        self, width, height, asset_loader, music_manager, font_manager
    ):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialize managers
        self.asset_loader = asset_loader
        self.music_manager = music_manager
        self.font_manager = font_manager

        # Initialize screens
        self.screens = {
            GameState.MENU: MenuScreen(
                width, height, asset_loader, font_manager, music_manager
            ),
            GameState.TRAVEL: TravelScreen(
                width, height, asset_loader, font_manager, music_manager
            ),
            GameState.MINIGAME: MinigameScreen(
                width, height, asset_loader, font_manager, music_manager
            ),
            GameState.OUTCOME: OutcomeScreen(
                width, height, asset_loader, font_manager, music_manager
            ),
        }

        # Initialize game state
        self.current_state = GameState.MENU
        self.game_data = {
            'points': 0,
            'lives': 3,
            'battery': 100,
            'fuel': 100,
            'morale': 100
        }

        # Add points tracking
        self.game_start_time = None

        # Initialize timers
        self.timers = {
            'travel': None,
            'game_start': None
        }

        # Start menu music
        self.music_manager.play('menu')

        self.operator_mode = False

    def handle_input(self):
        """Handle input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)

            # Pass events to menu screen for code input
            if self.current_state == GameState.MENU:
                self.screens[GameState.MENU].handle_input(event)

        # Handle continuous input for minigame
        if self.current_state == GameState.MINIGAME:
            self.screens[GameState.MINIGAME].handle_input(None)

    def handle_keydown(self, key):
        """Handle keyboard input"""
        if self.current_state == GameState.MENU:
            if key == pygame.K_1:
                menu_screen = self.screens[GameState.MENU]
                # Check for operator code
                if menu_screen.code_input in ["5337", "5335"]:
                    self.operator_mode = True
                    print("Operator mode activated")

                self.music_manager.play('travel')  # Start travel music
                self.current_state = GameState.TRAVEL
                self.timers['travel'] = pygame.time.get_ticks()
                self.game_start_time = pygame.time.get_ticks()
                # Start tracking time
            elif key == pygame.K_2:
                self.running = False

    def update(self):
        """Update game state"""
        # Only update points if not in OUTCOME state
        if (
            self.current_state != GameState.OUTCOME
            and self.game_start_time is not None
        ):
            elapsed_seconds = (
                pygame.time.get_ticks() - self.game_start_time
            ) // 1000
            self.game_data['points'] = elapsed_seconds

        current_screen = self.screens.get(self.current_state)
        if not current_screen:
            return

        if self.current_state == GameState.TRAVEL:
            current_screen.update()  # Update truck animation

            # Check for automatic transition to minigame
            if self.timers['travel'] is not None:
                elapsed = (
                    pygame.time.get_ticks() - self.timers['travel']
                ) / 1000
                if elapsed >= 3:  # Transition after 3 seconds
                    self.transition_to_minigame()
                    return

        if self.current_state == GameState.MINIGAME:
            current_screen.update()
            minigame = current_screen.ied_game

            if minigame:
                minigame.points = self.game_data['points']

            if minigame and minigame.game_over:
                if minigame.success:
                    minigame.draw_celebration_screen(self.screen)
                    pygame.display.flip()
                    pygame.time.delay(2000)
                    self.game_data['points'] += 100  # Bonus points for success
                    self.current_state = GameState.TRAVEL
                    self.timers['travel'] = pygame.time.get_ticks()
                    self.music_manager.play('travel')
                else:
                    # Update lives in game_data and minigame
                    if self.game_data['lives'] > 0:
                        self.game_data['lives'] -= 1
                        minigame.lives = self.game_data['lives']  # Sync lives
                        print(
                            f"Life lost. Lives remaining: "
                            f"{self.game_data['lives']}"
                        )

                    if self.game_data['lives'] <= 0:
                        # Game over - freeze final score
                        print(
                            f"Game Over. Final score: "
                            f"{self.game_data['points']}"
                        )
                        self.current_state = GameState.OUTCOME
                        self.music_manager.play('gameover')
                    else:
                        minigame.draw_transition_page(self.screen)
                        pygame.display.flip()
                        pygame.time.delay(2000)
                        self.current_state = GameState.TRAVEL
                        self.timers['travel'] = pygame.time.get_ticks()
                        self.music_manager.play('travel')

    def draw(self):
        """Draw current game state"""
        current_screen = self.screens.get(self.current_state)
        if current_screen:
            current_screen.draw(self.screen, self.game_data)

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)

    def transition_to_minigame(self):
        """Handle transition to minigame state"""
        self.music_manager.play('minigame')
        minigame_screen = self.screens[GameState.MINIGAME]
        minigame_screen.init_game(
            battery=self.game_data['battery'],
            lives=self.game_data['lives'],
            operator_mode=self.operator_mode,
            points=self.game_data['points'],
        )
        print(
            f"Transitioning to minigame with {self.game_data['lives']} lives"
        )
        self.current_state = GameState.MINIGAME
        self.timers['travel'] = None
