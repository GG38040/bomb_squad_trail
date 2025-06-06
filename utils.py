import os
import pygame


class AssetLoader:
    def __init__(self, base_path):
        self.base_path = base_path
        self.cached_images = {}
        self.cached_sounds = {}

    def load_image(self, filename, size=None):
        """Load and cache image assets"""
        cache_key = f"{filename}_{size if size else 'original'}"

        if cache_key in self.cached_images:
            return self.cached_images[cache_key]

        try:
            path = os.path.join(self.base_path, "assets", filename)
            image = pygame.image.load(path).convert_alpha()

            if size:
                image = pygame.transform.scale(image, size)

            self.cached_images[cache_key] = image
            return image
        except pygame.error as e:
            print(f"Error loading image {filename}: {e}")
            return None


class MusicManager:
    def __init__(self, base_path):
        self.base_path = base_path
        self.tracks = {
            'menu': "mission_start_whimsical_grand.ogg",
            'travel': "traveling_western.ogg",
            'minigame': "ied_minigame_dangerzone.ogg",
            'gameover': "game_over_anchors_aweigh.ogg"
        }
        self.current_track = None

    def play(self, track_key, volume=0.5):
        """Play a music track"""
        if track_key not in self.tracks:
            return False

        try:
            if (
                self.current_track == track_key
                and pygame.mixer.music.get_busy()
            ):
                return True

            pygame.mixer.music.stop()
            pygame.mixer.music.unload()

            track_path = os.path.join(
                self.base_path, "assets", self.tracks[track_key])
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)

            self.current_track = track_key
            return True
        except pygame.error as e:
            print(f"Error playing music track {track_key}: {e}")
            return False


class FontManager:
    def __init__(self):
        self.fonts = {}
        self.setup_fonts()

    def setup_fonts(self):
        """Initialize common fonts"""
        self.fonts.update({
            'regular': pygame.font.SysFont("consolas", 28),
            'small': pygame.font.SysFont("consolas", 20),
            'large': pygame.font.SysFont("consolas", 40, bold=True),
            'title': pygame.font.SysFont("consolas", 80, bold=True)
        })

    def get_font(self, font_key):
        """Get font by key"""
        return self.fonts.get(font_key)


def draw_text(surface, text, font, color, x, y):
    """Helper function to draw text"""
    rendered = font.render(text, True, color)
    surface.blit(rendered, (x - rendered.get_width()//2, y))
