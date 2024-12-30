import sys
import random
import pygame
from pygame.locals import *

pygame.init()

# Game assets
player_ship = 'player.png'
enemy_ship = 'enemy.png'
ufo_ship = 'ufo.png'
player_bullet = 'peluru.png'
enemy_bullet = 'pelurumusuh.png'
ufo_bullet = 'pelurumusuh.png'

# Initialize screen
screen = pygame.display.set_mode((0, 0), FULLSCREEN)
s_width, s_height = screen.get_size()
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

# Font initialization
pygame.font.init()
title_font = pygame.font.Font(None, 74)
normal_font = pygame.font.Font(None, 36)

# Sprite groups
background_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
sprite_group = pygame.sprite.Group()
ufo_group = pygame.sprite.Group()
playerbullet_group = pygame.sprite.Group()
enemybullet_group = pygame.sprite.Group()
ufobullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()

class Background(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface([x, y])
        self.image.fill('blue')
        self.image.set_colorkey('black')
        self.rect = self.image.get_rect()

    def update(self):
        self.rect.y += 1
        self.rect.x += 1
        if self.rect.y > s_height:
            self.rect.y = random.randrange(-10, 0)
            self.rect.x = random.randrange(-400, s_width)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load(player_ship).convert_alpha()
            self.image = pygame.transform.scale(self.image, (80, 60))
        except pygame.error as e:
            print(f"Error loading {player_ship}: {e}")
            sys.exit()
        self.original_image = self.image  # Simpan gambar asli
        self.rect = self.image.get_rect()
        self.image.set_colorkey('black')
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.blink_timer = 0
        self.blink_interval = 100  # Interval kedipan dalam milidetik
        self.visible = True

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = PlayerBullet(player_bullet)
            bullet.rect.centerx = self.rect.centerx
            bullet.rect.bottom = self.rect.top
            playerbullet_group.add(bullet)
            sprite_group.add(bullet)

    def update(self):
        mouse = pygame.mouse.get_pos()
        self.rect.center = mouse
        
        # Update invulnerability dan efek kedipan
        if self.invulnerable:
            current_time = pygame.time.get_ticks()
            
            # Cek apakah periode invulnerable sudah selesai (3000ms = 3 detik)
            if current_time - self.invulnerable_timer > 3000:
                self.invulnerable = False
                self.visible = True
                self.image = self.original_image
            else:
                # Efek kedipan
                if current_time - self.blink_timer > self.blink_interval:
                    self.blink_timer = current_time
                    self.visible = not self.visible
                    if self.visible:
                        self.image = self.original_image
                    else:
                        # Buat gambar transparan
                        self.image = pygame.Surface((80, 60), pygame.SRCALPHA)
                        self.image.fill((0, 0, 0, 0))  # Transparan sepenuhnya

    def make_invulnerable(self):
        self.invulnerable = True
        self.invulnerable_timer = pygame.time.get_ticks()
        self.blink_timer = pygame.time.get_ticks()
        self.visible = True

class Enemy(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__()
        try:
            self.image = pygame.image.load(img).convert_alpha()
            self.image = pygame.transform.scale(self.image, (80, 60))
        except pygame.error as e:
            print(f"Error loading {img}: {e}")
            sys.exit()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(0, s_width-50)
        self.rect.y = random.randrange(-500, 0)
        self.last_shot = pygame.time.get_ticks()
        self.shoot_delay = random.randint(1000, 3000)
        self.health = 2

    def update(self):
        self.rect.y += 1
        if self.rect.y > s_height:
            self.rect.x = random.randrange(0, s_width-50)
            self.rect.y = random.randrange(-2000, 0)
        self.shoot()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            bullet = EnemyBullet(enemy_bullet)
            bullet.rect.centerx = self.rect.centerx
            bullet.rect.top = self.rect.bottom
            enemybullet_group.add(bullet)
            sprite_group.add(bullet)

class Ufo(Enemy):
    def __init__(self, img):
        super().__init__(img)
        self.rect.x = -200
        self.rect.y = 200
        self.move = 1
        self.shoot_delay = 1500
        self.health = 3

    def update(self):
        self.rect.x += self.move
        if self.rect.x > s_width + 200:
            self.move *= -1
        elif self.rect.x < -200:
            self.move *= -1
        self.shoot()

class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, img):
        super().__init__()
        try:
            self.image = pygame.image.load(img).convert_alpha()
            self.image = pygame.transform.scale(self.image, (20, 40))
        except pygame.error as e:
            print(f"Error loading {img}: {e}")
            sys.exit()
        self.rect = self.image.get_rect()
        self.image.set_colorkey('black')

    def update(self):
        self.rect.y -= 10
        if self.rect.bottom < 0:
            self.kill()

class EnemyBullet(PlayerBullet):
    def __init__(self, img):
        super().__init__(img)

    def update(self):
        self.rect.y += 3
        if self.rect.top > s_height:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.img_list = []  # Initialize the img_list
        for i in range(1, 7):
            try:
                img = pygame.image.load(f'exp{i}.png').convert()
                img.set_colorkey('black')
                img = pygame.transform.scale(img, (120, 120))
                self.img_list.append(img)
            except pygame.error as e:
                print(f"Error loading explosion image {i}: {e}")
                sys.exit()
        self.index = 0
        self.image = self.img_list[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.count_delay = 0

    def update(self):
        self.count_delay += 1
        if self.count_delay >= 12:  # Fixed missing colon
            if self.index < len(self.img_list) - 1:
                self.count_delay = 0
                self.index += 1
                self.image = self.img_list[self.index]
        if self.index >= len(self.img_list) - 1:
            if self.count_delay >= 12:
                self.kill()

class Game:
    def __init__(self):
        self.score = 0
        self.lives = 3
        self.game_state = "opening"  # New game state variable
        try:
            self.life_icon = pygame.image.load(player_ship).convert_alpha()
            self.life_icon = pygame.transform.scale(self.life_icon, (30, 30))
        except pygame.error as e:
            print(f"Error loading life icon: {e}")
            sys.exit()

    def show_opening_screen(self):
        screen.fill(BLACK)
        
        # Title
        title_text = title_font.render("Space War", True, WHITE)
        title_rect = title_text.get_rect(center=(s_width//2, s_height//4))
        screen.blit(title_text, title_rect)
        
        # Team info
        team_text = normal_font.render("Kelompok 10", True, WHITE)
        team_rect = team_text.get_rect(center=(s_width//2, s_height//2 - 60))
        screen.blit(team_text, team_rect)
        
        # Member names
        members = [
            "Achmad Syamsudin  23091397146",
            "Zaki Fikri Ardiansyah 23091397149",
            "Dea Ayu Novita Putri 23091397173"
        ]
        
        for i, member in enumerate(members):
            member_text = normal_font.render(member, True, WHITE)
            member_rect = member_text.get_rect(center=(s_width//2, s_height//2 + i*40))
            screen.blit(member_text, member_rect)
        
        # Start instruction
        start_text = normal_font.render("Press SPACE to start", True, WHITE)
        start_rect = start_text.get_rect(center=(s_width//2, s_height*3//4))
        screen.blit(start_text, start_rect)

    def show_game_over_screen(self):
        screen.fill(BLACK)
        
        # Game Over text
        game_over_text = title_font.render("Game Over", True, WHITE)
        game_over_rect = game_over_text.get_rect(center=(s_width//2, s_height//3))
        screen.blit(game_over_text, game_over_rect)
        
        # Score
        score_text = normal_font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(s_width//2, s_height//2))
        screen.blit(score_text, score_rect)
        
        # Try again instruction
        retry_text = normal_font.render("Press SPACE to try again", True, WHITE)
        retry_rect = retry_text.get_rect(center=(s_width//2, s_height*2//3))
        screen.blit(retry_text, retry_rect)

    def reset_game(self):
        # Clear all sprite groups
        sprite_group.empty()
        player_group.empty()
        enemy_group.empty()
        ufo_group.empty()
        playerbullet_group.empty()
        enemybullet_group.empty()
        ufobullet_group.empty()
        explosion_group.empty()
        background_group.empty()
        
        # Reset game variables
        self.score = 0
        self.lives = 3
        
        # Create new game objects
        self.create_background()
        self.create_player()
        self.create_enemy()
        self.create_ufo()
        
    def check_player_hits(self):
        if not self.player.invulnerable:
            hits = pygame.sprite.spritecollide(self.player, enemybullet_group, True)
            hits_ufo = pygame.sprite.spritecollide(self.player, ufobullet_group, True)
            
            if hits or hits_ufo:
                self.lives -= 1
                if self.lives >= 0:
                    self.player.make_invulnerable()
                    explosion = Explosion(self.player.rect.centerx, self.player.rect.centery)
                    explosion_group.add(explosion)
                    sprite_group.add(explosion)
                else:
                    pygame.quit()
                    sys.exit()

    def create_background(self):
        for i in range(40):
            x = random.randint(1, 7)
            background_image = Background(x, x)
            background_image.rect.x = random.randrange(0, s_width)
            background_image.rect.y = random.randrange(0, s_height)
            background_group.add(background_image)
            sprite_group.add(background_image)

    def create_player(self):
        self.player = Player()
        player_group.add(self.player)
        sprite_group.add(self.player)

    def create_enemy(self):
        for i in range(10):
            self.enemy = Enemy(enemy_ship)
            enemy_group.add(self.enemy)
            sprite_group.add(self.enemy)

    def create_ufo(self):
        for i in range(1):
            self.ufo = Ufo(ufo_ship)
            ufo_group.add(self.ufo)
            sprite_group.add(self.ufo)

    def check_collision(self):
        # Player bullets hitting enemies
        hits = pygame.sprite.groupcollide(enemy_group, playerbullet_group, False, True)
        for enemy in hits:
            enemy.health -= 1
            if enemy.health <= 0:
                expl_x = enemy.rect.x + enemy.rect.width // 2  # Center the explosion
                expl_y = enemy.rect.y + enemy.rect.height // 2
                explosion = Explosion(expl_x, expl_y)
                explosion_group.add(explosion)
                sprite_group.add(explosion)
                enemy.rect.x = random.randrange(0, s_width)
                enemy.rect.y = random.randrange(-3000, 0)
                enemy.health = 2
                self.score += 100

        # Player bullets hitting UFO
        hits = pygame.sprite.groupcollide(ufo_group, playerbullet_group, False, True)
        for ufo in hits:
            ufo.health -= 1
            if ufo.health <= 0:
                expl_x = ufo.rect.x + ufo.rect.width // 2  # Center the explosion
                expl_y = ufo.rect.y + ufo.rect.height // 2
                explosion = Explosion(expl_x, expl_y)
                explosion_group.add(explosion)
                sprite_group.add(explosion)
                ufo.rect.x = -200
                ufo.health = 3
                self.score += 500

    def display_score(self):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

    def display_lives(self):
        if self.life_icon:
            for i in range(self.lives):
                screen.blit(self.life_icon, (10 + i * 40, s_height - 40))

    def check_player_hits(self):
        if not self.player.invulnerable:
            hits = pygame.sprite.spritecollide(self.player, enemybullet_group, True)
            hits_ufo = pygame.sprite.spritecollide(self.player, ufobullet_group, True)
            
            if hits or hits_ufo:
                self.lives -= 1
                if self.lives >= 0:
                    self.player.make_invulnerable()
                    explosion = Explosion(self.player.rect.centerx, self.player.rect.centery)
                    explosion_group.add(explosion)
                    sprite_group.add(explosion)
                else:
                    self.game_state = "game_over"

    def run_update(self):
        sprite_group.draw(screen)
        sprite_group.update()
        self.display_score()
        self.display_lives()

    def start_game(self):
        while True:
            if self.game_state == "opening":
                self.show_opening_screen()
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == KEYDOWN:
                        if event.key == K_SPACE:
                            self.game_state = "playing"
                            self.reset_game()
                        elif event.key == K_ESCAPE:
                            pygame.quit()
                            sys.exit()
            
            elif self.game_state == "playing":
                screen.fill('black')
                self.check_collision()
                self.check_player_hits()
                self.run_update()
                
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == KEYDOWN:
                        if event.key == K_SPACE:
                            self.player.shoot()
                        if event.key == K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                    if event.type == MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.player.shoot()
            
            elif self.game_state == "game_over":
                self.show_game_over_screen()
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == KEYDOWN:
                        if event.key == K_SPACE:
                            self.game_state = "playing"
                            self.reset_game()
                        elif event.key == K_ESCAPE:
                            pygame.quit()
                            sys.exit()
            
            pygame.display.update()
            clock.tick(FPS)

if __name__ == '__main__':
    game = Game()
    game.start_game()