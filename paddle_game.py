import pygame
import random
import sys
import math
import os

# Initialize the game
pygame.init()
pygame.mixer.init()  # Initialize sound mixer

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

# Create asset folder if it doesn't exist
if not os.path.exists('assets'):
    os.makedirs('assets/images', exist_ok=True)
    os.makedirs('assets/sounds', exist_ok=True)

# Function to load or create images
def load_or_create_image(file_path, default_surface, default_color):
    if os.path.exists(file_path):
        try:
            return pygame.image.load(file_path).convert_alpha()
        except pygame.error:
            pass
    default_surface.fill(default_color)
    return default_surface

# Load sound effects
def load_or_default_sound(file_path, volume=0.5):
    sound = None
    if os.path.exists(file_path):
        try:
            sound = pygame.mixer.Sound(file_path)
            sound.set_volume(volume)
        except pygame.error:
            print(f"Could not load sound: {file_path}")
    return sound

# Load/create game assets
paddle_img_path = 'assets/images/paddle.png'
ball_img_path = 'assets/images/ball.png'
bullet_img_path = 'assets/images/bullet.png'
block_img_paths = {
    'red': 'assets/images/block_red.png',
    'orange': 'assets/images/block_orange.png',
    'yellow': 'assets/images/block_yellow.png',
    'green': 'assets/images/block_green.png',
    'purple': 'assets/images/block_purple.png'
}
boss_img_path = 'assets/images/boss.png'
powerup_img_paths = {
    'damage': 'assets/images/powerup_damage.png',
    'multi': 'assets/images/powerup_multi.png',
    'life': 'assets/images/powerup_life.png'
}

# Sound effects
hit_sound_path = 'assets/sounds/hit.wav'
powerup_sound_path = 'assets/sounds/powerup.wav'
shoot_sound_path = 'assets/sounds/shoot.wav'
boss_appear_sound_path = 'assets/sounds/boss_appear.wav'
level_up_sound_path = 'assets/sounds/level_up.wav'
game_over_sound_path = 'assets/sounds/game_over.wav'

# Load sounds
hit_sound = load_or_default_sound(hit_sound_path)
powerup_sound = load_or_default_sound(powerup_sound_path)
shoot_sound = load_or_default_sound(shoot_sound_path)
boss_appear_sound = load_or_default_sound(boss_appear_sound_path)
level_up_sound = load_or_default_sound(level_up_sound_path)
game_over_sound = load_or_default_sound(game_over_sound_path)

