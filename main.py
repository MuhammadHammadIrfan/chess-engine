import pygame
import sys
import os
from chess_gui import ChessGUI

# Global settings
DEPTH = 5
TIME_LIMIT = 5.0

def check_required_files():
    """Check if all required files and directories exist."""
    required_dirs = ['assets', 'assets/chess_pieces', 'assets/sounds']
    required_sounds = ['move.wav', 'capture.wav', 'castle.wav', 'checkmate.wav', 'draw.wav']
    required_pieces = [
        'b_p.png', 'b_n.png', 'b_b.png', 'b_r.png', 'b_q.png', 'b_k.png',
        'w_p.png', 'w_n.png', 'w_b.png', 'w_r.png', 'w_q.png', 'w_k.png'
    ]
    
    # Check directories
    for directory in required_dirs:
        if not os.path.exists(directory):
            print(f"Error: Directory '{directory}' not found.")
            print("Please create the required directory structure.")
            return False
            
    # Check sound files
    for sound in required_sounds:
        path = os.path.join('assets/sounds', sound)
        if not os.path.exists(path):
            print(f"Error: Sound file '{sound}' not found in assets/sounds directory.")
            print("Please ensure all required sound files are present.")
            return False
            
    # Check piece images
    for piece in required_pieces:
        path = os.path.join('assets/chess_pieces', piece)
        if not os.path.exists(path):
            print(f"Error: Piece image '{piece}' not found in assets/chess_pieces directory.")
            print("Please ensure all required piece images are present.")
            return False
            
    return True

def main():
    """Main function to run the chess game."""
    # Check for required files
    if not check_required_files():
        print("\nPlease ensure all required files are present before running the game.")
        print("Required directory structure:")
        print("- assets/")
        print("  - chess_pieces/")
        print("    - [piece images: b_p.png, w_k.png, etc.]")
        print("  - sounds/")
        print("    - [sound files: move.wav, capture.wav, etc.]")
        sys.exit(1)
        
    # Initialize pygame
    pygame.init()
    
    try:
        # Create and run the game
        game = ChessGUI(depth=DEPTH, time_limit=TIME_LIMIT)
        game.run()
    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()
        sys.exit(1)
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()