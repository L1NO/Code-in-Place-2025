import tkinter as tk
import random
from collections import deque

MIN_SIZE = 5
MAX_SIZE = 9
CELL_SIZE = 60
BARRIER_COUNT_RATIO = 0.18  # About 18% barriers

class MazeGame:
    def __init__(self, root):
        self.root = root
        # Make sure guide_label always on the top
        self.guide_label = tk.Label(
            root,
            text="How to play：\nUse ↑ ↓ ← → to move, let 😃 to 🏁！\nBlack blocks are barriers.",
            font=("Arial", 10, "bold"),
            fg="blue"
        )
        self.guide_label.pack(pady=5, side="top", anchor="n")
        self.reset_game()
        self.move_steps = 0  # Record for move steps
        self.root.bind("<Key>", self.on_key)
        self.draw_board()

    def reset_game(self):
        # Random map size
        self.size = random.randint(MIN_SIZE, MAX_SIZE)
        self.player_pos = [0, 0]
        self.goal_pos = [self.size-1, self.size-1]
        self.move_steps = 0  # Reset move steps counter
        # Random generate barriers
        while True:
            total_cells = self.size * self.size
            barrier_count = int(total_cells * BARRIER_COUNT_RATIO)
            self.barriers = set()
            while len(self.barriers) < barrier_count:
                bx = random.randint(0, self.size-1)
                by = random.randint(0, self.size-1)
                # Make sure the goal always clean
                if [bx, by] != self.player_pos and [bx, by] != self.goal_pos:
                    self.barriers.add((bx, by))
            if self.is_reachable():
                break
        # Regenerate canvas
        if hasattr(self, "canvas"):
            self.canvas.destroy()
        self.canvas = tk.Canvas(self.root, width=self.size*CELL_SIZE, height=self.size*CELL_SIZE, bg="white")
        self.canvas.pack()

    def is_reachable(self):
        """Check player can reach the flag（BFS）"""
        queue = deque()
        visited = set()
        queue.append(tuple(self.player_pos))
        visited.add(tuple(self.player_pos))
        directions = [(-1,0),(1,0),(0,-1),(0,1)]
        while queue:
            x, y = queue.popleft()
            if [x, y] == self.goal_pos:
                return True
            for dx, dy in directions:
                nx, ny = x+dx, y+dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    if (nx, ny) not in self.barriers and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
        return False

    def draw_board(self):
        self.canvas.delete("all")
        for i in range(self.size):
            for j in range(self.size):
                x1, y1 = j*CELL_SIZE, i*CELL_SIZE
                x2, y2 = x1+CELL_SIZE, y1+CELL_SIZE
                if (i, j) in self.barriers:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="black")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="gray", width=2)
                if [i, j] == self.goal_pos:
                    self.canvas.create_text(x1+CELL_SIZE//2, y1+CELL_SIZE//2, text="🏁", font=("Arial", 32))
        # Draw the player
        px, py = self.player_pos
        self.canvas.create_text(py*CELL_SIZE+CELL_SIZE//2, px*CELL_SIZE+CELL_SIZE//2, text="😃", font=("Arial", 32))

    def on_key(self, event):
        x, y = self.player_pos
        moved = False
        if event.keysym == "Up" and x > 0 and (x-1, y) not in self.barriers:
            x -= 1
            moved = True
        elif event.keysym == "Down" and x < self.size-1 and (x+1, y) not in self.barriers:
            x += 1
            moved = True
        elif event.keysym == "Left" and y > 0 and (x, y-1) not in self.barriers:
            y -= 1
            moved = True
        elif event.keysym == "Right" and y < self.size-1 and (x, y+1) not in self.barriers:
            y += 1
            moved = True
        if moved:
            self.move_steps += 1  # move step counter+1
        self.player_pos = [x, y]
        self.draw_board()
        if self.player_pos == self.goal_pos:
            # Get y-coordinate and make sure the overlay will not cover the guide space
            canvas_x = self.canvas.winfo_rootx() - self.root.winfo_rootx()
            canvas_y = self.canvas.winfo_rooty() - self.root.winfo_rooty()
            # Draw the overlay background for result
            overlay = self.canvas.create_rectangle(
                0, 0,
                self.size * CELL_SIZE, self.size * CELL_SIZE,
                fill="#000000", stipple="gray50", outline="", width=0
            )
            self.canvas.create_text(
                self.size*CELL_SIZE//2, self.size*CELL_SIZE//2-10,
                text="🎉 GOAL！", font=("Arial", 32, "bold"), fill="white"
            )
            self.canvas.create_text(
                self.size*CELL_SIZE//2, self.size*CELL_SIZE//2+25,
                text=f"Steps: {self.move_steps}", font=("Arial", 24, "bold"), fill="white"
            )
            # When game over, reset new game auto.
            self.root.after(1500, self.new_game)

    def new_game(self):
        self.canvas.destroy()
        self.reset_game()
        self.draw_board()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Easy Maze Game")
    root.resizable(False, False)
    game = MazeGame(root)
    root.mainloop()
