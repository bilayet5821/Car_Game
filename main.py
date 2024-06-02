import pygame
from pygame.locals import *
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WIDTH = 500
HEIGHT = 600
FPS = 90
ROAD_WIDTH = 300
MARKER_WIDTH = 10
MARKER_HEIGHT = 50
LEFT_LANE = 150
CENTER_LANE = 250
RIGHT_LANE = 350
LANES = [LEFT_LANE, CENTER_LANE, RIGHT_LANE]

# Colors
GRAY = (100, 100, 100)
GREEN = (76, 208, 56)
RED = (200, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 232, 0)
BLACK = (0, 0, 0)

# Load images
PLAYER_IMAGE = 'images/Audi.png'
VEHICLE_IMAGES = [
    'images/truck.png', 'images/Car.png', 'images/taxi.png',
    'images/Mini_van.png', 'images/Police.png', 'images/Mini_truck.png',
    'images/Black_viper.png', 'images/Ambulance.png'
]
CRASH_IMAGE = 'images/explosion1.png'

# Load sounds
SCORE_SOUND = 'sounds/score_increase.mp3'  
CRASH_SOUND = 'sounds/crash_sound.wav' 
BACKGROUND_MUSIC = 'sounds/background_music.mp3'  

# Initialize background music
pygame.mixer.music.load(BACKGROUND_MUSIC)
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1) 

# Sound effects
score_sound = pygame.mixer.Sound(SCORE_SOUND)
crash_sound = pygame.mixer.Sound(CRASH_SOUND)


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        image_scale = 70 / image.get_rect().width
        new_width = image.get_rect().width * image_scale
        new_height = image.get_rect().height * image_scale
        self.image = pygame.transform.scale(image, (new_width, new_height))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]


class PlayerVehicle(Vehicle):
    def __init__(self, x, y):
        image = pygame.image.load(PLAYER_IMAGE)
        super().__init__(image, x, y)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Car Driving ')
        self.clock = pygame.time.Clock()
        self.running = True
        self.gameover = False
        self.speed = 2
        self.score = 0
        self.lane_marker_move_y = 0
        self.font = pygame.font.Font(pygame.font.get_default_font(), 16)

        # Create sprite groups
        self.player_group = pygame.sprite.Group()
        self.vehicle_group = pygame.sprite.Group()

        # Create player
        self.player = PlayerVehicle(CENTER_LANE, HEIGHT - 100)
        self.player_group.add(self.player)

        # Load vehicle images
        self.vehicle_images = [pygame.image.load(image) for image in VEHICLE_IMAGES]

        # Load crash image
        self.crash = pygame.image.load(CRASH_IMAGE)
        self.crash_rect = self.crash.get_rect()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            if not self.gameover:
                self.update()
                self.draw()
            else:
                self.show_gameover()
            pygame.display.update()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            if event.type == KEYDOWN:
                if not self.gameover:
                    if event.key == K_LEFT and self.player.rect.center[0] > LEFT_LANE:
                        self.player.rect.x -= 100
                    elif event.key == K_RIGHT and self.player.rect.center[0] < RIGHT_LANE:
                        self.player.rect.x += 100

                    for vehicle in self.vehicle_group:
                        if pygame.sprite.collide_rect(self.player, vehicle):
                            self.gameover = True
                            crash_sound.play()  # Play crash sound when collision occurs
                            if event.key == K_LEFT:
                                self.player.rect.left = vehicle.rect.right
                                self.crash_rect.center = [self.player.rect.left, (self.player.rect.center[1] + vehicle.rect.center[1]) / 2]
                            elif event.key == K_RIGHT:
                                self.player.rect.right = vehicle.rect.left
                                self.crash_rect.center = [self.player.rect.right, (self.player.rect.center[1] + vehicle.rect.center[1]) / 2]
                else:
                    if event.key == K_y:
                        self.reset()
                    elif event.key == K_n:
                        self.running = False

    def update(self):
        self.lane_marker_move_y += self.speed * 2
        if self.lane_marker_move_y >= MARKER_HEIGHT * 2:
            self.lane_marker_move_y = 0

        if len(self.vehicle_group) < 2:
            add_vehicle = True
            for vehicle in self.vehicle_group:
                if vehicle.rect.top < vehicle.rect.height * 1.5:
                    add_vehicle = False
            if add_vehicle:
                lane = random.choice(LANES)
                image = random.choice(self.vehicle_images)
                vehicle = Vehicle(image, lane, HEIGHT / -2)
                self.vehicle_group.add(vehicle)

        for vehicle in self.vehicle_group:
            vehicle.rect.y += self.speed
            if vehicle.rect.top >= HEIGHT:
                vehicle.kill()
                self.score += 1
                score_sound.play()  # Play score sound when score increases
                if self.score > 0 and self.score % 5 == 0:
                    self.speed += 1

        if pygame.sprite.spritecollide(self.player, self.vehicle_group, True):
            self.gameover = True
            crash_sound.play()  # Play crash sound when collision occurs
            self.crash_rect.center = [self.player.rect.center[0], self.player.rect.top]

    def draw(self):
        self.screen.fill(GREEN)
        pygame.draw.rect(self.screen, GRAY, (100, 0, ROAD_WIDTH, HEIGHT))
        pygame.draw.rect(self.screen, YELLOW, (95, 0, MARKER_WIDTH, HEIGHT))
        pygame.draw.rect(self.screen, YELLOW, (395, 0, MARKER_WIDTH, HEIGHT))

        for y in range(MARKER_HEIGHT * -2, HEIGHT, MARKER_HEIGHT * 2):
            pygame.draw.rect(self.screen, WHITE, (LEFT_LANE + 45, y + self.lane_marker_move_y, MARKER_WIDTH, MARKER_HEIGHT))
            pygame.draw.rect(self.screen, WHITE, (CENTER_LANE + 45, y + self.lane_marker_move_y, MARKER_WIDTH, MARKER_HEIGHT))

        self.player_group.draw(self.screen)
        self.vehicle_group.draw(self.screen)

        score_text = self.font.render('Score: ' + str(self.score), True, BLACK)
        score_rect = score_text.get_rect()
        score_rect.center = (50, 400)
        self.screen.blit(score_text, score_rect)

    def show_gameover(self):
        self.screen.blit(self.crash, self.crash_rect)
        pygame.draw.rect(self.screen, RED, (0, 50, WIDTH, 100))
        gameover_text = self.font.render('Game over. Play again? (Enter Y or N)', True, WHITE)
        gameover_rect = gameover_text.get_rect()
        gameover_rect.center = (WIDTH / 2, 100)
        self.screen.blit(gameover_text, gameover_rect)

    def reset(self):
        self.gameover = False
        self.speed = 2
        self.score = 0
        self.vehicle_group.empty()
        self.player.rect.center = [CENTER_LANE, HEIGHT - 100]


if __name__ == "__main__":
    game = Game()
    game.run()
