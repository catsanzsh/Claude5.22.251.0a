import pygame
import numpy as np
import random

class PongGame:
    def __init__(self):
        # Initialize Pygame and mixer
        pygame.init()
        pygame.mixer.init()
        
        # Screen dimensions
        self.WIDTH, self.HEIGHT = 800, 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Pong (Atari Clone)")
        self.clock = pygame.time.Clock()
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        
        # Paddle dimensions and speed
        self.paddle_width, self.paddle_height = 10, 100
        self.paddle_speed = 5
        
        # Ball dimensions and speed
        self.ball_radius = 8
        self.ball_speed_x = 5 * random.choice((1, -1))
        self.ball_speed_y = 5 * random.choice((1, -1))
        
        # Initialize game objects
        self.left_paddle = pygame.Rect(20, self.HEIGHT // 2 - self.paddle_height // 2, 
                                      self.paddle_width, self.paddle_height)
        self.right_paddle = pygame.Rect(self.WIDTH - 20 - self.paddle_width, 
                                       self.HEIGHT // 2 - self.paddle_height // 2, 
                                       self.paddle_width, self.paddle_height)
        self.ball = pygame.Rect(self.WIDTH // 2 - self.ball_radius, 
                               self.HEIGHT // 2 - self.ball_radius, 
                               self.ball_radius * 2, self.ball_radius * 2)
        
        # Scores
        self.score_left = 0
        self.score_right = 0
        self.font = pygame.font.SysFont(None, 50)
        self.small_font = pygame.font.SysFont(None, 36)
        
        # Game state
        self.game_over = False
        self.winner = None
        self.winning_score = 5
        
        # Generate sounds
        self.bounce_sound = self.generate_sound(440, 0.05)
        self.score_sound = self.generate_sound(880, 0.2)
        
        self.running = True
    
    def generate_sound(self, freq, duration=0.1, volume=0.5):
        """Generate a simple sine wave sound with proper stereo formatting"""
        sample_rate = 44100
        n_samples = int(round(duration * sample_rate))
        t = np.linspace(0, duration, n_samples, False)
        wave = np.sin(2 * np.pi * freq * t)
        
        # Convert to 16-bit signed and create stereo array
        mono_audio = (wave * 32767 * volume).astype(np.int16)
        
        # Create stereo array by stacking mono channel twice (left and right)
        stereo_audio = np.column_stack((mono_audio, mono_audio))
        
        sound = pygame.sndarray.make_sound(stereo_audio)
        return sound
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r and not self.game_over:
                    self.reset_game()
                # Game over screen controls
                elif self.game_over:
                    if event.key == pygame.K_y:
                        self.reset_game()
                    elif event.key == pygame.K_n:
                        self.running = False
    
    def update_paddles(self):
        """Update paddle positions"""
        # Control left paddle with mouse
        mouse_y = pygame.mouse.get_pos()[1]
        self.left_paddle.y = mouse_y - self.paddle_height // 2
        self.left_paddle.y = max(0, min(self.HEIGHT - self.paddle_height, self.left_paddle.y))
        
        # Simple AI for right paddle
        paddle_center = self.right_paddle.centery
        ball_center = self.ball.centery
        
        if ball_center < paddle_center - 10:  # Added dead zone for smoother AI
            self.right_paddle.y -= self.paddle_speed
        elif ball_center > paddle_center + 10:
            self.right_paddle.y += self.paddle_speed
        
        # Keep right paddle on screen
        self.right_paddle.y = max(0, min(self.HEIGHT - self.paddle_height, self.right_paddle.y))
    
    def update_ball(self):
        """Update ball position and handle collisions"""
        # Move ball
        self.ball.x += self.ball_speed_x
        self.ball.y += self.ball_speed_y
        
        # Collide with top/bottom walls
        if self.ball.top <= 0 or self.ball.bottom >= self.HEIGHT:
            self.ball_speed_y *= -1
            self.bounce_sound.play()
            # Keep ball on screen
            if self.ball.top <= 0:
                self.ball.top = 0
            if self.ball.bottom >= self.HEIGHT:
                self.ball.bottom = self.HEIGHT
        
        # Collide with paddles
        if (self.ball.colliderect(self.left_paddle) and self.ball_speed_x < 0):
            self.ball_speed_x = abs(self.ball_speed_x)  # Ensure ball moves right
            self.ball.left = self.left_paddle.right  # Prevent ball from sticking
            self.bounce_sound.play()
            
        if (self.ball.colliderect(self.right_paddle) and self.ball_speed_x > 0):
            self.ball_speed_x = -abs(self.ball_speed_x)  # Ensure ball moves left
            self.ball.right = self.right_paddle.left  # Prevent ball from sticking
            self.bounce_sound.play()
    
    def check_scoring(self):
        """Check if anyone scored and reset ball"""
        if self.ball.left <= 0:
            self.score_right += 1
            self.score_sound.play()
            self.reset_ball()
            
        if self.ball.right >= self.WIDTH:
            self.score_left += 1
            self.score_sound.play()
            self.reset_ball()
            
        # Check for game over condition
        if self.score_left >= self.winning_score:
            self.game_over = True
            self.winner = "LEFT PLAYER"
        elif self.score_right >= self.winning_score:
            self.game_over = True
            self.winner = "RIGHT PLAYER"
    
    def reset_ball(self):
        """Reset ball to center with random direction"""
        self.ball.center = (self.WIDTH // 2, self.HEIGHT // 2)
        self.ball_speed_x = 5 * random.choice((1, -1))
        self.ball_speed_y = 5 * random.choice((1, -1))
    
    def reset_game(self):
        """Reset the entire game"""
        self.score_left = 0
        self.score_right = 0
        self.game_over = False
        self.winner = None
        self.reset_ball()
        self.left_paddle.y = self.HEIGHT // 2 - self.paddle_height // 2
        self.right_paddle.y = self.HEIGHT // 2 - self.paddle_height // 2
    
    def draw(self):
        """Draw all game elements"""
        self.screen.fill(self.BLACK)
        
        # Draw center line
        for y in range(0, self.HEIGHT, 20):
            pygame.draw.rect(self.screen, self.WHITE, (self.WIDTH // 2 - 1, y, 2, 10))
        
        # Draw paddles and ball
        pygame.draw.rect(self.screen, self.WHITE, self.left_paddle)
        pygame.draw.rect(self.screen, self.WHITE, self.right_paddle)
        pygame.draw.ellipse(self.screen, self.WHITE, self.ball)
        
        # Draw scores
        score_text = f"{self.score_left}    {self.score_right}"
        score_surf = self.font.render(score_text, True, self.WHITE)
        score_rect = score_surf.get_rect(center=(self.WIDTH // 2, 50))
        self.screen.blit(score_surf, score_rect)
        
        # Draw game over screen
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(self.BLACK)
            self.screen.blit(overlay, (0, 0))
            
            # Game over text
            game_over_text = self.font.render("GAME OVER", True, self.WHITE)
            game_over_rect = game_over_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 60))
            self.screen.blit(game_over_text, game_over_rect)
            
            # Winner text
            winner_text = self.small_font.render(f"{self.winner} WINS!", True, self.WHITE)
            winner_rect = winner_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 20))
            self.screen.blit(winner_text, winner_rect)
            
            # Play again prompt
            prompt_text = self.small_font.render("Play Again? Y/N", True, self.WHITE)
            prompt_rect = prompt_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 + 20))
            self.screen.blit(prompt_text, prompt_rect)
            
            # Instructions
            y_text = pygame.font.SysFont(None, 24).render("Y = Yes (Play Again)", True, self.WHITE)
            n_text = pygame.font.SysFont(None, 24).render("N = No (Quit Game)", True, self.WHITE)
            y_rect = y_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 + 60))
            n_rect = n_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 + 85))
            self.screen.blit(y_text, y_rect)
            self.screen.blit(n_text, n_rect)
        
        # Draw instructions for normal gameplay
        elif self.score_left == 0 and self.score_right == 0:
            instruction_font = pygame.font.SysFont(None, 24)
            instructions = [
                "Move mouse to control left paddle",
                "Press ESC to quit, R to reset",
                f"First to {self.winning_score} points wins!"
            ]
            for i, instruction in enumerate(instructions):
                text_surf = instruction_font.render(instruction, True, self.WHITE)
                text_rect = text_surf.get_rect(center=(self.WIDTH // 2, self.HEIGHT - 75 + i * 25))
                self.screen.blit(text_surf, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            
            # Only update game logic if not in game over state
            if not self.game_over:
                self.update_paddles()
                self.update_ball()
                self.check_scoring()
            
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()

# Run the game
if __name__ == "__main__":
    game = PongGame()
    game.run()
