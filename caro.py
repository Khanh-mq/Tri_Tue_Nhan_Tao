import numpy as np
import tkinter as tk
from tkinter import messagebox
import threading
import random

class Connect6:
    def __init__(self, size=19, ai_enabled=True):
        self.size = size
        self.board = np.zeros((size, size), dtype=int)  # Bảng trò chơi
        self.players = {1: "X", 2: "O"}  # Người chơi: 1 là Đen (người), 2 là Trắng (AI)
        self.turn = 1  # Lượt chơi ban đầu là người chơi 1
        self.move_count = 0  # Số nước đã đi trong lượt
        self.moves_per_turn = 1  # Lượt đầu tiên chỉ đặt 1 quân
        self.ai_enabled = ai_enabled
        
        # Giao diện đồ họa
        self.root = tk.Tk()
        self.root.title("Connect6")
        self.canvas = tk.Canvas(self.root, width=size*30, height=size*30, bg="white")
        self.canvas.pack()
        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack()
        self.canvas.bind("<Button-1>", self.click_event)
        self.draw_board()
        self.root.mainloop()
    
    def draw_board(self):
        """Vẽ bảng trò chơi"""
        self.canvas.delete("all")
        for i in range(self.size):
            for j in range(self.size):
                x0, y0 = i * 30, j * 30
                x1, y1 = x0 + 30, y0 + 30
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="black")
                if self.board[i, j] == 1:
                    self.canvas.create_oval(x0+5, y0+5, x1-5, y1-5, fill="black")
                elif self.board[i, j] == 2:
                    self.canvas.create_oval(x0+5, y0+5, x1-5, y1-5, fill="white")
    
    def click_event(self, event):
        """Xử lý sự kiện nhấp chuột của người chơi"""
        if self.turn == 2 and self.ai_enabled:
            return
        
        x, y = event.x // 30, event.y // 30
        if 0 <= x < self.size and 0 <= y < self.size and self.board[x, y] == 0:
            self.place_piece(x, y)
    
    def place_piece(self, x, y):
        """Đặt quân cờ và kiểm tra thắng"""
        self.board[x, y] = self.turn
        self.move_count += 1
        self.draw_board()
        
        if self.check_win(self.turn):
            messagebox.showinfo("Game Over", f"Người chơi {self.players[self.turn]} thắng!")
            self.root.quit()
            return
        
        if self.move_count >= self.moves_per_turn:
            self.turn = 3 - self.turn  # Chuyển lượt
            self.move_count = 0
            self.moves_per_turn = 2  # Từ lượt thứ 2, mỗi bên đặt 2 quân
            if self.turn == 2 and self.ai_enabled:
                self.root.after(500, self.ai_move)
        elif self.turn == 2 and self.ai_enabled:
            self.root.after(500, self.ai_move)
    
    def ai_move(self):
        """Xử lý nước đi của AI"""
        def run_ai():
            self.status_label.config(text="AI đang suy nghĩ...")
            candidate_moves = self.get_candidate_moves()
            
            # 1. Kiểm tra thắng ngay cho AI
            for i, j in candidate_moves:
                self.board[i, j] = 2
                if self.check_win(2):
                    self.root.after(0, lambda x=i, y=j: self.place_piece(x, y))
                    self.status_label.config(text="")
                    return
                self.board[i, j] = 0
            
            # 2. Kiểm tra chặn khẩn cấp (người chơi sắp thắng)
            for i, j in candidate_moves:
                self.board[i, j] = 1
                if self.check_win(1):
                    self.board[i, j] = 2
                    self.root.after(0, lambda x=i, y=j: self.place_piece(x, y))
                    self.status_label.config(text="")
                    return
                self.board[i, j] = 0
            
            # 3. Chặn chuỗi 5 mở của người chơi
            for i, j in candidate_moves:
                self.board[i, j] = 1
                if self.has_open_five(1):
                    self.board[i, j] = 2
                    self.root.after(0, lambda x=i, y=j: self.place_piece(x, y))
                    self.status_label.config(text="")
                    return
                self.board[i, j] = 0
            
            # 4. Dùng Minimax để chọn nước đi tối ưu
            best_score = float('-inf')
            best_move = None
            for move in candidate_moves[:10]:  # Giới hạn 10 nước để tăng tốc độ
                i, j = move
                self.board[i, j] = 2
                score = self.minimax(2, False, float('-inf'), float('inf'))
                self.board[i, j] = 0
                if score > best_score:
                    best_score = score
                    best_move = move
            
            if best_move:
                self.root.after(0, lambda x=best_move[0], y=best_move[1]: self.place_piece(x, y))
            self.status_label.config(text="")
        
        thread = threading.Thread(target=run_ai)
        thread.start()
    
    def get_candidate_moves(self):
        """Tìm các nước đi tiềm năng gần các quân cờ đã đặt"""
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
        """Thuật toán Minimax với alpha-beta pruning"""
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
        """Hàm đánh giá tình hình bảng"""
        score = 0
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x, y] == 0:
                    continue
                for dx, dy in directions:
                    count_2, count_1 = 0, 0
                    open_ends_2, open_ends_1 = 0, 0
                    
                    # Đếm quân liên tiếp
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
                    
                    # Kiểm tra đầu mở
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
                    
                    # Đánh giá điểm số
                    if count_2 >= 5:
                        score += 10000  # AI sắp thắng
                    elif count_2 == 4 and open_ends_2 > 0:
                        score += 1000   # Chuỗi 4 mở
                    elif count_2 == 3 and open_ends_2 > 1:
                        score += 200    # Chuỗi 3 mở 2 đầu
                    elif count_2 == 2 and open_ends_2 > 1:
                        score += 50     # Chuỗi 2 mở
                    
                    if count_1 >= 5:
                        score -= 5000   # Người chơi sắp thắng
                    elif count_1 == 4 and open_ends_1 > 0:
                        score -= 1000   # Chặn chuỗi 4 mở của người chơi
                    elif count_1 == 3 and open_ends_1 > 1:
                        score -= 200    # Chặn chuỗi 3 mở 2 đầu
                    elif count_1 == 2 and open_ends_1 > 1:
                        score -= 50     # Chặn chuỗi 2 mở
        
        return score
    
    def has_open_five(self, player):
        """Kiểm tra chuỗi 5 mở"""
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
        """Kiểm tra chiến thắng (chuỗi 6 trở lên)"""
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

if __name__ == "__main__":
    Connect6(size=19, ai_enabled=True)