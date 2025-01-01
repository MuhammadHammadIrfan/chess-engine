import chess
import time
from typing import Optional, Tuple, List
from evaluation import ChessEvaluator

class ChessEngine:
    def __init__(self, depth: int, time_limit: float):
        self.depth = depth
        self.time_limit = time_limit
        self.evaluator = ChessEvaluator()
        self.start_time = 0
        self.position_history = {}

    def order_moves(self, board: chess.Board, moves: List[chess.Move]) -> List[chess.Move]:
        """Orders moves based on basic heuristics, prioritizing checkmate moves and defense."""
        move_scores = []
        for move in moves:
            score = 0
            moving_piece = board.piece_at(move.from_square)
            captured_piece = board.piece_at(move.to_square)
            
            # Check for immediate checkmate (highest priority)
            board.push(move)
            if board.is_checkmate():
                score += 10000  # Extremely high score for checkmate
            elif board.is_check():
                score += 30
                # Extra bonus for checks in winning positions
                if self.evaluator.evaluate(board) > 500:  # If we're winning
                    score += 50
                
                # Simulate opponent's response to check
                opponent_moves = list(board.legal_moves)
                for opponent_move in opponent_moves:
                    board.push(opponent_move)
                    if board.is_capture(opponent_move) and board.piece_at(opponent_move.to_square) == moving_piece:
                        score -= 100  # Penalize if the piece giving check is captured
                    board.pop()
            board.pop()
            
            # Prioritize captures based on MVV-LVA (Most Valuable Victim - Least Valuable Aggressor)
            if captured_piece:
                score += 10 * self.evaluator.PIECE_VALUES[captured_piece.piece_type] - \
                        self.evaluator.PIECE_VALUES[moving_piece.piece_type]
            
            # Prioritize promotions
            if move.promotion:
                score += 800
            
            # Prioritize central squares for pieces
            to_rank = chess.square_rank(move.to_square)
            to_file = chess.square_file(move.to_square)
            center_distance = abs(3.5 - to_file) + abs(3.5 - to_rank)
            score -= center_distance * 10
            
            # Penalize moves that lead to repetition in winning positions
            board.push(move)
            pos_hash = board.fen().split(' ')[0]  # Only consider piece positions
            if pos_hash in self.position_history and self.evaluator.evaluate(board) > 500:
                score -= 400  # Strong penalty for repetition when winning
            board.pop()
            
            # Add defense evaluation
            board.push(move)
            defense_score = self.evaluator._evaluate_piece_defense(board)
            score += defense_score
            board.pop()
            
            move_scores.append((move, score))
        
        # Sort moves by score in descending order
        move_scores.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in move_scores]

    def is_time_up(self) -> bool:
        """Checks if we've exceeded our time limit."""
        return time.time() - self.start_time > self.time_limit

    def alpha_beta(self, board: chess.Board, depth: int, alpha: float, beta: float, maximizing_player: bool) -> Tuple[float, Optional[chess.Move]]:
        """Implements alpha-beta pruning with move ordering and repetition avoidance."""
        if self.is_time_up():
            raise TimeoutError
            
        if depth == 0 or board.is_game_over():
            eval_score = self.evaluator.evaluate(board)
            # Penalize repetitions in winning positions
            pos_hash = board.fen().split(' ')[0]
            if pos_hash in self.position_history and abs(eval_score) > 500:
                eval_score *= 0.8  # Reduce score for repeated positions when winning
            return eval_score, None

        best_move = None
        moves = list(board.legal_moves)
        ordered_moves = self.order_moves(board, moves)

        if maximizing_player:
            max_eval = float('-inf')
            for move in ordered_moves:
                board.push(move)
                pos_hash = board.fen().split(' ')[0]
                self.position_history[pos_hash] = self.position_history.get(pos_hash, 0) + 1
                
                try:
                    eval, _ = self.alpha_beta(board, depth - 1, alpha, beta, False)
                except TimeoutError:
                    board.pop()
                    raise
                    
                self.position_history[pos_hash] -= 1
                board.pop()
                
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in ordered_moves:
                board.push(move)
                pos_hash = board.fen().split(' ')[0]
                self.position_history[pos_hash] = self.position_history.get(pos_hash, 0) + 1
                
                try:
                    eval, _ = self.alpha_beta(board, depth - 1, alpha, beta, True)
                except TimeoutError:
                    board.pop()
                    raise
                    
                self.position_history[pos_hash] -= 1
                board.pop()
                
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def iterative_deepening(self, board: chess.Board) -> Optional[chess.Move]:
        """Implements iterative deepening within time constraints."""
        best_move = None
        current_depth = 1
        
        try:
            while current_depth <= self.depth and not self.is_time_up():
                _, move = self.alpha_beta(board, current_depth, float('-inf'), float('inf'), True)
                if move:  # Only update if we found a valid move
                    best_move = move
                current_depth += 1
                
        except TimeoutError:
            pass  # Time's up, return the best move found so far
            
        return best_move

    def get_best_move(self, board: chess.Board) -> Optional[chess.Move]:
        """Returns the best move for the current position using iterative deepening."""
        self.start_time = time.time()
        self.position_history = {}  # Reset position history for new search
        best_move = self.iterative_deepening(board)
        end_time = time.time()
        print(f"Move found in {end_time - self.start_time:.2f} seconds at depth {self.depth}")
        return best_move
