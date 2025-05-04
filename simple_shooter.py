import pygame
import random
import sys

# ゲームの初期化
pygame.init()

# 画面設定
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("シンプルシューティングゲーム")

# 色の定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# プレイヤークラス
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
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
            
    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

# 弾クラス
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = -10
        
    def update(self):
        self.rect.y += self.speed
        # 画面外に出たら削除
        if self.rect.bottom < 0:
            self.kill()

# 敵クラス
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 4)
        self.speedx = random.randrange(-2, 2)
        
    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        # 画面外に出たら再配置
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 25:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 4)
            self.speedx = random.randrange(-2, 2)

# スプライトグループの設定
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# プレイヤーの作成
player = Player()
all_sprites.add(player)

# 敵の作成
for i in range(8):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# スコアの初期化
score = 0
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
            if event.key == pygame.K_SPACE:
                player.shoot()
    
    # スプライトの更新
    all_sprites.update()
    
    # 弾と敵の衝突判定
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        score += 10
        enemy = Enemy()
        all_sprites.add(enemy)
        enemies.add(enemy)
    
    # プレイヤーと敵の衝突判定
    hits = pygame.sprite.spritecollide(player, enemies, False)
    if hits:
        running = False
        
    # 描画
    screen.fill(BLACK)
    all_sprites.draw(screen)
    
    # スコア表示
    score_text = font.render(f"スコア: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # 画面の更新
    pygame.display.flip()

# ゲーム終了
pygame.quit()
sys.exit() 