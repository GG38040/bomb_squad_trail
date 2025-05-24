from enum import Enum

class GameState(Enum):
    MENU = 'menu'
    TRAVEL = 'travel'
    MINIGAME = 'minigame'
    OUTCOME = 'outcome'

class StateManager:
    def __init__(self):
        self.current_state = GameState.MENU
        self.previous_state = None
        self.game_data = {
            'points': 0,
            'lives': 3,
            'battery': 100,
            'fuel': 100,
            'morale': 100
        }
        self.timers = {
            'game_start': None,
            'travel': None
        }
    
    def change_state(self, new_state):
        """Change game state and store previous state"""
        self.previous_state = self.current_state
        self.current_state = new_state
        
    def update_timer(self, timer_key, time_value):
        """Update specific timer"""
        self.timers[timer_key] = time_value
        
    def get_timer(self, timer_key):
        """Get specific timer value"""
        return self.timers.get(timer_key)