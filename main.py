import pygame
import sys
import os
from game_manager import GameManager
from utils import AssetLoader, MusicManager, FontManager

class BombSquadTrail:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Get current directory
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Initialize managers
        self.asset_loader = AssetLoader(self.current_dir)
        self.music_manager = MusicManager(self.current_dir)
        self.font_manager = FontManager()
        self.game_manager = GameManager(1024, 768, 
                                      self.asset_loader, 
                                      self.music_manager, 
                                      self.font_manager)
    
    def run(self):
        """Start and run the game"""
        try:
            self.game_manager.run()
        except Exception as e:
            print(f"Error running game: {e}")
        finally:
            # Cleanup
            pygame.mixer.quit()
            pygame.quit()
            sys.exit()

def main():
    game = BombSquadTrail()
    game.run()

if __name__ == "__main__":
    main()