# Paddle class
class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = 100
        self.height = 20
        # Create or load paddle image
        paddle_surface = pygame.Surface((self.width, self.height))
        self.image = load_or_create_image(paddle_img_path, paddle_surface, BLUE)
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
            # Play shoot sound
            if shoot_sound:
                shoot_sound.play()
            
            # bullet_width is the number of bullets fired at once
            if bullet_width <= 1:
                # Normal single bullet
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
            else:
                # Calculate angle spread based on bullet count
                # More bullets = wider spread, but capped
                max_spread = 45  # Maximum spread angle in degrees
                angle_spread = min(max_spread, 5 + bullet_width * 1.5)
                
                # Fire bullets in a fan pattern
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
            
            # Cooldown scales with bullet width - more bullets = slightly longer cooldown
            # But we cap it to maintain playability
            self.cooldown = min(20, 8 + bullet_width // 3)

# Ball class
class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = 10
        # Create or load ball image
        ball_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(ball_surface, WHITE, (self.size//2, self.size//2), self.size//2)
        self.image = load_or_create_image(ball_img_path, ball_surface, WHITE)
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
            if hit_sound:
                hit_sound.play()
        
        # Ceiling collision detection
        if self.rect.top <= 0:
            self.speed_y = -self.speed_y
            if hit_sound:
                hit_sound.play()
            
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
        # Create or load bullet image
        bullet_surface = pygame.Surface((5, 15))
        self.original_image = load_or_create_image(bullet_img_path, bullet_surface, GREEN)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        
        # Rotate bullet image based on direction (if not vertical)
        if speed_x != 0:
            angle = math.degrees(math.atan2(-speed_y, speed_x))
            self.image = pygame.transform.rotate(self.original_image, angle + 90)  # +90 to adjust image orientation
            self.rect = self.image.get_rect(center=self.rect.center)
        
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
        # Create or load block image based on color
        block_surface = pygame.Surface((self.width, self.height))
        color_name = ''
        if color == RED:
            color_name = 'red'
        elif color == ORANGE:
            color_name = 'orange'
        elif color == YELLOW:
            color_name = 'yellow'
        elif color == GREEN:
            color_name = 'green'
        elif color == PURPLE:
            color_name = 'purple'
        
        if color_name and color_name in block_img_paths:
            self.image = load_or_create_image(block_img_paths[color_name], block_surface, color)
        else:
            block_surface.fill(color)
            self.image = block_surface
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.strength = strength  # Block durability
        self.original_color = color
        self.max_strength = strength
        
    def hit(self):
        self.strength -= 1
        # Play hit sound
        if hit_sound:
            hit_sound.play()
            
        # Adjust color based on remaining durability
        if self.strength > 0:
            # If using a texture, adjust alpha to show damage
            if hasattr(self, 'surface_copy') and self.surface_copy:
                alpha = int(255 * (self.strength / self.max_strength))
                self.image.set_alpha(alpha)
            else:
                # Fade the color
                try:
                    r, g, b = self.original_color
                    fade_factor = self.strength / self.max_strength
                    new_color = (int(r * fade_factor), int(g * fade_factor), int(b * fade_factor))
                    self.image.fill(new_color)
                except ValueError:
                    # If there's an error with the color, use a default approach
                    block_surface = pygame.Surface((self.width, self.height))
                    block_surface.fill((100, 100, 100))  # Gray
                    self.image = block_surface
            return False  # Not destroyed yet
        return True  # Destroyed

# Boss class for boss levels
class Boss(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        self.level = level
        # Boss size increases with level, but is capped
        size = min(250, 100 + (level * 15))
        
        # Create or load boss image
        boss_surface = pygame.Surface((size, size))
        boss_surface.fill(RED)
        self.image = load_or_create_image(boss_img_path, boss_surface, RED)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.y = 50
        # Boss speed increases with level
        self.speed_x = 2 + (level * 0.5)
        # Boss health scales exponentially with level
        self.health = 25 * (level ** 1.5)
        self.max_health = self.health
        self.shoot_timer = 0
        # Boss shoots faster at higher levels
        self.shoot_delay = max(20, 60 - (level * 5))
        self.attack_pattern = 0  # Current attack pattern
        self.pattern_timer = 0   # Timer for changing patterns
        self.pattern_delay = 300  # Change pattern every 5 seconds (300 frames)
        self.bullet_count = min(10, 1 + level)  # Number of bullets fired at once
        
    def update(self):
        # Boss movement
        self.rect.x += self.speed_x
        
        # Change direction when hitting walls
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.speed_x = -self.speed_x
            
        # Boss shooting
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_delay:
            self.shoot()
            self.shoot_timer = 0
            
        # Change attack pattern periodically
        self.pattern_timer += 1
        if self.pattern_timer >= self.pattern_delay:
            self.attack_pattern = (self.attack_pattern + 1) % 3
            self.pattern_timer = 0
            
    def shoot(self):
        # Different attack patterns
        if self.attack_pattern == 0:
            # Single aimed shot at player
            bullet = BossBullet(self.rect.centerx, self.rect.bottom, target_x=paddle.rect.centerx)
            all_sprites.add(bullet)
            boss_bullets.add(bullet)
        elif self.attack_pattern == 1:
            # Spread shot
            for i in range(self.bullet_count):
                angle = -45 + i * (90 / (self.bullet_count - 1)) if self.bullet_count > 1 else 0
                speed_x = math.sin(math.radians(angle)) * 3
                speed_y = math.cos(math.radians(angle)) * 5
                bullet = BossBullet(self.rect.centerx, self.rect.bottom, speed_x=speed_x, speed_y=speed_y)
                all_sprites.add(bullet)
                boss_bullets.add(bullet)
        else:
            # Rapid fire
            for _ in range(3):
                x_offset = random.randint(-self.rect.width//3, self.rect.width//3)
                bullet = BossBullet(self.rect.centerx + x_offset, self.rect.bottom)
                all_sprites.add(bullet)
                boss_bullets.add(bullet)
        
    def hit(self, damage=1):
        self.health -= damage
        # Play hit sound
        if hit_sound:
            hit_sound.play()
        return self.health <= 0
        
    def draw_health_bar(self, surface):
        # Draw health bar above the boss
        bar_width = self.rect.width
        bar_height = 10
        fill_width = (self.health / self.max_health) * bar_width
        
        outline_rect = pygame.Rect(self.rect.x, self.rect.y - 15, bar_width, bar_height)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y - 15, fill_width, bar_height)
        
        pygame.draw.rect(surface, RED, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 2)

# Boss Bullet class
class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_x=0, speed_y=5, target_x=None):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        
        # If a target is provided, aim at it
        if target_x is not None:
            # Calculate angle to target
            dx = target_x - x
            dy = HEIGHT - y  # Target the bottom of the screen
            angle = math.atan2(dx, dy)
            speed = 5
            self.speed_x = math.sin(angle) * speed
            self.speed_y = math.cos(angle) * speed
        else:
            self.speed_x = speed_x
            self.speed_y = speed_y
        
    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        # Remove when off-screen
        if self.rect.top > HEIGHT or self.rect.left < 0 or self.rect.right > WIDTH:
            self.kill()

# Power-up item class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.type = type  # 0: Extra damage, 1: Multi-shot, 2: Extra life
        # Create or load powerup image based on type
        powerup_surface = pygame.Surface((20, 20))
        
        # Color based on type and path selection
        if self.type == 0:  # Extra damage
            self.image = load_or_create_image(powerup_img_paths['damage'], powerup_surface, YELLOW)
        elif self.type == 1:  # Multi-shot
            self.image = load_or_create_image(powerup_img_paths['multi'], powerup_surface, GREEN)
        elif self.type == 2:  # Extra life
            self.image = load_or_create_image(powerup_img_paths['life'], powerup_surface, RED)
            
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
boss_group = pygame.sprite.Group()
boss_bullets = pygame.sprite.Group()

# Create paddle
paddle = Paddle()
all_sprites.add(paddle)
paddle_group.add(paddle)

# Create ball
ball = Ball()
all_sprites.add(ball)

# Create blocks - will be created in the start_level function
block_colors = [RED, ORANGE, YELLOW, GREEN, PURPLE]

# Game variable initialization
score = 0
lives = 3
level = 1
bullet_power = 1  # Bullet power
bullet_width = 1  # Number of bullets (increases with multi-shot)
is_boss_level = False
font = pygame.font.SysFont(None, 36)

# Function to start a new level
def start_level(level_num):
    global is_boss_level
    
    # Clear any existing blocks
    blocks.empty()
    boss_group.empty()
    boss_bullets.empty()
    for sprite in all_sprites:
        if isinstance(sprite, Block) or isinstance(sprite, Boss) or isinstance(sprite, BossBullet):
            all_sprites.remove(sprite)
    
    # Check if it's a boss level
    is_boss_level = (level_num % 3 == 0)  # Every 3 levels is a boss level
    
    if is_boss_level:
        # Create boss
        boss = Boss(level_num // 3)  # Boss level
        all_sprites.add(boss)
        boss_group.add(boss)
        
        # Play boss sound
        if boss_appear_sound:
            boss_appear_sound.play()
    else:
        # Create normal blocks
        for row in range(5):
            for col in range(9):
                # Increase durability with level
                strength = min(level_num + 1, 5)  # Maximum durability is 5
                block = Block(col * 85 + 20, row * 35 + 50, block_colors[row], strength)
                all_sprites.add(block)
                blocks.add(block)

# Create initial blocks for level 1
start_level(level)

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
            # Play hit sound
            if hit_sound:
                hit_sound.play()
    
    # Ball and block collision
    if ball.active and not is_boss_level:
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
    if not is_boss_level:
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
    
    # Bullet and boss collision
    if is_boss_level:
        hits = pygame.sprite.groupcollide(bullets, boss_group, True, False)
        for bullet, hit_bosses in hits.items():
            for boss in hit_bosses:
                if boss.hit(bullet_power):  # Apply damage and check if defeated
                    boss.kill()  # Remove boss
                    score += 500  # Bonus points for defeating boss
                    
                    # Drop multiple power-ups when boss is defeated
                    for i in range(3):
                        powerup = PowerUp(
                            boss.rect.centerx + random.randint(-50, 50),
                            boss.rect.centery + random.randint(-30, 30),
                            random.randint(0, 2)
                        )
                        all_sprites.add(powerup)
                        powerups.add(powerup)
                score += 20
    
    # Paddle and power-up collision
    hits = pygame.sprite.spritecollide(paddle, powerups, True)
    for powerup in hits:
        # Play powerup sound
        if powerup_sound:
            powerup_sound.play()
            
        if powerup.type == 0:  # Extra damage
            bullet_power += 1
        elif powerup.type == 1:  # Multi-shot
            if bullet_width < 20:  # Maximum 20 bullets
                bullet_width += 1
        elif powerup.type == 2:  # Extra life
            lives += 1
    
    # Player and boss bullets collision
    hits = pygame.sprite.spritecollide(paddle, boss_bullets, True)
    if hits:
        lives -= 1
        if lives <= 0:
            ball.active = False
        # Play hit sound
        if hit_sound:
            hit_sound.play()
    
    # Ball falls off
    if not ball.active:
        lives -= 1
        if lives > 0:
            ball.reset()
        else:
            # Play game over sound
            if game_over_sound:
                game_over_sound.play()
                
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
                            is_boss_level = False
                            
                            # Clear all entities and recreate initial level
                            for sprite in all_sprites:
                                if isinstance(sprite, (Block, PowerUp, Boss, BossBullet)):
                                    all_sprites.remove(sprite)
                            blocks.empty()
                            powerups.empty()
                            boss_group.empty()
                            boss_bullets.empty()
                            
                            # Start fresh at level 1
                            start_level(level)
                            
                            waiting = False
    
    # Level up when all blocks/bosses are destroyed
    if (not is_boss_level and len(blocks) == 0) or (is_boss_level and len(boss_group) == 0):
        level += 1
        
        # Play level up sound
        if level_up_sound:
            level_up_sound.play()
            
        level_up_text = font.render(f"LEVEL {level} COMPLETE!", True, WHITE)
        screen.blit(level_up_text, (WIDTH//2 - 120, HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(2000)
        
        # Start the next level
        start_level(level)
        
        # Reset ball and increase speed
        ball.reset()
        ball.speed_x *= 1.1
        ball.speed_y *= 1.1
    
    # Drawing
    screen.fill(BLACK)
    all_sprites.draw(screen)
    
    # Draw boss health bar if it's a boss level
    if is_boss_level and boss_group:
        for boss in boss_group:
            boss.draw_health_bar(screen)
    
    # Display score and other info
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    power_text = font.render(f"Power: {bullet_power}", True, WHITE)
    width_text = font.render(f"Bullets: {bullet_width}/20", True, WHITE)
    
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