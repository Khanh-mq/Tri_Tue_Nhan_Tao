import asyncio
import pygame
import numpy as np
import random
from pygame import Vector2

from menu import MainMenu

menu = MainMenu()
# Initialize Pygame
pygame.init()

class Connect6:
    def __init__(self, size=19, ai_enabled=True, time_limit=300 ,  sound_enabled = True ):  # time_limit in seconds (5 minutes default)
        self.size = size
        self.cell_size = 30
        self.screen_width = size * self.cell_size
        self.screen_height = size * self.cell_size + 50
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Connect6")
        self.font = pygame.font.SysFont("arial", 24)
        self.button_font = pygame.font.SysFont("arial", 30)
        self.winner_font = pygame.font.SysFont("arial", 48, bold=True)
        self.clock = pygame.time.Clock()
        self.board = np.zeros((size, size), dtype=int)
        self.players = {1: "X", 2: "O"}
        self.turn = 1
        self.move_count = 0
        self.moves_per_turn = 1
        self.ai_enabled = ai_enabled
        self.status_text = ""
        self.game_over = False
        self.game_state = "playing"
        self.last_placed = []
        self.time_limit = time_limit
        self.player1_time = time_limit
        self.player2_time = time_limit
        self.last_update_time = pygame.time.get_ticks() / 1000.0
        self.play_again_rect = pygame.Rect(self.screen_width // 2 - 150, self.screen_height // 2 + 80, 120, 50)
        self.quit_rect = pygame.Rect(self.screen_width // 2 + 30, self.screen_height // 2 + 80, 120, 50)
        self.loop = asyncio.get_event_loop()
        self.sound_enabled = sound_enabled
        self.place_sound = self.create_place_sound()
        if not self.sound_enabled:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            print(f"Connect6 initialized with sound_enabled={self.sound_enabled}, music stopped, music_busy={pygame.mixer.music.get_busy()}")
        else:
            print(f"Connect6 initialized with sound_enabled={self.sound_enabled}, music continues, music_busy={pygame.mixer.music.get_busy()}")
            
            
            
    def create_place_sound(self):
        """Create a sound for placing a piece"""
        try:
            freq = 660
            duration = 0.05
            sample_rate = 44100
            t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
            wave = (np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)
            stereo_wave = np.column_stack((wave, wave)).flatten().tobytes()
            return pygame.mixer.Sound(buffer=stereo_wave)
        except Exception as e:
            print(f"Error creating place sound: {e}")
            return None


    def play_place_sound(self):
        """Play sound when placing a piece"""
        print(f"play_place_sound: sound_enabled={self.sound_enabled}, music_busy={pygame.mixer.music.get_busy()}")
        if self.place_sound:
            self.place_sound.play()
        else:
            print("No place sound played (place_sound is None)")
 
            
    def reset_game(self):
        """Reset the game state for a new game"""
        self.board = np.zeros((self.size, self.size), dtype=int)
        self.turn = 1
        self.move_count = 0
        self.moves_per_turn = 1
        self.status_text = ""
        self.game_over = False
        self.player1_time = self.time_limit
        self.player2_time = self.time_limit
        self.last_update_time = pygame.time.get_ticks() / 1000.0
        self.last_placed = []  # Clear highlighted positions for new game

    def draw_board(self):
        """Draw the game board, pieces, timers, and game over screen"""
        self.screen.fill((255, 255, 255))  # White background
        
        # Draw grid with highlights for last placed positions
        for i in range(self.size):
            for j in range(self.size):
                x, y = i * self.cell_size, j * self.cell_size
                # Highlight cell if it was placed
                if (i, j) in self.last_placed:
                    if self.board[i, j] == 1:
                        pygame.draw.rect(self.screen, (150, 255, 150),  # Green for Player 1
                                        (x, y, self.cell_size, self.cell_size))
                    elif self.board[i, j] == 2:
                        pygame.draw.rect(self.screen, (255, 200, 150),  # Orange for AI
                                        (x, y, self.cell_size, self.cell_size))
                # Draw grid lines
                pygame.draw.rect(self.screen, (0, 0, 0), 
                               (x, y, self.cell_size, self.cell_size), 1)
                # Draw pieces
                if self.board[i, j] == 1:
                    pygame.draw.circle(self.screen, (0, 0, 0), 
                                     (x + self.cell_size // 2, y + self.cell_size // 2), 
                                     self.cell_size // 2 - 5)
                elif self.board[i, j] == 2:
                    pygame.draw.circle(self.screen, (255, 255, 255), 
                                     (x + self.cell_size // 2, y + self.cell_size // 2), 
                                     self.cell_size // 2 - 5)
                    pygame.draw.circle(self.screen, (0, 0, 0), 
                                     (x + self.cell_size // 2, y + self.cell_size // 2), 
                                     self.cell_size // 2 - 5, 1)
        
        # Draw timers and status
        p1_minutes = int(self.player1_time // 60)
        p1_seconds = int(self.player1_time % 60)
        p1_time_text = f"X Time: {p1_minutes:02d}:{p1_seconds:02d}"
        p1_time_surface = self.font.render(p1_time_text, True, (0, 0, 0))
        self.screen.blit(p1_time_surface, (10, self.screen_height - 40))
        
        p2_minutes = int(self.player2_time // 60)
        p2_seconds = int(self.player2_time % 60)
        p2_time_text = f"O Time: {p2_minutes:02d}:{p2_seconds:02d}"
        p2_time_surface = self.font.render(p2_time_text, True, (0, 0, 0))
        p2_time_rect = p2_time_surface.get_rect(topright=(self.screen_width - 10, self.screen_height - 40))
        self.screen.blit(p2_time_surface, p2_time_rect)
        
        status_surface = self.font.render(self.status_text, True, (0, 0, 0))
        status_rect = status_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 40))
        self.screen.blit(status_surface, status_rect)
        
        # Draw game over menu if game is over
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            self.screen.blit(overlay, (0, 0))
            
            # Draw winner text (ensure it appears above buttons)
            if self.status_text:
                winner_surface = self.winner_font.render(self.status_text, True, (255, 255, 255))
                winner_rect = winner_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 80))  # Move higher
                self.screen.blit(winner_surface, winner_rect)
            else:
                # Debug: If status_text is empty, show a default message
                winner_surface = self.winner_font.render("Game Over", True, (255, 255, 255))
                winner_rect = winner_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 80))
                self.screen.blit(winner_surface, winner_rect)
            
            # Draw buttons
            pygame.draw.rect(self.screen, (0, 255, 0), self.play_again_rect)  # Green for Play Again
            pygame.draw.rect(self.screen, (255, 0, 0), self.quit_rect)  # Red for Quit
            
            play_again_text = self.button_font.render("Play Again", True, (0, 0, 0))
            quit_text = self.button_font.render("Quit", True, (0, 0, 0))
            
            play_again_rect = play_again_text.get_rect(center=self.play_again_rect.center)
            quit_rect = quit_text.get_rect(center=self.quit_rect.center)
            
            self.screen.blit(play_again_text, play_again_rect)
            self.screen.blit(quit_text, quit_rect)
        
        pygame.display.flip()

    def update_timers(self):
        """Update the timers based on whose turn it is"""
        if self.game_over:
            return  # Skip timer update if game is over
        
        current_time = pygame.time.get_ticks() / 1000.0
        elapsed_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        if self.turn == 1:
            self.player1_time -= elapsed_time
            if self.player1_time <= 0:
                self.player1_time = 0
                self.status_text= "Player O wins!"
                self.game_over = True
        elif self.turn == 2:
            self.player2_time -= elapsed_time
            if self.player2_time <= 0:
                self.player2_time = 0
                self.status_text = "Player X wins!"
                self.game_over = True

    def handle_click(self, pos):
        """Handle mouse click events during the game"""
        if self.turn == 2 and self.ai_enabled:
            return
        
        x, y = pos[0] // self.cell_size, pos[1] // self.cell_size
        if 0 <= x < self.size and 0 <= y < self.size and self.board[x, y] == 0:
            self.place_piece(x, y)

    # def handle_menu_click(self, pos):
    #     """Handle clicks on the game over menu"""
    #     if self.play_again_rect.collidepoint(pos):
    #         self.reset_game()
    #         self.game_state='playing'
    #         return True  , 'continue' # Continue the game
    #     elif self.quit_rect.collidepoint(pos):
    #         self.game_state = "main_menu"  # Return to main menu instead of quitting
    #         self.main_menu.needs_redraw = True  # Force redraw of main menu
    #         return True , 'menu'
    #     return True  , 'continue' # Continue showing the menu
    def handle_menu_click(self, pos):
        """Handle clicks on the game over menu"""
        if self.play_again_rect.collidepoint(pos):
            self.reset_game()
            self.game_state = "playing"
            return True, "continue"
        elif self.quit_rect.collidepoint(pos):
            self.game_state = "main_menu"
            return False, "menu"
        return True, "continue"

    
    def place_piece(self, x, y):
        """Place a piece, play sound, check for win, and highlight the cell"""
        if self.game_over:
            return
        
        self.board[x, y] = self.turn
        self.last_placed.append((x, y))
        self.play_place_sound()
        self.move_count += 1
        self.draw_board()
        
        if self.check_win(self.turn):
            self.status_text = f"Player {self.players[self.turn]} wins!"
            self.game_over = True
            self.draw_board()
            return
        
        if self.move_count >= self.moves_per_turn:
            self.turn = 3 - self.turn
            self.move_count = 0
            self.moves_per_turn = 2
            if self.turn == 2 and self.ai_enabled:
                self.status_text = "AI đang suy nghĩ..."
                self.draw_board()
                asyncio.run_coroutine_threadsafe(self.ai_move(), self.loop)
        elif self.turn == 2 and self.ai_enabled:
            self.status_text = "AI đang suy nghĩ..."
            self.draw_board()
            asyncio.run_coroutine_threadsafe(self.ai_move(), self.loop)

    async def ai_move(self):
        """Handle AI move with realistic thinking delay"""
        self.status_text = "AI đang suy nghĩ..."
        self.draw_board()  # Update display immediately
        think_time = random.uniform(0.5, 2.0)  # Random thinking time from 0.5 to 2 seconds
        await asyncio.sleep(think_time)
        
        candidate_moves = self.get_candidate_moves()
        
        # 1. Check for immediate AI win
        for i, j in candidate_moves:
            self.board[i, j] = 2
            if self.check_win(2):
                self.board[i, j] = 0
                self.place_piece(i, j)
                self.status_text = "Player O wins!"
                self.game_over = True  # Explicitly set game_over
                self.draw_board()  # Ensure board is updated
                return
            self.board[i, j] = 0
        
        # 2. Check for blocking human win
        for i, j in candidate_moves:
            self.board[i, j] = 1
            if self.check_win(1):
                self.board[i, j] = 2
                self.place_piece(i, j)
                self.status_text = "AI blocks human win!"
                self.draw_board()  # Ensure board is updated
                return
            self.board[i, j] = 0
        
        # 3. Block human's open five
        for i, j in candidate_moves:
            self.board[i, j] = 1
            if self.has_open_five(1):
                self.board[i, j] = 2
                self.place_piece(i, j)
                self.status_text = "AI blocks open five!"
                self.draw_board()  # Ensure board is updated
                return
            self.board[i, j] = 0
        
        # 4. Use Minimax to select optimal move
        best_score = float('-inf')
        best_move = None
        for move in candidate_moves[:10]:  # Limit to 10 moves for speed
            i, j = move
            self.board[i, j] = 2
            score = self.minimax(2, False, float('-inf'), float('inf'))
            self.board[i, j] = 0
            if score > best_score:
                best_score = score
                best_move = move
        
        if best_move:
            self.place_piece(best_move[0], best_move[1])
        else:
            # Fallback to a random move
            i, j = random.choice(candidate_moves)
            self.place_piece(i, j)
        self.status_text = ""
        self.draw_board()  # Ensure board is updated after move

    def get_candidate_moves(self):
        """Find potential moves near placed pieces"""
        search_range = 2
        candidate_moves = set()
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i, j] == 0:
                    for dx in range(-search_range, search_range + 1):
                        for dy in range(-search_range, search_range + 1):
                            ni, nj = i + dx, j + dy
                            if 0 <= ni < self.size and 0 <= nj < self.size and self.board[ni, nj] != 0:
                                candidate_moves.add((i, j))
                                break
        return list(candidate_moves) if candidate_moves else [(self.size//2, self.size//2)]

    def minimax(self, depth, is_maximizing, alpha, beta):
        """Minimax algorithm with alpha-beta pruning"""
        if self.check_win(2):
            return 10000
        if self.check_win(1):
            return -10000
        if depth == 0:
            return self.evaluate_board()
        
        candidate_moves = self.get_candidate_moves()[:10]
        
        if is_maximizing:
            max_eval = float('-inf')
            for i, j in candidate_moves:
                self.board[i, j] = 2
                eval = self.minimax(depth-1, False, alpha, beta)
                self.board[i, j] = 0
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for i, j in candidate_moves:
                self.board[i, j] = 1
                eval = self.minimax(depth-1, True, alpha, beta)
                self.board[i, j] = 0
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval


    def evaluate_board(self):
        """Evaluate the board state"""
        score = 0
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x, y] == 0:
                    continue
                for dx, dy in directions:
                    count_2, count_1 = 0, 0
                    open_ends_2, open_ends_1 = 0, 0                
                    for step in range(6):
                        nx, ny = x + step * dx, y + step * dy
                        if 0 <= nx < self.size and 0 <= ny < self.size:
                            if self.board[nx, ny] == 2:
                                count_2 += 1
                            elif self.board[nx, ny] == 1:
                                count_1 += 1
                            else:
                                break
                        else:
                            break               
                    if count_2 > 0:
                        before_x, before_y = x - dx, y - dy
                        after_x, after_y = x + count_2 * dx, y + count_2 * dy
                        if (0 <= before_x < self.size and 0 <= before_y < self.size and self.board[before_x, before_y] == 0):
                            open_ends_2 += 1
                        if (0 <= after_x < self.size and 0 <= after_y < self.size and self.board[after_x, after_y] == 0):
                            open_ends_2 += 1
                    if count_1 > 0:
                        before_x, before_y = x - dx, y - dy
                        after_x, after_y = x + count_1 * dx, y + count_1 * dy
                        if (0 <= before_x < self.size and 0 <= before_y < self.size and self.board[before_x, before_y] == 0):
                            open_ends_1 += 1
                        if (0 <= after_x < self.size and 0 <= after_y < self.size and self.board[after_x, after_y] == 0):
                            open_ends_1 += 1                  
                    if count_2 >= 5:
                        score += 100000
                    elif count_2 == 4 and open_ends_2 > 0:
                        score += 10000
                    elif count_2 == 3 and open_ends_2 > 1:
                        score += 500
                    elif count_2 == 2 and open_ends_2 > 1:
                        score += 3000
                    
                    if count_1 >= 5:
                        score -= 70000
                    elif count_1 == 4 and open_ends_1 > 0:
                        score -= 15000
                    elif count_1 == 3 and open_ends_1 > 1:
                        score -= 5000
                    elif count_1 == 2 and open_ends_1 > 1:
                        score -= 500
        return score

    def has_open_five(self, player):
        """Check for open five sequence"""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x, y] != player:
                    continue
                for dx, dy in directions:
                    count = 1
                    for step in range(1, 5):
                        nx, ny = x + step * dx, y + step * dy
                        if 0 <= nx < self.size and 0 <= ny < self.size and self.board[nx, ny] == player:
                            count += 1
                        else:
                            break
                    if count == 5:
                        before_x, before_y = x - dx, y - dy
                        after_x, after_y = x + 5 * dx, y + 5 * dy
                        if (0 <= before_x < self.size and 0 <= before_y < self.size and self.board[before_x, before_y] == 0) or \
                           (0 <= after_x < self.size and 0 <= after_y < self.size and self.board[after_x, after_y] == 0):
                            return True
        return False

    def check_win(self, player):
        """Check for win (6 or more in a row)"""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x, y] != player:
                    continue
                for dx, dy in directions:
                    count = 1
                    for step in range(1, 6):
                        nx, ny = x + step * dx, y + step * dy
                        if 0 <= nx < self.size and 0 <= ny < self.size and self.board[nx, ny] == player:
                            count += 1
                        else:
                            break
                    if count >= 6:
                        return True
        return False

    def setup(self):
        """Initialize the game"""
        self.draw_board()

    def update_loop(self):
        """Handle game events and update timers"""
        if self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False, "quit"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    continue_game, action = self.handle_menu_click(event.pos)
                    return continue_game, action
            self.draw_board()
            return True, "continue"
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False, "quit"
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)
            
            self.update_timers()
            self.draw_board()
            return True, "continue"

    def run(self):
        """Main game loop, returns status when exiting"""
        if not self.sound_enabled:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            print(f"Game started, sound_enabled={self.sound_enabled}, music stopped, music_busy={pygame.mixer.music.get_busy()}")
        else:
            print(f"Game started, sound_enabled={self.sound_enabled}, music continues, music_busy={pygame.mixer.music.get_busy()}")
        self.setup()
        running = True
        while running:
            continue_game, action = self.update_loop()
            self.loop.run_until_complete(asyncio.sleep(0))
            if action == "menu":
                return "menu"
            elif action == "quit":
                return "quit"
            if continue_game and not self.game_over:
                self.clock.tick(60)
            else:
                self.clock.tick(30)
        return "quit"


# if __name__ == "__main__":
#     try:
#         game = Connect6(size=19, ai_enabled=True)
#         game.run()
#     finally:
#         pygame.quit()