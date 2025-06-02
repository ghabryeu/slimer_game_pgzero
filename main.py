import pgzrun
import random
import math
from pgzero.builtins import Actor, Rect, sounds, music, keyboard, keys

WIDTH = 463
HEIGHT = 358
FONT_REGULAR = "pixelifysansbold.ttf"

class Player:
    def __init__(self):
        self.actor = Actor('p4.png', (400, 300))
        self.images = ['p4.png', 'p3.png', 'p2.png', 'p1.png', 'p5.png']
        self.actor.image = self.images[0]
        self.animation_speed = 0.1
        self.animation_frame = 0
        self.state = 'alive'
        self.x_speed = 0
        self.y_speed = 0

    def update_animation(self):
        self.animation_frame += self.animation_speed
        if self.animation_frame >= len(self.images):
            self.animation_frame = 0
        self.actor.image = self.images[int(self.animation_frame)]

    def update_movement(self):
        self.x_speed = 0
        self.y_speed = 0
        
        if keyboard.w: self.y_speed = -5
        elif keyboard.s: self.y_speed = 5
            
        if keyboard.a: self.x_speed = -5
        elif keyboard.d: self.x_speed = 5
            
        self.actor.x += self.x_speed
        self.actor.y += self.y_speed

    def draw(self):
        if self.state == 'alive':
            self.actor.draw()

class Enemy:
    def __init__(self, player_pos):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        
        if side == 'top':
            x = random.randint(0, WIDTH)
            y = -50
        elif side == 'bottom':
            x = random.randint(0, WIDTH)
            y = HEIGHT + 50
        elif side == 'left':
            x = -50
            y = random.randint(0, HEIGHT)
        else:  
            x = WIDTH + 50
            y = random.randint(0, HEIGHT)

        self.actor = Actor('e4.png', (x, y))
        self.images = ['e4.png', 'e3.png', 'e2.png', 'e1.png', 'e5.png']
        self.actor.image = self.images[0]
        self.animation_frame = 0
        self.animation_speed = 0.1

        dx = player_pos[0] - x
        dy = player_pos[1] - y
        distance = math.hypot(dx, dy)
        speed = 0.2
        self.dx = (dx / distance) * speed
        self.dy = (dy / distance) * speed

    def update(self):
        self.animation_frame += self.animation_speed
        if self.animation_frame >= len(self.images):
            self.animation_frame = 0
        self.actor.image = self.images[int(self.animation_frame)]
        
        self.actor.x += self.dx
        self.actor.y += self.dy

    def draw(self):
        self.actor.draw()

class Bullet:
    def __init__(self, start_pos, target_pos):
        self.actor = Actor('bala1.png', start_pos)
        
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        distance = math.hypot(dx, dy)
        speed = 10
        self.dx = (dx / distance) * speed
        self.dy = (dy / distance) * speed

    def update(self):
        self.actor.x += self.dx
        self.actor.y += self.dy

    def draw(self):
        self.actor.draw()

