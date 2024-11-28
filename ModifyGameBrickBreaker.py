import tkinter as tk
import random

class GameObject:
    def init(self, canvas, x, y, width, height, color):
        self.canvas = canvas
        self.item = canvas.create_rectangle(x, y, x + width, y + height, fill=color)
        self.width = width
        self.height = height
        
    def move(self, dx, dy):
        self.canvas.move(self.item, dx, dy)
        
    def position(self):
        return self.canvas.coords(self.item)
        
    def delete(self):
        self.canvas.delete(self.item)

class Ball(GameObject):
    def init(self, canvas, x, y, speed):
        super().init(canvas, x, y, 10, 10, 'red')
        self.speed = speed
        self.dx = speed
        self.dy = -speed
        
    def update(self):
        self.move(self.dx, self.dy)
        pos = self.position()
        if pos[0] <= 0 or pos[2] >= self.canvas.winfo_width():
            self.dx = -self.dx
        if pos[1] <= 0:
            self.dy = -self.dy

class Paddle(GameObject):
    def init(self, canvas, width):
        self.canvas_width = canvas.winfo_width()
        super().init(canvas, self.canvas_width/2 - width/2, 350, width, 10, 'blue')
        self.speed = 6
        self.canvas = canvas
        self.movement = 0  # -1 untuk kiri, 1 untuk kanan, 0 untuk diam

    def start_move(self, direction):
        self.movement = direction
        
    def stop_move(self):
        self.movement = 0
        
    def update(self):
        if self.movement != 0:
            new_pos = self.position()
            # Cek batas kiri
            if self.movement == -1 and new_pos[0] > 0:
                self.move(-self.speed, 0)
            # Cek batas kanan
            elif self.movement == 1 and new_pos[2] < self.canvas.winfo_width():
                self.move(self.speed, 0)

class Brick(GameObject):
    def init(self, canvas, x, y, hits_to_break, color):
        super().init(canvas, x, y, 50, 20, color)
        self.hits_to_break = hits_to_break

