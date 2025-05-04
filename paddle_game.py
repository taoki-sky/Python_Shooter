import pygame
import random
import sys
import math

# Initialize the game
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout + Shooting")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Paddle class
class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = 100
        self.height = 20
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 8
        self.cooldown = 0
        
    def update(self):
        # Movement based on key input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
            
        # Decrease cooldown timer
        if self.cooldown > 0:
            self.cooldown -= 1

    def shoot(self, bullet_width):
        if self.cooldown == 0:
            # bullet_width is the number of bullets fired at once
            if bullet_width <= 1:
                # Normal single bullet
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
            else:
                # Multiple bullets in a fan pattern
                angle_spread = 10  # Spread angle (degrees)
                for i in range(bullet_width):
                    if bullet_width == 2:
                        # If 2 bullets, one on each side
                        angle = -angle_spread/2 if i == 0 else angle_spread/2
                    else:
                        # 3+ bullets, evenly distributed
                        angle = -angle_spread + i * (angle_spread * 2) / (bullet_width - 1)
                    
                    # Calculate velocity based on angle
                    speed_x = math.sin(math.radians(angle)) * 3
                    speed_y = -10  # Base upward speed
                    
                    bullet = Bullet(self.rect.centerx, self.rect.top, speed_x, speed_y)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
            
            self.cooldown = 10  # Cooldown time (lower = faster firing rate)

# Ball class
class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = 10
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (self.size//2, self.size//2), self.size//2)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.centery = HEIGHT // 2
        self.speed_x = random.choice([-4, -3, 3, 4])
        self.speed_y = -4
        self.active = True
        
    def update(self):
        if not self.active:
            return
            
        # Ball movement
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # Wall collision detection
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.speed_x = -self.speed_x
        
        # Ceiling collision detection
        if self.rect.top <= 0:
            self.speed_y = -self.speed_y
            
        # Ball falls off the bottom
        if self.rect.bottom >= HEIGHT:
            self.active = False
            
    def reset(self):
        self.rect.centerx = WIDTH // 2
        self.rect.centery = HEIGHT // 2
        self.speed_x = random.choice([-4, -3, 3, 4])
        self.speed_y = -4
        self.active = True

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_x=0, speed_y=-10):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        
        # Rotate bullet image based on direction (if not vertical)
        if speed_x != 0:
            angle = math.degrees(math.atan2(-speed_y, speed_x))
            self.image = pygame.transform.rotate(self.image, angle + 90)  # +90 to adjust image orientation
        
    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        # Remove when off-screen
        if self.rect.bottom < 0 or self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

# Block class
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, color, strength=1):
        super().__init__()
        self.width = 80
        self.height = 30
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.strength = strength  # Block durability
        self.original_color = color
        
    def hit(self):
        self.strength -= 1
        # Adjust color based on remaining durability
        if self.strength > 0:
            # Fade the color
            r, g, b = self.original_color
            fade_factor = self.strength / 2  # If original durability is 2, divide by 2
            new_color = (int(r * fade_factor), int(g * fade_factor), int(b * fade_factor))
            self.image.fill(new_color)
            return False  # Not destroyed yet
        return True  # Destroyed

# Power-up item class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.type = type  # 0: Extra damage, 1: Multi-shot, 2: Extra life
        self.image = pygame.Surface((20, 20))
        
        # Color based on type
        if self.type == 0:  # Extra damage
            self.image.fill(YELLOW)
        elif self.type == 1:  # Multi-shot
            self.image.fill(GREEN)
        elif self.type == 2:  # Extra life
            self.image.fill(RED)
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 3
        
    def update(self):
        self.rect.y += self.speed
        # Remove when off-screen
        if self.rect.top > HEIGHT:
            self.kill()

# Sprite group setup
all_sprites = pygame.sprite.Group()
blocks = pygame.sprite.Group()
paddle_group = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

# Create paddle
paddle = Paddle()
all_sprites.add(paddle)
paddle_group.add(paddle)

# Create ball
ball = Ball()
all_sprites.add(ball)

# Create blocks
block_colors = [RED, ORANGE, YELLOW, GREEN, PURPLE]
for row in range(5):
    for col in range(9):
        # Upper rows have higher durability
        strength = min(2, 5 - row)  # Top row has durability 2, others 1
        block = Block(col * 85 + 20, row * 35 + 50, block_colors[row], strength)
        all_sprites.add(block)
        blocks.add(block)

# Game variable initialization
score = 0
lives = 3
level = 1
bullet_power = 1  # Bullet power
bullet_width = 1  # Number of bullets (increases with multi-shot)
font = pygame.font.SysFont(None, 36)

# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    # Frame rate setting
    clock.tick(60)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # Press space to launch ball when inactive
            if event.key == pygame.K_SPACE and not ball.active and lives > 0:
                ball.reset()

    # Shooting with key input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_z]:  # Z key to shoot
        paddle.shoot(bullet_width)
    
    # Update sprites
    all_sprites.update()
    
    # Ball and paddle collision
    if ball.active:
        hits = pygame.sprite.spritecollide(ball, paddle_group, False)
        for hit in hits:
            ball.speed_y = -abs(ball.speed_y)  # Always bounce upward
            # Angle depends on where it hits the paddle
            ball.speed_x = (ball.rect.centerx - paddle.rect.centerx) / (paddle.width / 2) * 5
    
    # Ball and block collision
    if ball.active:
        hits = pygame.sprite.spritecollide(ball, blocks, False)
        for block in hits:
            if block.hit():  # Apply damage and check if destroyed
                block.kill()  # Remove destroyed block
                # Chance to drop power-up
                if random.random() < 0.2:  # 20% chance
                    powerup = PowerUp(block.rect.centerx, block.rect.centery, random.randint(0, 2))
                    all_sprites.add(powerup)
                    powerups.add(powerup)
            ball.speed_y = -ball.speed_y
            score += 10
    
    # Bullet and block collision
    hits = pygame.sprite.groupcollide(bullets, blocks, True, False)
    for bullet, hit_blocks in hits.items():
        for block in hit_blocks:
            if block.hit():  # Apply damage and check if destroyed
                block.kill()  # Remove destroyed block
                # Chance to drop power-up
                if random.random() < 0.2:  # 20% chance
                    powerup = PowerUp(block.rect.centerx, block.rect.centery, random.randint(0, 2))
                    all_sprites.add(powerup)
                    powerups.add(powerup)
            score += 5
    
    # Paddle and power-up collision
    hits = pygame.sprite.spritecollide(paddle, powerups, True)
    for powerup in hits:
        if powerup.type == 0:  # Extra damage
            bullet_power += 1
        elif powerup.type == 1:  # Multi-shot
            if bullet_width < 5:  # Maximum 5 bullets
                bullet_width += 1
        elif powerup.type == 2:  # Extra life
            lives += 1
    
    # Ball falls off
    if not ball.active:
        lives -= 1
        if lives > 0:
            ball.reset()
        else:
            # Game over display
            game_over_text = font.render("GAME OVER - Press R to Restart", True, WHITE)
            screen.blit(game_over_text, (WIDTH//2 - 180, HEIGHT//2))
            pygame.display.flip()
            
            # Press R to restart
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            # Reset game
                            lives = 3
                            score = 0
                            level = 1
                            bullet_power = 1
                            bullet_width = 1
                            ball.reset()
                            
                            # Recreate blocks
                            blocks.empty()
                            for sprite in all_sprites:
                                if isinstance(sprite, Block) or isinstance(sprite, PowerUp):
                                    all_sprites.remove(sprite)
                            powerups.empty()
                            
                            for row in range(5):
                                for col in range(9):
                                    strength = min(2, 5 - row)
                                    block = Block(col * 85 + 20, row * 35 + 50, block_colors[row], strength)
                                    all_sprites.add(block)
                                    blocks.add(block)
                            
                            waiting = False
    
    # Level up when all blocks are destroyed
    if len(blocks) == 0:
        level += 1
        level_up_text = font.render(f"LEVEL {level} COMPLETE!", True, WHITE)
        screen.blit(level_up_text, (WIDTH//2 - 120, HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(2000)
        
        # Create next level blocks (higher durability with level)
        for row in range(5):
            for col in range(9):
                # Increase durability with level
                strength = min(level + 1, 5)  # Maximum durability is 5
                block = Block(col * 85 + 20, row * 35 + 50, block_colors[row], strength)
                all_sprites.add(block)
                blocks.add(block)
        
        # Reset ball and increase speed
        ball.reset()
        ball.speed_x *= 1.1
        ball.speed_y *= 1.1
    
    # Drawing
    screen.fill(BLACK)
    all_sprites.draw(screen)
    
    # Display score and other info
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    power_text = font.render(f"Power: {bullet_power}", True, WHITE)
    width_text = font.render(f"Bullets: {bullet_width}/5", True, WHITE)
    
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (WIDTH - 120, 10))
    screen.blit(level_text, (WIDTH - 120, 40))
    screen.blit(power_text, (10, 40))
    screen.blit(width_text, (10, 70))
    
    # Display controls
    controls_text = font.render("Arrow Keys: Move  Z: Shoot  Space: Launch Ball", True, WHITE)
    screen.blit(controls_text, (WIDTH//2 - 250, HEIGHT - 30))
    
    # Update display
    pygame.display.flip()

# Quit game
pygame.quit()
sys.exit() 