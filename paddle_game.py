import pygame
import random
import sys

# ゲームの初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ブロック崩しゲーム")

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# パドルクラス
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
        
    def update(self):
        # キー入力による移動
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

# ボールクラス
class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.size = 10
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(WHITE)
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
            
        # ボールの移動
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        
        # 左右の壁の衝突判定
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.speed_x = -self.speed_x
        
        # 上の壁の衝突判定
        if self.rect.top <= 0:
            self.speed_y = -self.speed_y
            
        # 下に落ちた場合
        if self.rect.bottom >= HEIGHT:
            self.active = False
            
    def reset(self):
        self.rect.centerx = WIDTH // 2
        self.rect.centery = HEIGHT // 2
        self.speed_x = random.choice([-4, -3, 3, 4])
        self.speed_y = -4
        self.active = True

# ブロッククラス
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.width = 80
        self.height = 30
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# スプライトグループの設定
all_sprites = pygame.sprite.Group()
blocks = pygame.sprite.Group()
paddle_group = pygame.sprite.Group()

# パドルの作成
paddle = Paddle()
all_sprites.add(paddle)
paddle_group.add(paddle)

# ボールの作成
ball = Ball()
all_sprites.add(ball)

# ブロックの作成
block_colors = [RED, ORANGE, YELLOW, GREEN, PURPLE]
for row in range(5):
    for col in range(9):
        block = Block(col * 85 + 20, row * 35 + 50, block_colors[row])
        all_sprites.add(block)
        blocks.add(block)

# スコアの初期化
score = 0
lives = 3
font = pygame.font.SysFont(None, 36)

# メインゲームループ
clock = pygame.time.Clock()
running = True

while running:
    # フレームレートの設定
    clock.tick(60)
    
    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # ボールが非アクティブでスペースを押すと再開
            if event.key == pygame.K_SPACE and not ball.active and lives > 0:
                ball.reset()
    
    # スプライトの更新
    all_sprites.update()
    
    # ボールとパドルの衝突判定
    if ball.active:
        hits = pygame.sprite.spritecollide(ball, paddle_group, False)
        for hit in hits:
            ball.speed_y = -abs(ball.speed_y)  # 常に上向きに
            # パドルのどこに当たったかで跳ね返る角度を変える
            ball.speed_x = (ball.rect.centerx - paddle.rect.centerx) / (paddle.width / 2) * 5
    
    # ボールとブロックの衝突判定
    if ball.active:
        hits = pygame.sprite.spritecollide(ball, blocks, True)
        if hits:
            ball.speed_y = -ball.speed_y
            score += len(hits) * 10
    
    # ボールが落ちた場合
    if not ball.active:
        lives -= 1
        if lives > 0:
            ball.reset()
        else:
            # ゲームオーバー表示
            game_over_text = font.render("GAME OVER - Press R to Restart", True, WHITE)
            screen.blit(game_over_text, (WIDTH//2 - 180, HEIGHT//2))
            pygame.display.flip()
            
            # Rキーでリスタート
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        waiting = False
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            # ゲームをリセット
                            lives = 3
                            score = 0
                            ball.reset()
                            
                            # ブロックを再作成
                            blocks.empty()
                            for sprite in all_sprites:
                                if isinstance(sprite, Block):
                                    all_sprites.remove(sprite)
                            
                            for row in range(5):
                                for col in range(9):
                                    block = Block(col * 85 + 20, row * 35 + 50, block_colors[row])
                                    all_sprites.add(block)
                                    blocks.add(block)
                            
                            waiting = False
    
    # すべてのブロックを壊したらレベルアップ
    if len(blocks) == 0:
        level_up_text = font.render("LEVEL COMPLETE!", True, WHITE)
        screen.blit(level_up_text, (WIDTH//2 - 100, HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(2000)
        
        # ブロックを再作成
        for row in range(5):
            for col in range(9):
                block = Block(col * 85 + 20, row * 35 + 50, block_colors[row])
                all_sprites.add(block)
                blocks.add(block)
        
        # ボールをリセットして速度を上げる
        ball.reset()
        ball.speed_x *= 1.2
        ball.speed_y *= 1.2
    
    # 描画
    screen.fill(BLACK)
    all_sprites.draw(screen)
    
    # スコアと残りライフの表示
    score_text = font.render(f"スコア: {score}", True, WHITE)
    lives_text = font.render(f"ライフ: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (WIDTH - 120, 10))
    
    # 画面の更新
    pygame.display.flip()

# ゲーム終了
pygame.quit()
sys.exit() 