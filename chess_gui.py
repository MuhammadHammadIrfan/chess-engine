import pygame
import chess
import sys
from chess_engine import ChessEngine
from menu import Menu
from sound_manager import SoundManager
from popup_manager import PopupManager
from constants import *

class ChessGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
        pygame.display.set_caption("Chess Game")
        
        # Initialize managers
        self.sound_manager = SoundManager()
        self.popup_manager = PopupManager(self.screen)
        
        # Show menu and get game mode
        menu = Menu(self.screen)
        self.game_mode = menu.run()
        if self.game_mode is None:
            sys.exit()
            
        # Initialize game state
        self.board = chess.Board()
        self.engine = ChessEngine(depth=6, time_limit=3.0) if self.game_mode == "AI" else None
        
        # Load piece images
        self.pieces = {}
        pieces = ['b_p', 'b_n', 'b_b', 'b_r', 'b_q', 'b_k', 
                 'w_p', 'w_n', 'w_b', 'w_r', 'w_q', 'w_k']
        for piece in pieces:
            try:
                self.pieces[piece] = pygame.transform.scale(
                    pygame.image.load(f"{PIECES_DIR}/{piece}.png"),
                    (SQUARE_SIZE, SQUARE_SIZE)
                )
            except pygame.error as e:
                print(f"Error loading piece image {piece}: {e}")
                sys.exit(1)
            
        # Game state variables
        self.selected_square = None
        self.legal_moves = []
        self.game_over = False
        self.promotion_dialog_active = False
        self.pending_promotion_move = None
        
    def get_square_from_pos(self, pos):
        x, y = pos
        file = x // SQUARE_SIZE
        rank = 7 - (y // SQUARE_SIZE)
        return chess.square(file, rank)
        
    def get_pos_from_square(self, square):
        file = chess.square_file(square)
        rank = 7 - chess.square_rank(square)
        return (file * SQUARE_SIZE, rank * SQUARE_SIZE)
        
    def draw_board(self):
        for rank in range(8):
            for file in range(8):
                color = LIGHT_SQUARE if (rank + file) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(
                    self.screen,
                    color,
                    (file * SQUARE_SIZE, rank * SQUARE_SIZE, 
                     SQUARE_SIZE, SQUARE_SIZE)
                )
                
    def draw_pieces(self):
        symbol_to_filename = {
            'p': 'b_p', 'n': 'b_n', 'b': 'b_b', 'r': 'b_r', 'q': 'b_q', 'k': 'b_k',
            'P': 'w_p', 'N': 'w_n', 'B': 'w_b', 'R': 'w_r', 'Q': 'w_q', 'K': 'w_k'
        }
        
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                piece_symbol = piece.symbol()
                filename = symbol_to_filename[piece_symbol]
                pos = self.get_pos_from_square(square)
                self.screen.blit(self.pieces[filename], pos)

    def highlight_last_move(self):
        if self.board.move_stack:
            last_move = self.board.peek()
            for square in [last_move.from_square, last_move.to_square]:
                pos = self.get_pos_from_square(square)
                surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                surface.fill((255, 255, 0, 50))  # Light yellow
                self.screen.blit(surface, pos)
                
    def highlight_moves(self):
        if self.selected_square is not None:
            # Highlight selected square
            pos = self.get_pos_from_square(self.selected_square)
            surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            surface.fill(HIGHLIGHT_YELLOW)
            self.screen.blit(surface, pos)
            
            # Highlight legal moves
            for move in self.legal_moves:
                if move.from_square == self.selected_square:
                    pos = self.get_pos_from_square(move.to_square)
                    surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    color = HIGHLIGHT_RED if self.board.is_capture(move) else HIGHLIGHT_GREEN
                    surface.fill(color)
                    self.screen.blit(surface, pos)
                    
        # Highlight king if in check
        if self.board.is_check():
            king_square = self.board.king(self.board.turn)
            pos = self.get_pos_from_square(king_square)
            surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
            surface.fill(HIGHLIGHT_RED)
            self.screen.blit(surface, pos)

    def show_promotion_dialog(self):
        """Shows dialog for pawn promotion piece selection."""
        dialog_width = SQUARE_SIZE * 4
        dialog_height = SQUARE_SIZE
        dialog_x = (BOARD_SIZE - dialog_width) // 2
        dialog_y = (BOARD_SIZE - dialog_height) // 2
        
        # Draw dialog background
        pygame.draw.rect(self.screen, WHITE, 
                        (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(self.screen, BLACK, 
                        (dialog_x, dialog_y, dialog_width, dialog_height), 2)
        
        # Draw piece options
        pieces = ['q', 'r', 'b', 'n'] if self.board.turn else ['Q', 'R', 'B', 'N']
        self.promotion_rects = []
        
        for i, piece in enumerate(pieces):
            piece_x = dialog_x + i * SQUARE_SIZE
            piece_rect = pygame.Rect(piece_x, dialog_y, SQUARE_SIZE, SQUARE_SIZE)
            self.promotion_rects.append((piece_rect, piece))
            
            # Draw piece
            symbol_to_filename = {
                'q': 'b_q', 'r': 'b_r', 'b': 'b_b', 'n': 'b_n',
                'Q': 'w_q', 'R': 'w_r', 'B': 'w_b', 'N': 'w_n'
            }
            filename = symbol_to_filename[piece]
            self.screen.blit(self.pieces[filename], (piece_x, dialog_y))
            
        pygame.display.flip()

    def handle_promotion_click(self, pos):
        """Handles click during promotion dialog."""
        for rect, piece in self.promotion_rects:
            if rect.collidepoint(pos):
                promotion_piece = chess.Piece.from_symbol(piece)
                new_move = chess.Move(
                    self.pending_promotion_move.from_square,
                    self.pending_promotion_move.to_square,
                    promotion=promotion_piece.piece_type
                )
                self.make_move(new_move)
                self.promotion_dialog_active = False
                self.pending_promotion_move = None
                return True
        return False

    def is_promotion_move(self, move):
        """Checks if a move is a pawn promotion."""
        piece = self.board.piece_at(move.from_square)
        if piece is None or piece.piece_type != chess.PAWN:
            return False
            
        rank = chess.square_rank(move.to_square)
        return rank == 7 if piece.color else rank == 0
            
    def make_move(self, move):
        """Makes a move on the board and handles game state changes."""
        is_capture = self.board.is_capture(move)
        is_castle = self.board.is_castling(move)
        
        self.board.push(move)
        self.sound_manager.play_move(is_capture, is_castle)
        
        # Reset selection and legal moves before drawing
        self.selected_square = None
        self.legal_moves = []
        
        # Force update the display after the move
        self.draw_game_state()
        
        # Check game state
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn else "White"
            self.sound_manager.play_game_end(is_checkmate=True)
            self.game_over = True
            self.popup_manager.show_popup(f"Checkmate! {winner} wins!")
        elif self.board.is_stalemate():
            self.sound_manager.play_game_end()
            self.game_over = True
            self.popup_manager.show_popup("Stalemate! Game is drawn.")
        elif self.board.is_insufficient_material():
            self.sound_manager.play_game_end()
            self.game_over = True
            self.popup_manager.show_popup("Draw by insufficient material!")
        elif self.board.is_fifty_moves():
            self.sound_manager.play_game_end()
            self.game_over = True
            self.popup_manager.show_popup("Draw by fifty-move rule!")
        elif self.board.is_repetition():
            self.sound_manager.play_game_end()
            self.game_over = True
            self.popup_manager.show_popup("Draw by repetition!")
            
    def make_ai_move(self):
        """Makes AI move if playing against computer."""
        move = self.engine.get_best_move(self.board)
        if move:
            self.make_move(move)
            
    def draw_game_state(self):
        """Draws the current game state."""
        # Draw base board
        self.draw_board()
        
        # Draw highlights
        self.highlight_last_move()
        self.highlight_moves()
        
        # Draw pieces
        self.draw_pieces()
        
        # Update display
        pygame.display.flip()
            
    def run(self):
        """Main game loop."""
        running = True
        while running:
            current_turn = self.board.turn  # Store current turn for comparison
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if not self.game_over:
                    if self.promotion_dialog_active:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if not self.handle_promotion_click(event.pos):
                                self.promotion_dialog_active = False
                                self.pending_promotion_move = None
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        square = self.get_square_from_pos(pos)
                        
                        if self.selected_square is None:
                            piece = self.board.piece_at(square)
                            if piece and piece.color == self.board.turn and (
                                self.game_mode != "AI" or piece.color == chess.WHITE
                            ):
                                self.selected_square = square
                                self.legal_moves = list(self.board.legal_moves)
                        else:
                            move = chess.Move(self.selected_square, square)
                            promotion_moves = [
                                m for m in self.legal_moves
                                if m.from_square == self.selected_square 
                                and m.to_square == square 
                                and m.promotion is not None
                            ]
                            
                            if promotion_moves:
                                self.promotion_dialog_active = True
                                self.pending_promotion_move = move
                            elif move in self.legal_moves:
                                self.make_move(move)
                                
                            self.selected_square = None
                            self.legal_moves = []
                                
            # Make AI move if it's AI's turn
            if (not self.game_over and 
                self.game_mode == "AI" and 
                self.board.turn == chess.BLACK and 
                not self.promotion_dialog_active):
                self.make_ai_move()
                
            # Draw current game state
            self.draw_game_state()
            
            # Show promotion dialog if active
            if self.promotion_dialog_active:
                self.show_promotion_dialog()
                
        pygame.quit()