class Game(tk.Frame):
    def init(self, master, difficulty="medium"):
        super().init(master)
        self.master = master
        self.difficulty = difficulty
        self.score = 0
        self.lives = 3
        self.paused = False
        
        if difficulty == "easy":
            self.ball_speed = 3
            self.paddle_width = 100
        elif difficulty == "medium":
            self.ball_speed = 5
            self.paddle_width = 80
        else:  # hard
            self.ball_speed = 7
            self.paddle_width = 60
            
        self.setup_game()
        
    def setup_game(self):
        self.canvas = tk.Canvas(self, width=600, height=400, bg='black')
        self.canvas.pack(pady=10)
        self.pack()
        
        self.score_display = self.canvas.create_text(50, 20, text=f"Score: {self.score}", fill='white')
        self.lives_display = self.canvas.create_text(50, 40, text=f"Lives: {self.lives}", fill='white')
        
        self.paddle = Paddle(self.canvas, self.paddle_width)
        self.ball = Ball(self.canvas, 300, 340, self.ball_speed)
        self.create_bricks()
        
        # Membuat tombol kontrol
        self.create_controls()
        
        # Binding keyboard
        self.bind_keys()
        
        # Mulai game loop
        self.game_loop()
        
    def create_controls(self):
        control_frame = tk.Frame(self)
        control_frame.pack(side=tk.BOTTOM, pady=5)
        
        self.left_button = tk.Button(control_frame, text="← Left", width=10)
        self.left_button.pack(side=tk.LEFT, padx=5)
        self.left_button.bind('<Button-1>', lambda e: self.paddle.start_move(-1))
        self.left_button.bind('<ButtonRelease-1>', lambda e: self.paddle.stop_move())
        
        self.pause_button = tk.Button(control_frame, text="Pause", width=10, 
                                    command=self.toggle_pause)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.right_button = tk.Button(control_frame, text="Right →", width=10)
        self.right_button.pack(side=tk.LEFT, padx=5)
        self.right_button.bind('<Button-1>', lambda e: self.paddle.start_move(1))
        self.right_button.bind('<ButtonRelease-1>', lambda e: self.paddle.stop_move())

    def bind_keys(self):
        # Binding untuk keyboard
        self.master.bind('<Left>', lambda e: self.paddle.start_move(-1))
        self.master.bind('<KeyRelease-Left>', lambda e: self.paddle.stop_move())
        self.master.bind('<Right>', lambda e: self.paddle.start_move(1))
        self.master.bind('<KeyRelease-Right>', lambda e: self.paddle.stop_move())
        self.master.bind('<space>', self.toggle_pause)
        
    def create_bricks(self):
        self.bricks = []
        colors = {1: 'red', 2: 'orange', 3: 'yellow'}
        
        for row in range(5):
            for col in range(10):
                x = col * 60 + 10
                y = row * 25 + 50
                
                if self.difficulty == "easy":
                    hits = 1
                elif self.difficulty == "medium":
                    hits = 2 if row < 2 else 1
                else:
                    hits = 3 if row < 2 else (2 if row < 4 else 1)
                    
                brick = Brick(self.canvas, x, y, hits, colors[hits])
                self.bricks.append(brick)
    
    def toggle_pause(self, event=None):
        self.paused = not self.paused
        self.pause_button.config(text="Resume" if self.paused else "Pause")
        if not self.paused:
            self.game_loop()
    
    def check_collisions(self):
        # Ball and paddle collision
        paddle_pos = self.paddle.position()
        ball_pos = self.ball.position()
        
        if (ball_pos[2] >= paddle_pos[0] and ball_pos[0] <= paddle_pos[2] and
            ball_pos[3] >= paddle_pos[1] and ball_pos[1] <= paddle_pos[3]):
            self.ball.dy = -abs(self.ball.dy)
            
        # Ball and brick collision
        for brick in self.bricks[:]:
            brick_pos = brick.position()
            if (ball_pos[2] >= brick_pos[0] and ball_pos[0] <= brick_pos[2] and
                ball_pos[3] >= brick_pos[1] and ball_pos[1] <= brick_pos[3]):
                brick.hits_to_break -= 1
                if brick.hits_to_break <= 0:
                    brick.delete()
                    self.bricks.remove(brick)
                    self.score += 10
                    self.canvas.itemconfig(self.score_display, text=f"Score: {self.score}")
                self.ball.dy = -self.ball.dy
                break
    
    def game_loop(self):
        if not self.paused:
            # Update paddle dan ball
            self.paddle.update()
            self.ball.update()
            
            self.check_collisions()
            
            # Check ball out
            if self.ball.position()[3] >= self.canvas.winfo_height():
                self.lives -= 1
                self.canvas.itemconfig(self.lives_display, text=f"Lives: {self.lives}")
                if self.lives <= 0:
                    self.game_over()
                else:
                    self.ball = Ball(self.canvas, 300, 340, self.ball_speed)
            
            # Check victory
            if not self.bricks:
                self.victory()
                
            self.after(16, self.game_loop)
    
    def game_over(self):
        self.paused = True
        self.canvas.create_text(300, 200, text=f"Game Over! Score: {self.score}", 
                              fill='white', font=('Arial', 20))
        self.create_restart_button()
    
    def victory(self):
        self.paused = True
        self.canvas.create_text(300, 200, text=f"Victory! Score: {self.score}", 
                              fill='white', font=('Arial', 20))
        self.create_restart_button()
    
    def create_restart_button(self):
        restart_button = tk.Button(self, text="Play Again", 
                                 command=self.restart_game)
        restart_button.pack(pady=10)
    
    def restart_game(self):
        self.destroy()
        game = Game(self.master, self.difficulty)

def start_game():
    root = tk.Tk()
    root.title("Brick Breaker")
    
    menu = tk.Frame(root)
    menu.pack(pady=20)
    
    tk.Label(menu, text="Select Difficulty:", font=('Arial', 16)).pack(pady=10)
    
    def start_with_difficulty(diff):
        menu.destroy()
        game = Game(root, diff)
    
    tk.Button(menu, text="Easy", command=lambda: start_with_difficulty("easy")).pack(pady=5)
    tk.Button(menu, text="Medium", command=lambda: start_with_difficulty("medium")).pack(pady=5)
    tk.Button(menu, text="Hard", command=lambda: start_with_difficulty("hard")).pack(pady=5)
    
    root.mainloop()

if _name== "_main":
    start_game()