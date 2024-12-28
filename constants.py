import os

# Screen dimensions
BOARD_SIZE = 512
SQUARE_SIZE = BOARD_SIZE // 8

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT_YELLOW = (255, 255, 0, 128)
HIGHLIGHT_GREEN = (0, 255, 0, 128)
HIGHLIGHT_RED = (255, 0, 0, 128)

# Font settings
FONT_SIZE = 32
SMALL_FONT_SIZE = 24

# Button dimensions
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50

# Paths
ASSETS_DIR = "assets"
PIECES_DIR = os.path.join(ASSETS_DIR, "chess_pieces")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

# Sound files
MOVE_SOUND = os.path.join(SOUNDS_DIR, "move.wav")
CAPTURE_SOUND = os.path.join(SOUNDS_DIR, "capture.wav")
CASTLE_SOUND = os.path.join(SOUNDS_DIR, "castle.wav")
CHECKMATE_SOUND = os.path.join(SOUNDS_DIR, "checkmate.wav")
DRAW_SOUND = os.path.join(SOUNDS_DIR, "draw.wav")