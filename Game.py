import pygame
import sys
import random

pygame.init()

WIDTH = 600
HEIGHT = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
run = True
clock = pygame.time.Clock()
BLUE = (0, 0, 255)
BROWN = (153, 76, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ScoreFont = pygame.font.SysFont("Cherish Today", 30, True)


class Player(object):
    idle = [pygame.image.load('Idle (1).png'), pygame.image.load('Idle (2).png'), pygame.image.load('Idle (3).png'),
            pygame.image.load('Idle (4).png'), pygame.image.load('Idle (5).png'), pygame.image.load('Idle (6).png'),
            pygame.image.load('Idle (7).png'), pygame.image.load('Idle (8).png'), pygame.image.load('Idle (9).png'),
            pygame.image.load('Idle (10).png')]

    walk = [pygame.image.load('Run (1).png'), pygame.image.load('Run (2).png'), pygame.image.load('Run (3).png'),
            pygame.image.load('Run (4).png'), pygame.image.load('Run (5).png'), pygame.image.load('Run (6).png'),
            pygame.image.load('Run (7).png'), pygame.image.load('Run (8).png')]

    dead = [pygame.image.load('Dead (1).png'), pygame.image.load('Dead (2).png'), pygame.image.load('Dead (3).png'),
            pygame.image.load('Dead (4).png'), pygame.image.load('Dead (5).png'), pygame.image.load('Dead (6).png'),
            pygame.image.load('Dead (7).png'), pygame.image.load('Dead (8).png'), pygame.image.load('Dead (9).png'),
            pygame.image.load('Dead (10).png')]

    jump = [pygame.image.load('Jump (1).png'), pygame.image.load('Jump (2).png'), pygame.image.load('Jump (3).png'),
            pygame.image.load('Jump (4).png'), pygame.image.load('Jump (5).png'), pygame.image.load('Jump (6).png'),
            pygame.image.load('Jump (7).png'), pygame.image.load('Jump (8).png'), pygame.image.load('Jump (9).png'),
            pygame.image.load('Jump (10).png')]

    duck = [pygame.image.load('Duck (1).png'), pygame.image.load('Duck (2).png'), pygame.image.load('Duck (3).png'),
            pygame.image.load('Duck (4).png'), pygame.image.load('Duck (5).png')]

    shoot = [pygame.image.load('Shoot (1).png'), pygame.image.load('Shoot (2).png'), pygame.image.load('Shoot (3).png')]

    background = pygame.image.load('city.png')

    def __init__(self):
        self.width = 50
        self.height = 100
        self.x = 200
        self.y = HEIGHT - self.height
        self.speed = 5
        self.direction = "Right"
        # We use next 6 variables to determine if such action was taken
        self.Left = False
        self.Right = False
        self.Jump = False
        self.Stand = True
        self.Shoot = False
        self.Duck = False

        # We use next 6 variables to go through images and display moving as smooth animation
        self.jump_count = 9
        self.walk_count = 0
        self.stand_count = 0
        self.shoot_count = 0
        self.duck_count = 0
        self.dead_count = 0

        self.bullets = []
        self.hit_points = 10
        self.hitbox = [self.x + 50, self.y, self.width, self.height]
        self.Hit = False
        self.Dead = False
        self.score = 0

        # Bullet stacks and reload variables stop the player from spamming bullets
        self.bullet_stack = 5
        self.reload = False
        self.reload_count = 0

    def movement(self):
        global run
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                sys.exit()

        keys = pygame.key.get_pressed()

        #we do not allow player to move if character is dead:
        if not self.Dead:

            # We do not allow player to Duck while jumping
            if keys[pygame.K_DOWN] and not self.Jump:
                self.Duck = True
            else:
                self.Duck = False

            # We do not allow player to Shoot while Ducking
            # Next part of this method is allowing the player only 5 bullets, then the gun reloads for a second
            if keys[pygame.K_SPACE] and not self.Duck:
                if not self.reload:
                    self.bullets.append(Bullet(self.x, self.y, BLACK, self.direction, 10, 3))
                    self.Shoot = True
                    self.Stand = False
                    self.bullet_stack -= 1

            if self.bullet_stack <= 0:
                self.reload = True
                self.reload_count += 1
                if self.reload_count >= 60:
                    self.reload = False
                    self.bullet_stack = 5
                    self.reload_count = 0

            # We do not allow player to leave the screen
            if keys[pygame.K_LEFT]:
                if self.x > 0:
                    self.x -= self.speed
                self.direction = "Left"
                self.Left = True
                self.Right = False
            elif keys[pygame.K_RIGHT]:
                if self.x + self.width < WIDTH:
                    self.x += self.speed
                self.direction = "Right"
                self.Right = True
                self.Left = False
            else:
                self.Left = False
                self.Right = False
                self.walk_count = 0

            # For jump we use quadratic function to make the jump faster at the beginning and slower at the top
            if not self.Jump:
                if keys[pygame.K_UP]:
                    self.Jump = True
                    self.Left = False
                    self.Right = False
            else:
                if self.jump_count >= -9:
                    neg = 1
                    if self.jump_count < 0:
                        neg = -1
                    self.y -= (self.jump_count ** 2) / 2 * neg
                    self.jump_count -= 1
                else:
                    self.jump_count = 9
                    self.Jump = False
                self.Left = False
                self.Right = False

            if not self.Left and not self.Right and not self.Jump and not self.Shoot and not self.Duck:
                self.Stand = True
            else:
                self.Stand = False

            # When we are shooting or ducking we want to display those animations rather than walking or jumping
            if self.Duck or self.Shoot:
                self.Left = False
                self.Right = False
                
            if self.Duck:
                self.Shoot = False


            # Adjusting the hitbox based on players actions
            self.hitbox = [self.x + 20, self.y, self.width - 13, self.height]

            if self.direction == "Left":
                self.hitbox[0] = self.x + 35
            if self.Duck:
                self.hitbox[0] = self.x + 5
                self.hitbox[1] = self.y + 45
                if self.direction == "Left":
                    self.hitbox[0] = self.x + 53

        # This else refers to if not self.Dead condition: if player is in fact dead we want not only to stop his movement
        #but also to stop the program from displaying the images of moving
        else:
            self.Left = False
            self.Right = False
            self.Jump = False
            self.Shoot = False
            self.Duck = False
            self.Stand = False
            self.hitbox = [0, 0, 0, 0]

    # We display every image for 3 frames so we // the counts by 3 and reset them when they hit the number of images
    def draw(self):
        global run
        screen.blit(self.background, (0, 0))

        if self.walk_count >= 3 * len(self.walk):
            self.walk_count = 0
        if self.stand_count >= 3 * len(self.idle):
            self.stand_count = 0

        if self.Left:
            screen.blit(pygame.transform.flip(self.walk[self.walk_count // 3], True, False), (self.x, self.y))
            self.walk_count += 1

        if self.Right:
            screen.blit(self.walk[self.walk_count // 3], (self.x, self.y))
            self.walk_count += 1

        # We give shooting animation more value than jumping
        elif self.Jump and not self.Shoot:
            if self.direction == "Right":
                screen.blit(self.jump[self.jump_count // 3], (self.x, self.y))
            elif self.direction == "Left":
                screen.blit(pygame.transform.flip(self.jump[self.jump_count // 3], True, False), (self.x, self.y))

        elif self.Stand:
            if self.direction == "Right":
                screen.blit(self.idle[self.stand_count // 3], (self.x, self.y))
            elif self.direction == "Left":
                screen.blit(pygame.transform.flip(self.idle[self.stand_count // 3], True, False), (self.x, self.y))
            self.stand_count += 1

        if self.Shoot:
            if self.direction == "Right":
                screen.blit(self.shoot[self.shoot_count // 3], (self.x, self.y))
            if self.direction == "Left":
                screen.blit(pygame.transform.flip(self.shoot[self.shoot_count // 3], True, False), (self.x, self.y))
            self.shoot_count += 1
            if self.shoot_count >= 3 * len(self.shoot):
                self.shoot_count = 0
                self.Shoot = False

        if self.Duck:
            if self.direction == "Right":
                screen.blit(self.duck[self.duck_count // 3], (self.x, self.y))
            if self.direction == "Left":
                screen.blit(pygame.transform.flip(self.duck[self.duck_count // 3], True, False), (self.x, self.y))
            self.duck_count += 1
            if self.duck_count >= 3 * len(self.duck):
                self.duck_count = 0

        # When player dies we first display the dying animation and only then stop the game
        if self.Dead:
            screen.blit(self.dead[self.dead_count // 3], (self.x, HEIGHT - self.height))
            self.dead_count += 1
            if self.dead_count == 30:
                run = False

        for bullet in self.bullets:
            bullet.draw()
            if WIDTH < bullet.x < 0:  # leaving the screen
                self.bullets.pop(self.bullets.index(bullet))

        pygame.draw.rect(screen, RED, (self.x + 10, self.y - 10, 100, 10))
        if not self.Dead:
            pygame.draw.rect(screen, GREEN, (self.x + 10, self.y - 10, self.hit_points * 10, 10))

        # Since the enemies dont turn when player goes behind them we are going to kill the player if he ever goes behind
        # the enemy
        death_ray = pygame.Surface((50, 400))
        death_ray.set_alpha(50)
        death_ray.fill((255, 0, 0))
        screen.blit(death_ray, (550, 0))

        score_print = ScoreFont.render("Score " + str(self.score), 1, BLACK)
        screen.blit(score_print, (500, 0))

        bullet_stack_print = ScoreFont.render("Bullets: " + str(self.bullet_stack), 1, BLACK)
        screen.blit(bullet_stack_print, (0, 0))

        if self.reload:
            reload_print = ScoreFont.render("RELOADING", 1, YELLOW)
            screen.blit(reload_print, (0, 50))

        # pygame.draw.rect(screen, RED, (self.hitbox[0], self.hitbox[1], self.hitbox[2], self.hitbox[3]), 2)

    def hits(self, enemy):
        if not enemy.Dead:

            for bullet in enemy.bullets:
                if self.hitbox[0] < bullet.x - bullet.radius < self.hitbox[0] + self.hitbox[2]:
                    if self.hitbox[1] < bullet.y + bullet.radius < self.hitbox[1] + self.hitbox[3]:
                        self.Hit = True
                        enemy.bullets.pop(enemy.bullets.index(bullet))
            if self.Hit:
                self.hit_points -= 1
                self.Hit = False
                if self.hit_points == 0:
                    self.Dead = True
            if self.x + self.width >= 550:
                self.Dead = True

class Bullet(object):

    def __init__(self, x, y, color, direction, speed, radius):
        self.color = color
        self.direction = direction
        self.speed = speed
        self.radius = radius

        # changing place where bullets come from based on direction the character is facing
        if self.direction == "Right":
            self.x = x + 100
            self.y = y + 50
        elif self.direction == "Left":
            self.x = x + 5
            self.y = y + 50

    def draw(self):
        if 0 < self.x < WIDTH:
            pygame.draw.circle(screen, self.color, (self.x, round(self.y)), self.radius)
            if self.direction == "Right":
                self.x += self.speed
            elif self.direction == "Left":
                self.x -= self.speed


class Enemy(object):
    walk_s = [pygame.image.load('Walk_S (1).png'), pygame.image.load('Walk_S (2).png'),
              pygame.image.load('Walk_S (3).png'), pygame.image.load('Walk_S (4).png'),
              pygame.image.load('Walk_S (5).png'), pygame.image.load('Walk_S (6).png'),
              pygame.image.load('Walk_S (7).png'), pygame.image.load('Walk_S (8).png'),
              pygame.image.load('Walk_S (9).png'), pygame.image.load('Walk_S (10).png')]

    jump_s = [pygame.image.load('Jump_S (1).png'), pygame.image.load('Jump_S (2).png'),
              pygame.image.load('Jump_S (3).png'), pygame.image.load('Jump_S (4).png'),
              pygame.image.load('Jump_S (5).png'), pygame.image.load('Jump_S (6).png'),
              pygame.image.load('Jump_S (7).png'), pygame.image.load('Jump_S (8).png'),
              pygame.image.load('Jump_S (9).png'), pygame.image.load('Jump_S (10).png'),
              pygame.image.load('Jump_S (11).png'), pygame.image.load('Jump_S (12).png')]

    shoot_s = [pygame.image.load('Shoot_S (1).png'), pygame.image.load('Shoot_S (2).png'),
               pygame.image.load('Shoot_S (3).png'), pygame.image.load('Shoot_S (4).png'),
               pygame.image.load('Shoot_S (5).png'), pygame.image.load('Shoot_S (6).png'),
               pygame.image.load('Shoot_S (7).png')]

    dead_s = [pygame.image.load('Die_S (1).png'), pygame.image.load('Die_S (2).png'),
              pygame.image.load('Die_S (3).png'), pygame.image.load('Die_S (4).png'),
              pygame.image.load('Die_S (5).png'), pygame.image.load('Die_S (6).png')]

    images_s = [walk_s, jump_s, shoot_s, dead_s]

    walk_dino = [pygame.transform.flip(pygame.image.load('Walk_Dino (1).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Walk_Dino (2).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Walk_Dino (3).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Walk_Dino (4).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Walk_Dino (5).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Walk_Dino (6).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Walk_Dino (7).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Walk_Dino (8).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Walk_Dino (9).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Walk_Dino (10).png'), True, False)]

    dead_dino = [pygame.transform.flip(pygame.image.load('Dead_Dino (1).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Dead_Dino (2).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Dead_Dino (3).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Dead_Dino (4).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Dead_Dino (5).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Dead_Dino (6).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Dead_Dino (7).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Dead_Dino (8).png'), True, False)]

    jump_dino = [pygame.transform.flip(pygame.image.load('Jump_Dino (1).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Jump_Dino (2).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Jump_Dino (3).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Jump_Dino (4).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Jump_Dino (5).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Jump_Dino (6).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Jump_Dino (7).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Jump_Dino (8).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Jump_Dino (9).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Jump_Dino (10).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Jump_Dino (11).png'), True, False),
                 pygame.transform.flip(pygame.image.load('Jump_Dino (12).png'), True, False)]

    shoot_dino = [pygame.transform.flip(pygame.image.load('Walk_Dino (1).png'), True, False),
                  pygame.transform.flip(pygame.image.load('Walk_Dino (2).png'), True, False),
                  pygame.transform.flip(pygame.image.load('Walk_Dino (3).png'), True, False),
                  pygame.transform.flip(pygame.image.load('Walk_Dino (4).png'), True, False),
                  pygame.transform.flip(pygame.image.load('Walk_Dino (5).png'), True, False),
                  pygame.transform.flip(pygame.image.load('Walk_Dino (6).png'), True, False),
                  pygame.transform.flip(pygame.image.load('Walk_Dino (7).png'), True, False)]

    images_d = [walk_dino, jump_dino, shoot_dino, dead_dino]

    walk_R = [pygame.transform.flip(pygame.image.load('Walk_R (1).png'), True, False),
              pygame.transform.flip(pygame.image.load('Walk_R (2).png'), True, False),
              pygame.transform.flip(pygame.image.load('Walk_R (3).png'), True, False),
              pygame.transform.flip(pygame.image.load('Walk_R (4).png'), True, False),
              pygame.transform.flip(pygame.image.load('Walk_R (5).png'), True, False),
              pygame.transform.flip(pygame.image.load('Walk_R (6).png'), True, False),
              pygame.transform.flip(pygame.image.load('Walk_R (7).png'), True, False),
              pygame.transform.flip(pygame.image.load('Walk_R (8).png'), True, False)]

    dead_R = [pygame.transform.flip(pygame.image.load('Dead_R (1).png'), True, False),
              pygame.transform.flip(pygame.image.load('Dead_R (2).png'), True, False),
              pygame.transform.flip(pygame.image.load('Dead_R (3).png'), True, False),
              pygame.transform.flip(pygame.image.load('Dead_R (4).png'), True, False),
              pygame.transform.flip(pygame.image.load('Dead_R (5).png'), True, False),
              pygame.transform.flip(pygame.image.load('Dead_R (6).png'), True, False),
              pygame.transform.flip(pygame.image.load('Dead_R (7).png'), True, False),
              pygame.transform.flip(pygame.image.load('Dead_R (8).png'), True, False),
              pygame.transform.flip(pygame.image.load('Dead_R (9).png'), True, False),
              pygame.transform.flip(pygame.image.load('Dead_R (10).png'), True, False)]

    jump_R = [pygame.transform.flip(pygame.image.load('Jump_R (1).png'), True, False),
              pygame.transform.flip(pygame.image.load('Jump_R (2).png'), True, False),
              pygame.transform.flip(pygame.image.load('Jump_R (3).png'), True, False),
              pygame.transform.flip(pygame.image.load('Jump_R (4).png'), True, False),
              pygame.transform.flip(pygame.image.load('Jump_R (5).png'), True, False),
              pygame.transform.flip(pygame.image.load('Jump_R (6).png'), True, False),
              pygame.transform.flip(pygame.image.load('Jump_R (7).png'), True, False),
              pygame.transform.flip(pygame.image.load('Jump_R (8).png'), True, False),
              pygame.transform.flip(pygame.image.load('Jump_R (9).png'), True, False),
              pygame.transform.flip(pygame.image.load('Jump_R (10).png'), True, False)]

    shoot_R = [pygame.transform.flip(pygame.image.load('Walk_R (1).png'), True, False),
               pygame.transform.flip(pygame.image.load('Walk_R (2).png'), True, False),
               pygame.transform.flip(pygame.image.load('Walk_R (3).png'), True, False),
               pygame.transform.flip(pygame.image.load('Walk_R (4).png'), True, False)]

    images_r = [walk_R, jump_R, shoot_R, dead_R]

    def __init__(self, images, width, height, hit_points, bullet_speed, bullet_color, bullet_size, hitbox_additions):

        self.width = width
        self.height = height
        self.y = HEIGHT - self.height
        self.Dead = False
        self.appeared = False
        self.x = WIDTH + self.width
        self.hit_points = hit_points
        self.Left = False
        self.Right = False
        self.Shoot = False
        self.Jump = False
        self.count_left = 0
        self.count_right = 0
        self.count_jump = 9
        self.count_shoot = 0
        self.speed = 5
        self.walk_count = 0
        self.bullets = []
        self.count_bullets = 0
        self.hitbox = [self.x, self.y, self.width, self.height]
        self.Hit = False
        self.dead_count = 0
        self.images = images
        self.walk_png = self.images[0]
        self.jump_png = self.images[1]
        self.shoot_png = self.images[2]
        self.dead_png = self.images[3]
        self.completely_dead = False
        self.max_health = hit_points
        self.bullet_speed = bullet_speed
        self.bullet_color = bullet_color
        self.bullet_size = bullet_size
        self.hitbox_additions = hitbox_additions # We need different hitboxes for each enemy

    # forcing enemy to appear on the screen
    def appear(self):
        if not self.appeared:
            self.x -= 5
        if self.x <= WIDTH - self.width:
            self.appeared = True

    # We dont let the enemy go "both directions" at the same time and we limit his movements to portion of the screen
    # Enemy movements are decided randomly
    # When enemy starts moving we contionue the movement for at least 5 frames
    def movement(self):
        if not self.Left:
            if not self.Right and (self.x > 300):
                if random.random() > 0.5:
                    self.Left = True
        else:
            if (self.x > 300):
                self.x -= self.speed
                self.count_left += 1
                if self.count_left == 5:
                    self.count_left = 0
                    self.Left = False
            else:
                self.Left = False

        if not self.Right:
            if not self.Left:
                if random.random() > 0.5:
                    self.Right = True
        else:
            if self.x < WIDTH - self.width:
                self.x += self.speed
                self.count_right += 1
                if self.count_right == 5:
                    self.count_right = 0
                    self.Right = False
            else:
                self.Right = False

        if not self.Jump:
            if random.random() > 0.95:
                self.Jump = True
            else:
                self.Jump = False
        else:
            if self.count_jump >= -9:
                neg = 1
                if self.count_jump < 0:
                    neg = -1
                self.y -= (self.count_jump ** 2) / 2 * neg
                self.count_jump -= 1
            else:
                self.count_jump = 9
                self.Jump = False

        if random.random() > 0.9 and not self.Dead:
            self.Shoot = True
            if self.count_bullets > 1:
                self.Shoot = False
                self.count_bullets = 0
        else:
            self.Shoot = False

        if self.Shoot:
            self.bullets.append(Bullet(self.x, self.y, self.bullet_color, "Left", self.bullet_speed, self.bullet_size))
            self.count_bullets += 1

        # We tweak hitboxes for each enemy
        self.hitbox = [self.x + self.hitbox_additions[0], self.y + self.hitbox_additions[1], self.width + self.hitbox_additions[2], self.height + self.hitbox_additions[3]]
        if self.Jump:
            self.hitbox[3] = self.height - 10
        if not self.Jump and not self.Shoot:
            self.hitbox[1] += 17

        if self.Dead or player.Dead:
            self.Left = False
            self.Right = False
            self.Jump = False
            self.Shoot = False
            self.hitbox = [0, 0, 0, 0]

    def draw(self):

        if not self.Dead:

            if self.walk_count >= 3 * len(self.walk_png):
                self.walk_count = 0
            if self.count_shoot >= 3 * len(self.shoot_png):
                self.count_shoot = 0

            if (self.Left or self.Right) and not self.Jump and not self.Shoot:
                screen.blit(self.walk_png[self.walk_count // 3], (self.x, self.y))
                self.walk_count += 1

            if self.Jump and not self.Shoot:
                screen.blit(self.jump_png[self.count_jump // 3], (self.x, self.y))

            if self.Shoot:
                screen.blit(self.shoot_png[self.count_shoot // 3], (self.x, self.y + 5))
                self.count_shoot += 1

            if not self.Shoot and not self.Left and not self.Right and not self.Jump and not self.Dead and not self.completely_dead:
                screen.blit(self.walk_png[1], (self.x, self.y))

            for bullet in self.bullets:
                bullet.draw()

            if not self.Dead:
                pygame.draw.rect(screen, RED, (self.x + 10, self.y - 10, 100, 10))
                pygame.draw.rect(screen, GREEN, (self.x + 10, self.y - 10, self.hit_points / self.max_health * 100, 10))

        # checking if hitboxes fit
        # pygame.draw.rect(screen, RED, (self.hitbox[0], self.hitbox[1], self.hitbox[2], self.hitbox[3]), 2)

        # We display dying animation before "completely killing" the enemy
        if self.Dead and not self.completely_dead:
            screen.blit(self.dead_png[self.dead_count // 3], (self.x, self.y))
            self.dead_count += 1
            if self.dead_count >= 3 * len(self.dead_png):
                self.completely_dead = True

    def hits(self):
        for bullet in player.bullets:
            if self.hitbox[0] < bullet.x < self.hitbox[0] + self.hitbox[2]:
                if self.hitbox[1] < bullet.y < self.hitbox[1] + self.hitbox[3]:
                    self.Hit = True
                    player.bullets.pop(player.bullets.index(bullet))
        if self.Hit:
            player.score += 1
            self.hit_points -= 1
            self.Hit = False
            if self.hit_points == 0:
                self.Dead = True


player = Player()
enemy = Enemy(Enemy.images_s, 100, 110, 10, 10, BLACK, 3, [50,  0, -60, 0])

while run:

    player.movement()
    player.draw()
    player.hits(enemy)

    enemy.appear()
    enemy.movement()
    enemy.hits()
    if not enemy.completely_dead:
        enemy.draw()

    if enemy.completely_dead:
        if player.score == 10:
            enemy = Enemy(Enemy.images_d, 100, 110, 20, 13, GREEN, 5, [60, -10, -30, 0])
        elif player.score == 30:
            enemy = Enemy(Enemy.images_r, 100, 110, 30, 15, RED, 10, [30,  -10, -50, 0])

    clock.tick(30)
    pygame.display.update()