class Game:
    def __init__(self):
        self.state = 'menu'
        self.sound_enabled = True
        self.music_enabled = True
        self.score = 0
        self.world_record = 0
        self.round_num = 1
        self.enemies_remaining = 0
        self.round_over = False
        
        self.player = Player()
        self.enemies = []
        self.bullets = []
        
        #botoes
        self.start_button = Rect(WIDTH//2 - 75, HEIGHT//2 - 20, 150, 40)
        self.next_round_button = Rect(WIDTH//2 - 75, HEIGHT//2 + 50, 150, 40)
        self.exit_button = Rect(WIDTH//2 - 75, HEIGHT//2 + 50, 150, 40)
        self.sound_toggle_button = Rect(WIDTH - 100, 10, 80, 30)
        self.music_toggle_button = Rect(WIDTH - 100, 50, 80, 30)
        
        if self.music_enabled:
            music.play('background_music.wav')

    def play_sound(self, sound_name):
        if not self.sound_enabled:
            return
            
        try:
            sound = getattr(sounds, sound_name)
            sound.play()
        except Exception:
            pass

    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        self.play_sound('button_click.wav')

    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            music.play('background_music.wav')
        else:
            music.stop()
        self.play_sound('button_click.wav')

    def start_game(self):
        self.state = 'playing'
        self.player.state = 'alive'
        self.round_over = False
        self.reset_game()

    def reset_game(self):
        if self.score > self.world_record:
            self.world_record = self.score
            self.play_sound('new_record.wav')
            
        self.score = 0
        self.player.actor.x = 400
        self.player.actor.y = 300
        self.player.state = 'alive'
        self.enemies.clear()
        self.bullets.clear()
        self.round_num = 1
        self.enemies_remaining = self.round_num * 5
        self.round_over = False

    def next_round(self):
        self.round_num += 1
        self.enemies_remaining = self.round_num * 5
        self.round_over = False
        self.enemies.clear()
        self.bullets.clear()

    def spawn_enemy(self):
        if self.enemies_remaining > 0:
            self.enemies.append(Enemy((self.player.actor.x, self.player.actor.y)))
            self.enemies_remaining -= 1
            self.play_sound('enemy_spawn.wav')

    def fire_bullet(self, target_pos):
        self.bullets.append(Bullet((self.player.actor.x, self.player.actor.y), target_pos))
        self.play_sound('shoot.wav')

    def update(self):
        if self.state != 'playing' or self.player.state == 'dead':
            return
            
        self.player.update_animation()
        self.player.update_movement()

        #atualiza inimigos
        for enemy in self.enemies[:]:
            enemy.update()
            
            if self.player.actor.colliderect(enemy.actor):
                self.player.state = 'dead'
                self.state = 'dead'
                self.play_sound('player_death.wav')

        #atualiza tiros
        for bullet in self.bullets[:]:
            bullet.update()

            if (bullet.actor.x < 0 or bullet.actor.x > WIDTH or
                bullet.actor.y < 0 or bullet.actor.y > HEIGHT):
                self.bullets.remove(bullet)
            else:
                for enemy in self.enemies[:]:
                    if bullet.actor.colliderect(enemy.actor):
                        self.enemies.remove(enemy)
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        self.score += 1
                        self.play_sound('enemy_hit.wav')
                        break

        if self.enemies_remaining > 0 and random.randint(1, 30) == 1:
            self.spawn_enemy()

        if self.enemies_remaining == 0 and len(self.enemies) == 0 and not self.round_over:
            self.round_over = True
            self.play_sound('round_complete.wav')

    def draw(self):
        screen.clear()
        screen.blit('background.png', (0, 0))
        
        if self.state == 'menu':
            self.draw_menu()
        elif self.state == 'playing':
            self.draw_game()
        elif self.state == 'dead':
            self.draw_game()
            self.draw_game_over()

        self.draw_audio_controls()

    def draw_audio_controls(self):
        #botao de som
        color = 'green' if self.sound_enabled else 'red'
        screen.draw.filled_rect(self.sound_toggle_button, color)
        screen.draw.text("SOM", center=self.sound_toggle_button.center, fontsize=20, color="white", fontname=FONT_REGULAR)
        
        #botao de musica
        color = 'green' if self.music_enabled else 'red'
        screen.draw.filled_rect(self.music_toggle_button, color)
        screen.draw.text("MÚSICA", center=self.music_toggle_button.center, fontsize=20, color="white", fontname=FONT_REGULAR)

    def draw_menu(self):
        title = Actor('title.png', center=(WIDTH/2 - 50, HEIGHT/2 - 100))
        title.draw()
        
        start_btn = Actor('start3.png', center=self.start_button.center)
        start_btn.draw()
        
        screen.draw.filled_rect(self.exit_button, "green")
        screen.draw.text("SAIR", center=self.exit_button.center, fontsize=25, color="white", fontname=FONT_REGULAR)

    def draw_game(self):
        self.player.draw()

        for bullet in self.bullets:
            bullet.draw()

        for enemy in self.enemies:
            enemy.draw()

        screen.draw.text(f"Score: {self.score}", (10, 10))
        screen.draw.text(f"World Record: {self.world_record}", (10, 30))
        screen.draw.text(f"Round: {self.round_num}", (10, 50))

        if self.round_over:
            screen.draw.filled_rect(self.next_round_button, "green")
            screen.draw.text("NEXT ROUND", center=self.next_round_button.center, fontsize=30, color="white", fontname=FONT_REGULAR)

    def draw_game_over(self):
        screen.draw.text("VOCÊ MORREU!", center=(WIDTH/2, HEIGHT/2 - 50), fontsize=60, color="red", fontname=FONT_REGULAR)

        screen.draw.filled_rect(self.start_button, "green")
        screen.draw.text("Try Again!", center=self.start_button.center, fontsize=25, color="white", fontname=FONT_REGULAR)

        screen.draw.filled_rect(self.exit_button, "red")
        screen.draw.text("Exit", center=self.exit_button.center, fontsize=25, color="white", fontname=FONT_REGULAR)

#instancia do jogo
game = Game()

def update():
    game.update()

def draw():
    game.draw()

def on_key_down(key):
    if game.state == 'playing' and key == keys.R:
        game.reset_game()
    elif key == keys.ESCAPE:
        if game.state == 'playing':
            game.state = 'menu'
        else:
            game.state = 'playing'

def on_mouse_down(pos):
    if game.sound_toggle_button.collidepoint(pos):
        game.toggle_sound()
        return
    elif game.music_toggle_button.collidepoint(pos):
        game.toggle_music()
        return
    
    if game.state == 'menu' and game.start_button.collidepoint(pos):
        game.play_sound('button_click.wav')
        game.start_game()
    elif game.state == 'menu' and game.exit_button.collidepoint(pos):
        game.play_sound('button_click.wav')
        exit()
    elif game.state == 'dead' and game.start_button.collidepoint(pos):
        game.play_sound('button_click.wav')
        game.start_game()
    elif game.state == 'dead' and game.exit_button.collidepoint(pos):
        game.play_sound('button_click.wav')
        exit()
    elif game.state == 'playing' and game.round_over and game.next_round_button.collidepoint(pos):
        game.play_sound('button_click.wav')
        game.next_round()
    elif game.state == 'playing' and game.player.state == 'alive':
        game.fire_bullet(pos)

pgzrun.go()