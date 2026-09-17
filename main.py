import os.path
import time
import pickle
import pygame
import pygame.gfxdraw
import math
import neat
from os import listdir
# import custom_genome
import neat.checkpoint
from ui import *
import re

pygame.init()

print("Program Started")
screen_width = 1500
screen_height = 750
menu_colour = (10, 200, 20)
grass_colour = (10, 200, 20)
road_colour = (81, 84, 90)
win = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Car Game")

clock = pygame.time.Clock()

start_pos = (100, 100)
start_rot = 0.75
outer_track = [(50, 50), (600, 50), (1200, 100), (1450, 250), (1450, 600), (1000, 700), (500, 400), (200, 650), (50, 650)]
inner_track = [(150, 150), (600, 150), (1200, 200), (1350, 300), (1350, 500), (1000, 600), (500, 300), (200, 550), (150, 550)]
all_tracks = [inner_track, outer_track]

reward_gates = [((200, 25), (200, 175)), ((600, 25), (600, 175)), ((1200, 75), (1200, 225)), ((1300, 125), (1300, 300)),
                ((1325, 300), (1475, 225)), ((1325, 400), (1475, 400)), ((1325, 475), (1475, 625)),
                ((1200, 525), (1200, 675)), ((1000, 575), (1000, 725)), ((750, 425), (750, 575)), ((500, 275), (500, 425)),
                ((425, 325), (425, 500)), ((300, 450), (300, 600)), ((25, 675), (175, 525)), ((25, 230), (175, 230)),
                ((25, 210), (175, 210)), ((25, 190), (175, 190)), ((25, 170), (175, 170)), ((25, 150), (175, 150))]
path_points = [((point[0][0] + point[1][0]) / 2, (point[0][1] + point[1][1]) / 2) for point in reward_gates]

home_buttons = [Button(400, 50, 300, 100, "train", text="TRAIN AI", font_size=50),
                     Button(800, 50, 300, 100, "play", text="PLAY GAME", font_size=50),
                     Button(400, 200, 300, 100, "replay_model", text="REPLAY MODEL", font_size=40),
                     Button(800, 200, 300, 100, "replay_checkpoint", text="REPLAY CHECKPOINT", font_size=30),
                     Button(400, 350, 300, 100, "edit_level", text="LEVEL EDITOR", font_size=40),
                     Button(800, 350, 300, 100, "save", text="SAVE MODEL FROM CHECKPOINT", font_size=19),
                     Button(400, 500, 300, 100, "mass_save_models", text="MASS SAVE MODELS", font_size=30),
                     Button(800, 500, 300, 100, "mass_replay_models", text="MASS REPLAY MODELS", font_size=19),
                     Button(600, 650, 100, 30, "quit", text="QUIT", font_size=20),
                     Button(800, 650, 100, 30, "open_menu_settings", text="SETTINGS", font_size=20)]
home_settings_text = [Text(100, 65, "Save checkpoints:"), Text(100, 90, "Yes", code="save_checkpoints"),
                      Text(100, 140, "Load checkpoints:"), Text(100, 165, "Yes", code="load_checkpoints"),
                      Text(100, 215, "Save best model:"), Text(100, 240, "Yes", code="save_best"),
                      Text(100, 315, "Max gen time:"), Text(100, 405, "Fitness cutoff time:"),
                      Text(100, 495, "Max gen frames:"), Text(850, 65, "Checkpoint prefix:"),
                      Text(850, 155, "Checkpoint path:"), Text(850, 245, "Model path:"),
                      Text(100, 585, "Training generations:"), Text(100, 675, "Checkpoint interval:")]
home_settings_buttons = [Button(25, 25, 100, 30, "close_menu_settings", text="Close", font_size=20),
                         Button(200, 50, 100, 30, "save_checkpoints", text="Yes", font_size=20),
                         Button(350, 50, 100, 30, "no_save_checkpoints", text="No", font_size=20),
                         Button(200, 125, 100, 30, "load_checkpoints", text="Yes", font_size=20),
                         Button(350, 125, 100, 30, "no_load_checkpoints", text="No", font_size=20),
                         Button(200, 200, 100, 30, "save_best", text="Yes", font_size=20),
                         Button(350, 200, 100, 30, "no_save_best", text="No", font_size=20)]
home_settings_textboxes = [TextBox(200, 280, 250, 60, code="max_gen_time"),
                           TextBox(200, 370, 250, 60, code="fitness_cutoff_time"),
                           TextBox(200, 460, 250, 60, code="max_gen_frames"),
                           TextBox(200, 550, 250, 60, code="training_generations"),
                           TextBox(200, 640, 250, 60, code="checkpoint_interval"),
                           TextBox(950, 35, 250, 60, code="checkpoint_prefix", font_size=15),
                           TextBox(950, 125, 250, 60, code="checkpoint_path", font_size=15),
                           TextBox(950, 205, 250, 60, code="model_path", font_size=15)]

game_text = [Text(screen_width / 2, 20, "Generation: 0", code="generation"),
             Text(screen_width / 2 - 400, 20, "Players: 1", code="players"),
             Text(screen_width / 2 + 400, 20, "Best fitness: 0", code="max_fitness")]
game_buttons = [Button(25, 25, 100, 30, "toggle_game_settings", text="Settings", font_size=20)]
game_settings_text = [Text(75, 165, "FPS:"), Text(75, 240, "Draw cars:"),
                 Text(75, 315, "Draw rays:"), Text(75, 390, "Draw hitbox:"),
                 Text(75, 465, "Draw collisions:"), Text(75, 540, "Draw gates:"),
                 Text(75, 615, "Draw track:"), Text(850, 165, "Max gen time:"),
                 Text(850, 255, "Fitness cutoff time:")]
game_settings_buttons = [Button(150, 150, 50, 30, "fps15", text="15", font_size=20),
                         Button(225, 150, 50, 30, "fps30", text="30", font_size=20),
                         Button(300, 150, 50, 30, "fps60", text="60", font_size=20),
                         Button(375, 150, 50, 30, "fps120", text="120", font_size=20),
                         Button(450, 150, 50, 30, "fps_max", text="Max", font_size=20),
                         Button(150, 225, 100, 30, "draw_cars", text="Yes", font_size=20),
                         Button(300, 225, 100, 30, "no_draw_cars", text="No", font_size=20),
                         Button(150, 300, 100, 30, "draw_rays", text="Yes", font_size=20),
                         Button(300, 300, 100, 30, "no_draw_rays", text="No", font_size=20),
                         Button(150, 375, 100, 30, "draw_hitbox", text="Yes", font_size=20),
                         Button(300, 375, 100, 30, "no_draw_hitbox", text="No", font_size=20),
                         Button(150, 450, 100, 30, "draw_ray_collisions", text="Yes", font_size=20),
                         Button(300, 450, 100, 30, "no_draw_ray_collisions", text="No", font_size=20),
                         Button(150, 525, 100, 30, "draw_reward_gates", text="Yes", font_size=20),
                         Button(300, 525, 100, 30, "no_draw_reward_gates", text="No", font_size=20),
                         Button(150, 600, 100, 30, "draw_track", text="Yes", font_size=20),
                         Button(300, 600, 100, 30, "no_draw_track", text="No", font_size=20),
                         Button(1250, 150, 100, 30, "apply_max_gen_time", text="Apply", font_size=20),
                         Button(1250, 240, 100, 30, "apply_fitness_cutoff_time", text="Apply", font_size=20)]
game_settings_textboxes = [TextBox(950, 135, 250, 60, code="max_gen_time"),
                           TextBox(950, 225, 250, 60, code="fitness_cutoff_time")]

edit_text = [Text(1250, 40, "Level name:"), Text(1250, 75, "Player rotation:")]
edit_buttons = [Button(150, 25, 100, 30, "save_level", text="Save level", font_size=20),
                Button(150, 60, 100, 30, "load_level", text="Load level", font_size=20),
                Button(275, 25, 100, 30, "delete_outer", text="Delete outer track", font_size=12),
                Button(400, 25, 100, 30, "draw_outer_track", text="Draw outer track", font_size=12),
                Button(275, 60, 100, 30, "delete_inner", text="Delete inner track", font_size=12),
                Button(400, 60, 100, 30, "draw_inner_track", text="Draw inner track", font_size=12),
                Button(900, 25, 100, 30, "delete_gates", text="Delete reward gates", font_size=11),
                Button(900, 60, 100, 30, "draw_gates", text="Draw reward gates", font_size=12),
                Button(25, 60, 100, 30, "change_start_pos", text="Change start pos", font_size=12),
                Button(650, 25, 100, 30, "delete_outer_point", text="Remove outer point", font_size=12),
                Button(525, 25, 100, 30, "add_outer_point", text="Add outer point", font_size=12),
                Button(650, 60, 100, 30, "delete_inner_point", text="Remove inner point", font_size=12),
                Button(775, 25, 100, 30, "move_outer_point", text="Move outer point", font_size=12),
                Button(775, 60, 100, 30, "move_inner_point", text="Move inner point", font_size=12),
                Button(525, 60, 100, 30, "add_inner_point", text="Add inner point", font_size=12),
                Button(1025, 25, 100, 30, "deselect", text="Deselect", font_size=20),
                Button(1025, 60, 100, 30, "move_pointer", text="Move pointer", font_size=16)]
edit_textboxes = [TextBox(1325, 25, 150, 30, code="level_name", font_size=14),
                  TextBox(1325, 60, 150, 30, code="start_rot", font_size=14)]

# ray_offsets = [(0, -120), (0, -300), (50, -100), (100, 0), (0, 120), (-100, 0), (-50, -100)]
ray_offsets = [(0, -400), (80, -220), (120, -120), (200, 0), (120, 120), (0, 200), (-120, 120), (-200, 0), (-120, -120), (-80, -220)]

play_fps = 30
train_fps = -1

fps = -1
GEN = 0

is_in_menu = True
is_left_clicking = False
game_settings_open = False
menu_settings_open = False

# Defines the variables for the fitness function
gate_reward = 100
death_penalty = 0
dist_reward_multiplier = 0
path_point_dist_penalty_multiplier = 0.1
backwards_penalty = -0.01
turn_penalty = -0.001

max_gen_time = 60
max_gen_frames = 360 * 60
fitness_cutoff_time = 10
cutoff_penalty = -20
fitness_cutoff_threshold = gate_reward / 2

player_playing = False
editing_level = False
exit_training = False
edit_mode = ""

replay_best = True
save_best = False
save_checkpoints = False
load_checkpoints = True
save_checkpoint_to_model = False

generations = 500
checkpoint_interval = 1

checkpoint_prefix = "checkpoints/neat-checkpoint"
checkpoint_path = checkpoint_prefix + "0"
saved_model_path = "player-model-fast.pickle"
levels_path = "levels.txt"
level_name = "Edited track"

# Defines boolean variables for drawing various aspects of the scene to the screen
draw_player = True
draw_car = True
draw_hitbox = False
draw_rays = False
draw_ray_collisions = False
draw_reward_gates = True
draw_track = True


class Car():

    def __init__(self, x, y, rotation=0):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 60

        self.vel = 0
        self.x_vel = 0
        self.y_vel = 0
        self.acc = 0

        self.max_vel = 5
        self.friction = 0.9
        self.vel_strength = 1
        self.drift_friction = 0.9
        self.drift_strength = 0.4

        self.forward_acc = 1
        self.backward_acc = 0.4

        self.rotation = rotation % 1
        self.turn_strength = 0.006

        self.centre = (self.x, self.y)

        self.image = pygame.transform.rotozoom(pygame.image.load("TopDownCar.png"), self.rotation * 360, 0.2)
        self.rect = self.image.get_rect(center = self.centre)

        self.x1 = self.x - self.width / 2
        self.y1 = self.y - self.height / 2
        self.x2 = self.x + self.width / 2
        self.y2 = self.y + self.height / 2

        self.point1 = (self.x1, self.y1)
        self.point2 = (self.x1, self.y2)
        self.point3 = (self.x2, self.y2)
        self.point4 = (self.x2, self.y1)

        self.point1 = rotate_point(self.point1, self.centre, -math.radians(self.rotation * 360))
        self.point2 = rotate_point(self.point2, self.centre, -math.radians(self.rotation * 360))
        self.point3 = rotate_point(self.point3, self.centre, -math.radians(self.rotation * 360))
        self.point4 = rotate_point(self.point4, self.centre, -math.radians(self.rotation * 360))

        self.lines = [(self.point1, self.point2), (self.point2, self.point3), (self.point3, self.point4), (self.point4, self.point1)]

        self.ray_points = []
        for offset in ray_offsets:
            x_pos = self.x + offset[0]
            y_pos = self.y + offset[1]

            x_pos, y_pos = rotate_point((x_pos, y_pos), self.centre, -math.radians(self.rotation * 360))

            self.ray_points.append((x_pos, y_pos))

        self.target_gate = 0
        self.total_gates = len(reward_gates)

    def turn(self, direction):
        self.rotation += direction * self.turn_strength * self.vel

    def accelerate(self, direction):
        if direction > 0:
            self.acc = direction * self.forward_acc
        else:
            self.acc = direction * self.backward_acc

    def update(self):
        self.rotation = self.rotation % 1

        self.x_vel += self.acc * math.sin(self.rotation * math.pi * 2)
        self.y_vel += self.acc * math.cos(self.rotation * math.pi * 2)
        self.vel += self.acc

        self.x_vel *= self.drift_friction
        self.y_vel *= self.drift_friction
        self.vel *= self.friction

        if self.vel > self.max_vel:
            self.vel = self.max_vel
        elif self.vel < -self.max_vel:
            self.vel = -self.max_vel

        self.x -= self.vel * self.vel_strength * math.sin(self.rotation * math.pi * 2) + self.x_vel * self.drift_strength
        self.y -= self.vel * self.vel_strength * math.cos(self.rotation * math.pi * 2) + self.y_vel * self.drift_strength

        self.centre = (self.x, self.y)

        self.x1 = self.x - self.width / 2
        self.y1 = self.y - self.height / 2
        self.x2 = self.x + self.width / 2
        self.y2 = self.y + self.height / 2

        self.point1 = (self.x1, self.y1)
        self.point2 = (self.x1, self.y2)
        self.point3 = (self.x2, self.y2)
        self.point4 = (self.x2, self.y1)

        self.point1 = rotate_point(self.point1, self.centre, -math.radians(self.rotation * 360))
        self.point2 = rotate_point(self.point2, self.centre, -math.radians(self.rotation * 360))
        self.point3 = rotate_point(self.point3, self.centre, -math.radians(self.rotation * 360))
        self.point4 = rotate_point(self.point4, self.centre, -math.radians(self.rotation * 360))

        self.lines = [(self.point1, self.point2), (self.point2, self.point3), (self.point3, self.point4),
                      (self.point4, self.point1)]

        self.ray_points = []
        for offset in ray_offsets:
            x_pos = self.x + offset[0]
            y_pos = self.y + offset[1]

            x_pos, y_pos = rotate_point((x_pos, y_pos), self.centre, -math.radians(self.rotation * 360))

            self.ray_points.append((x_pos, y_pos))

    def draw(self, win, draw_car=draw_car, draw_hitbox=draw_hitbox, draw_rays=draw_rays):
        self.image = pygame.transform.rotozoom(pygame.image.load("TopDownCar.png"), self.rotation * 360, 0.2)
        self.rect = self.image.get_rect(center=(self.x, self.y))

        if draw_car:
            win.blit(self.image, self.rect)

        # Draws the player's collision box if draw_hitbox is True
        if draw_hitbox:
            pygame.draw.line(win, (0, 0, 0), self.point1, self.point2)
            pygame.draw.line(win, (0, 0, 0), self.point2, self.point3)
            pygame.draw.line(win, (0, 0, 0), self.point3, self.point4)
            pygame.draw.line(win, (0, 0, 0), self.point4, self.point1)

        # Draws the rays which the player uses to see if draw_rays is True
        if draw_rays:
            for point in self.ray_points:
                pygame.draw.line(win, (0, 0, 0), self.centre, point)

    def find_dists(self, tracks, win=win, draw_ray_collisions=draw_ray_collisions):
        dists = []

        for i in range(len(ray_offsets)):
            dists.append(0)

        for track in tracks:
            for i in range(len(track)):
                for j, ray_point in enumerate(self.ray_points):
                    intersection = find_intersection(self.centre, ray_point, track[i], track[(i + 1) % len(track)])
                    if (intersection != False):
                        dist = math.sqrt((intersection[0] - self.x) ** 2 + (intersection[1] - self.y) ** 2)
                        if (dist < dists[j] or dists[j] == 0):
                            dists[j] = dist

                        if draw_ray_collisions:
                            pygame.draw.circle(win, (255, 0, 0), intersection, 10)

        for i, dist in enumerate(dists):
            dists[i] = dist / math.sqrt(ray_offsets[i][0] ** 2 + ray_offsets[i][1] ** 2)

            if (not dists[i] == 0):
                dists[i] = 1 - dists[i]

        return dists

    def die(self):
        self = None


def find_intersection(p1, p2, p3, p4):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    if (max(x1, x2) < min(x3, x4)):
        return False

    if (x2 == x1):
        x1 += 1
    if (x3 == x4):
        x3 += 1

    m1 = (y2 - y1) / (x2 - x1)
    m2 = (y4 - y3) / (x4 - x3)

    b1 = y1 - m1 * x1
    b2 = y3 - m2 * x3

    if (m1 == m2):
        return False

    xa = (b2 - b1) / (m1 - m2)

    if (xa < max(min(x1, x2), min(x3, x4)) or xa > min(max(x1, x2), max(x3, x4))):
        return False

    ya = m2 * xa + b2

    return (xa, ya)

def rotate_point(point, origin, angle):
    pointX, pointY = point
    originX, originY = origin

    newX = originX + math.cos(angle) * (pointX - originX) - math.sin(angle) * (pointY - originY)
    newY = originY + math.sin(angle) * (pointX - originX) + math.cos(angle) * (pointY - originY)

    return newX, newY

def load_level(level_name):
    with open("levels.txt", "r") as f:
        levels = f.read()

    levels_arr = levels.split('\n\n')
    current_level = None
    for i, level in enumerate(levels_arr[:-1]):
        this_level_name = level.split('\n')[0].split(': ')[1]
        if this_level_name == level_name:
            current_level = level

    if current_level is None:
        print("WARNING: No level with name '" + level_name + "' exists. Are you sure it's correct?")

        return None
    else:
        outer_track = []
        inner_track = []
        reward_gates = []

        encoded_outer_track = current_level.split('\n')[1].split(' ')
        if encoded_outer_track[1] != '':
            outer_track = [(int(point.split(',')[0]), int(point.split(',')[1])) for point in
                           encoded_outer_track[1:]]

        encoded_inner_track = current_level.split('\n')[2].split(' ')
        if encoded_inner_track[1] != '':
            inner_track = [(int(point.split(',')[0]), int(point.split(',')[1])) for point in
                           encoded_inner_track[1:]]

        encoded_reward_gates = current_level.split('\n')[3].split(' ')
        if encoded_reward_gates[1] != '':
            reward_gates = [
                ((int(point.split(',')[0]), int(point.split(',')[1])), (int(point.split(',')[2]), int(point.split(',')[3])))
                for point in encoded_reward_gates[1:]]

        start_pos = (int(current_level.split('\n')[4].split(' ')[1].split(',')[0]),
                     int(current_level.split('\n')[4].split(' ')[1].split(',')[1]))
        start_rot = float(current_level.split('\n')[5].split(' ')[1])

        return outer_track, inner_track, reward_gates, start_pos, start_rot


def main(genomes, config):
    global GEN
    global fps
    global exit_training
    global player_playing
    global editing_level
    global edit_mode
    global game_settings_open
    global menu_settings_open
    global is_left_clicking
    global draw_car
    global draw_rays
    global draw_hitbox
    global draw_ray_collisions
    global draw_reward_gates
    global draw_track
    global max_gen_time
    global fitness_cutoff_time
    global level_name
    global outer_track
    global inner_track
    global reward_gates

    is_left_clicking = False
    is_right_clicking = False

    best_fitness = 0
    frames_passed = 0

    game_paused = False
    draw_buttons = True

    gate_point_1 = None
    gate_point_2 = None
    pointer_pos = (screen_width / 2, screen_height / 2)

    GEN += 1

    if load_level(level_name) is not None:
        outer_track, inner_track, reward_gates, start_pos, start_rot = load_level(level_name)

    nets = []
    ge = []
    players = []

    if player_playing and not editing_level:
        players.append(Car(start_pos[0], start_pos[1], start_rot))
    elif not editing_level:
        for _, g in genomes:
            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            players.append(Car(start_pos[0], start_pos[1], start_rot))
            g.fitness = 0
            ge.append(g)

    all_textboxes = []
    all_textboxes += home_settings_textboxes
    all_textboxes += game_settings_textboxes
    all_textboxes += edit_textboxes

    for textbox in all_textboxes:
        match textbox.code:
            case "level_name":
                textbox.text = level_name
            case "start_rot":
                textbox.text = str(start_rot)

    is_running = True
    start_time = time.time()

    while is_running:
        events = pygame.event.get()

        user_input = ""
        hit_backspace = False
        interacting_with_ui = False
        just_left_clicked  = False
        just_right_clicked = False

        if draw_track:
            if len(outer_track) > 2:
                pygame.gfxdraw.filled_polygon(win, outer_track, road_colour)
            if len(inner_track) > 2:
                pygame.gfxdraw.filled_polygon(win, inner_track, grass_colour)

        if exit_training:
            break

        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        # Checks if the player quit the program
        for event in events:
            if event.type == pygame.QUIT:
                is_running = False
                print("Program Ended")
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    is_left_clicking = True
                    just_left_clicked = True
                elif event.button == 3:
                    is_right_clicking = True
                    just_right_clicked = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_left_clicking = False
                elif event.button == 3:
                    is_right_clicking = False
            elif event.type == pygame.KEYDOWN:
                user_input += event.unicode
                if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    user_input.upper()
                elif event.key == pygame.K_BACKSPACE:
                    hit_backspace = True
                elif event.key == pygame.K_k:
                    game_paused = not game_paused
                elif event.key == pygame.K_b:
                    draw_buttons = not draw_buttons
                elif event.key == pygame.K_SPACE and not player_playing and not editing_level:
                    for i, g in enumerate(ge):
                        dist = math.sqrt((players[i].x - start_pos[0]) ** 2 + (players[i].y - start_pos[1]) ** 2)
                        ge[j].fitness += dist * dist_reward_multiplier

                        point_dist = math.sqrt(
                            (player.x - path_points[(player.target_gate) % len(path_points)][0]) ** 2 +
                            (player.y - path_points[(player.target_gate) % len(path_points)][1]) ** 2)
                        ge[j].fitness -= dist * path_point_dist_penalty_multiplier

                    players = []
                    ge = []
                    nets = []


        if keys[pygame.K_ESCAPE]:
            is_running = False
            exit_training = True

        if player_playing:
            if draw_ray_collisions:
                player.find_dists([outer_track, inner_track], draw_ray_collisions=draw_ray_collisions)

            if keys[pygame.K_SPACE]:
                players[0] = Car(start_pos[0], start_pos[1], start_rot)

            if keys[pygame.K_w]:
                players[0].accelerate(1)
            elif keys[pygame.K_s]:
                players[0].accelerate(-1)
            else:
                players[0].accelerate(0)

            if not game_paused:
                if keys[pygame.K_d]:
                    players[0].turn(-1)
                if keys[pygame.K_a]:
                    players[0].turn(1)
        elif not editing_level:
            if keys[pygame.K_TAB]:
                print("Program Ended")
                pygame.quit()
                quit()

            if not game_paused:
                for i, player in enumerate(players):
                    inputs = player.find_dists([outer_track, inner_track], draw_ray_collisions=draw_ray_collisions)
                    inputs += [player.vel]
                    output = nets[i].activate(inputs)

                    player_turn = 0
                    player_acc = 0
                    if (output[0] > 0.5):
                        player_acc += 1
                    if (output[1] > 0.5):
                        player_acc -= 1
                        ge[i].fitness += backwards_penalty
                    if (output[2] > 0.5):
                        player_turn += 1
                        ge[i].fitness += turn_penalty
                    if (output[3] > 0.5):
                        player_turn -= 1
                        ge[i].fitness += turn_penalty

                    player.turn(player_turn)
                    player.accelerate(player_acc)

        # pygame.draw.circle(win, (255, 255, 255), (screen_width / 2, screen_height / 2), 10)

        if not game_paused:
            for player in players:
                player.update()

        for i in range(len(outer_track)):
            if draw_track:
                pygame.draw.line(win, (0, 0, 0), outer_track[i], outer_track[(i+1)%len(outer_track)])

            if not editing_level:
                for j, player in enumerate(players):
                    for player_line in player.lines:
                        if (find_intersection(player_line[0], player_line[1], outer_track[i],
                                              outer_track[(i + 1) % len(outer_track)]) != False):
                            if player_playing:
                                players[0] = Car(start_pos[0], start_pos[1], start_rot)
                            else:
                                dist = math.sqrt((player.x - start_pos[0]) ** 2 + (player.y - start_pos[1]) ** 2)
                                ge[j].fitness += dist * dist_reward_multiplier

                                point_dist = math.sqrt((player.x - path_points[(player.target_gate) % len(path_points)][0]) ** 2 +
                                                       (player.y - path_points[(player.target_gate) % len(path_points)][1]) ** 2)
                                ge[j].fitness -= dist * path_point_dist_penalty_multiplier

                                ge[j].fitness += death_penalty
                                players.pop(j)
                                nets.pop(j)
                                ge.pop(j)
                                break
                            # player.die()

        for i in range(len(inner_track)):
            if draw_track:
                pygame.draw.line(win, (0, 0, 0), inner_track[i], inner_track[(i+1)%len(inner_track)])

            if not editing_level:
                for j, player in enumerate(players):
                    for player_line in player.lines:
                        if (find_intersection(player_line[0], player_line[1], inner_track[i],
                                              inner_track[(i + 1) % len(inner_track)]) != False):
                            if player_playing:
                                players[0] = Car(start_pos[0], start_pos[1], start_rot)
                            else:
                                dist = math.sqrt((player.x - start_pos[0]) ** 2 + (player.y - start_pos[1]) ** 2)
                                ge[j].fitness += dist * dist_reward_multiplier

                                point_dist = math.sqrt(
                                    (player.x - path_points[(player.target_gate) % len(path_points)][0]) ** 2 +
                                    (player.y - path_points[(player.target_gate) % len(path_points)][1]) ** 2)
                                ge[j].fitness -= dist * path_point_dist_penalty_multiplier

                                ge[j].fitness += death_penalty
                                players.pop(j)
                                nets.pop(j)
                                ge.pop(j)
                                break

        gate_intersections = []
        for i, gate in enumerate(reward_gates):
            if draw_reward_gates:
                pygame.draw.line(win, (255, 255, (i % 2) * 255), gate[0], gate[1])

            if not player_playing and not editing_level:
                gate_intersections.append([])

                for j, player in enumerate(players):
                    gate_intersections[i].append(False)

                    for line in player.lines:
                        intersection = find_intersection(gate[0], gate[1], line[0], line[1])
                        if (intersection != False):
                            gate_intersections[i][j] = True
                            break

        if not player_playing and not editing_level:
            for i, row in enumerate(gate_intersections):
                for j, intersection in enumerate(row):
                    if intersection:
                        if (i == players[j].target_gate):
                            ge[j].fitness += gate_reward
                            players[j].target_gate = (players[j].target_gate + 1) % players[j].total_gates
                            break

        if draw_player and (draw_car or draw_hitbox or draw_rays):
            for player in players:
                player.draw(win, draw_car=draw_car, draw_hitbox=draw_hitbox, draw_rays=draw_rays)

        visible_text = []
        visible_buttons = []
        visible_textboxes = []

        visible_buttons += game_buttons
        visible_text += game_text
        if game_settings_open:
            visible_text += game_settings_text
            visible_buttons += game_settings_buttons
            visible_textboxes += game_settings_textboxes
        elif menu_settings_open:
            visible_text += home_settings_text
            visible_buttons += home_settings_buttons
            visible_textboxes += home_settings_textboxes
        if editing_level:
            visible_text += edit_text
            visible_buttons += edit_buttons
            visible_textboxes += edit_textboxes

        for button in visible_buttons:
            if just_left_clicked:
                if button.x < mouse_pos[0] < button.x + button.w:
                    if button.y < mouse_pos[1] < button.y + button.h:
                        interacting_with_ui = True
                        button_code = button.code

                        match button_code:
                            case "toggle_game_settings":
                                game_settings_open = not game_settings_open
                                if game_settings_open:
                                    for textbox in all_textboxes:
                                        box_code = textbox.code

                                        match box_code:
                                            case "max_gen_time":
                                                textbox.text = str(max_gen_time)
                                            case "fitness_cutoff_time":
                                                textbox.text = str(fitness_cutoff_time)
                                            case "max_gen_frames":
                                                textbox.text = str(max_gen_frames)
                            case "close_game_settings":
                                game_settings_open = False
                            case "open_menu_settings":
                                menu_settings_open = True
                            case "close_menu_settings":
                                menu_settings_open = False
                            case "fps15":
                                fps = 15
                            case "fps30":
                                fps = 30
                            case "fps60":
                                fps = 60
                            case "fps120":
                                fps = 120
                            case "fps_max":
                                fps = -1
                            case "draw_cars":
                                draw_car = True
                            case "no_draw_cars":
                                draw_car = False
                            case "draw_rays":
                                draw_rays = True
                            case "no_draw_rays":
                                draw_rays = False
                            case "draw_hitbox":
                                draw_hitbox = True
                            case "no_draw_hitbox":
                                draw_hitbox = False
                            case "draw_ray_collisions":
                                draw_ray_collisions = True
                            case "no_draw_ray_collisions":
                                draw_ray_collisions = False
                            case "draw_reward_gates":
                                draw_reward_gates = True
                            case "no_draw_reward_gates":
                                draw_reward_gates = False
                            case "draw_track":
                                draw_track = True
                            case "no_draw_track":
                                draw_track = False
                            case "apply_max_gen_time":
                                for textbox in game_settings_textboxes:
                                    if textbox.code == "max_gen_time":
                                        try:
                                            max_gen_time = float(textbox.text)
                                        except ValueError:
                                            pass
                            case "apply_fitness_cutoff_time":
                                for textbox in game_settings_textboxes:
                                    if textbox.code == "fitness_cutoff_time":
                                        try:
                                            fitness_cutoff_time = float(textbox.text)
                                        except ValueError:
                                            pass
                            case "save_level":
                                encoded_level = "NAME: " + level_name

                                encoded_level += "\nOUTER_TRACK: "
                                encoded_level += ' '.join(
                                    [str(point).replace(" ", "").replace("(", "").replace(")", "")
                                     for point in outer_track])

                                encoded_level += "\nINNER_TRACK: "
                                encoded_level += ' '.join(
                                    [str(point).replace(" ", "").replace("(", "").replace(")", "")
                                     for point in inner_track])

                                encoded_level += "\nREWARD_GATES: "
                                encoded_level += ' '.join(
                                    [str(point).replace(" ", "").replace("(", "").replace(")", "")
                                     for point in reward_gates])

                                encoded_level += "\nSTART_POS: " + str(start_pos).replace(" ", "").replace("(", "").replace(")", "")
                                encoded_level += "\nSTART_ROT: " + str(start_rot)

                                encoded_level += "\n\n"

                                with open("levels.txt", "r") as f:
                                    levels = f.read()

                                levels_arr = levels.split('\n\n')
                                level_index = -1
                                for i, level in enumerate(levels_arr[:-1]):
                                    this_level_name = level.split('\n')[0].split(': ')[1]
                                    if this_level_name == level_name:
                                        level_index = i

                                if level_index == -1:
                                    with open("levels.txt", "a") as f:
                                        f.write(encoded_level)

                                    print("Added new level")
                                else:
                                    levels_arr[level_index] = encoded_level[:-2]
                                    updated_levels = "\n\n".join(levels_arr)

                                    with open("levels.txt", "w") as f:
                                        f.write(updated_levels)

                                    print("Overwrote level")
                            case "load_level":
                                if load_level(level_name) is not None:
                                    outer_track, inner_track, reward_gates, start_pos, start_rot = load_level(
                                        level_name)

                                for textbox in all_textboxes:
                                    match textbox.code:
                                        case "start_rot":
                                            textbox.text = str(start_rot)
                            case "delete_outer":
                                outer_track = []
                            case "draw_outer_track":
                                edit_mode = "draw_outer_track"
                            case "delete_inner":
                                inner_track = []
                            case "draw_inner_track":
                                edit_mode = "draw_inner_track"
                            case "delete_gates":
                                reward_gates = []
                            case "draw_gates":
                                edit_mode = "draw_gates"
                            case "change_start_pos":
                                edit_mode = "change_start_pos"
                            case "deselect":
                                edit_mode = ""
                                gate_point_1 = None
                                gate_point_2 = None
                            case "delete_outer_point":
                                edit_mode = "delete_outer_point"
                            case "add_outer_point":
                                edit_mode = "add_outer_point"
                            case "delete_inner_point":
                                edit_mode = "delete_inner_point"
                            case "add_inner_point":
                                edit_mode = "add_inner_point"
                            case "move_outer_point":
                                edit_mode = "move_outer_point"
                            case "move_inner_point":
                                edit_mode = "move_inner_point"
                            case "move_pointer":
                                edit_mode = "move_pointer"
                            case _:
                                print("WARNING: Button code '" + button_code + "' is not recognized. Are you sure it's correct?")

            if draw_buttons:
                button.draw(win, mouse_pos, is_left_clicking)

        for text in visible_text:
            text_code = text.code
            match text_code:
                case "generation":
                    text.text = "Generation: " + str(GEN)
                case "players":
                    text.text = "Players: " + str(len(players))
                case "max_fitness":
                    max_fitness = 0
                    for g in ge:
                        if g.fitness > max_fitness:
                            max_fitness = g.fitness

                    text.text = "Best fitness: " + str(round(max_fitness * 10) / 10)

            text.draw(win)

        for textbox in visible_textboxes:
            if textbox.x < mouse_pos[0] < textbox.x + textbox.w:
                if textbox.y < mouse_pos[1] < textbox.y + textbox.h:
                    interacting_with_ui = True
                    box_code = textbox.code

                    match box_code:
                        case "max_gen_time":
                            if user_input.isnumeric() or user_input in ['.', '-']:
                                textbox.text += user_input
                            if hit_backspace:
                                textbox.text = textbox.text[:-1]
                        case "fitness_cutoff_time":
                            if user_input.isnumeric() or user_input in ['.', '-']:
                                textbox.text += user_input
                            if hit_backspace:
                                textbox.text = textbox.text[:-1]
                        case "max_gen_frames":
                            if user_input.isnumeric() or user_input in ['.', '-']:
                                textbox.text += user_input
                            if hit_backspace:
                                textbox.text = textbox.text[:-1]
                        case "level_name":
                            if hit_backspace:
                                level_name = level_name[:-1]
                            elif ':' not in user_input and '\\' not in user_input and user_input.isprintable():
                                level_name += str(user_input)

                                textbox.text = level_name
                        case "start_rot":
                            if user_input.isnumeric() or user_input in ['.', '-']:
                                textbox.text += user_input
                            if hit_backspace:
                                textbox.text = textbox.text[:-1]

                            try:
                                start_rot = float(textbox.text)
                            except ValueError:
                                pass

            textbox.draw(win)

        if editing_level:
            pygame.draw.circle(win, (255, 0, 0), start_pos, 10)
            pygame.draw.circle(win, (0, 0, 255), pointer_pos, 10)

            if (just_left_clicked and not interacting_with_ui) or (keys[pygame.K_k] and pygame.KEYDOWN in [event.type for event in events]):
                match edit_mode:
                    case "draw_outer_track":
                        outer_track.append((mouse_pos[0], mouse_pos[1]))
                    case "draw_inner_track":
                        inner_track.append((mouse_pos[0], mouse_pos[1]))
                    case "draw_gates":
                        gate_point_1 = (mouse_pos[0], mouse_pos[1])
                    case "change_start_pos":
                        start_pos = (mouse_pos[0], mouse_pos[1])
                    case "delete_outer_point":
                        min_dist = -1
                        index = -1
                        for i, point in enumerate(outer_track):
                            dist = (point[0] - mouse_pos[0]) ** 2 + (point[1] - mouse_pos[1]) ** 2
                            if dist < min_dist or min_dist == -1:
                                min_dist = dist
                                index = i

                        outer_track.pop(index)
                        edit_mode = ""
                    case "add_outer_point":
                        min_dist = -1
                        index = -1
                        for i, point in enumerate(outer_track):
                            dist = (point[0] - mouse_pos[0]) ** 2 + (point[1] - mouse_pos[1]) ** 2
                            if dist < min_dist or min_dist == -1:
                                min_dist = dist
                                index = i

                        outer_track.insert(index + 1, pointer_pos)
                        edit_mode = ""
                    case "delete_inner_point":
                        min_dist = -1
                        index = -1
                        for i, point in enumerate(inner_track):
                            dist = (point[0] - mouse_pos[0]) ** 2 + (point[1] - mouse_pos[1]) ** 2
                            if dist < min_dist or min_dist == -1:
                                min_dist = dist
                                index = i

                        inner_track.pop(index)
                        edit_mode = ""
                    case "add_inner_point":
                        min_dist = -1
                        index = -1
                        for i, point in enumerate(inner_track):
                            dist = (point[0] - mouse_pos[0]) ** 2 + (point[1] - mouse_pos[1]) ** 2
                            if dist < min_dist or min_dist == -1:
                                min_dist = dist
                                index = i

                        inner_track.insert(index + 1, pointer_pos)
                        edit_mode = ""
                    case "move_outer_point":
                        min_dist = -1
                        index = -1
                        for i, point in enumerate(outer_track):
                            dist = (point[0] - mouse_pos[0]) ** 2 + (point[1] - mouse_pos[1]) ** 2
                            if dist < min_dist or min_dist == -1:
                                min_dist = dist
                                index = i

                        outer_track[index ] = pointer_pos
                        edit_mode = ""
                    case "move_inner_point":
                        min_dist = -1
                        index = -1
                        for i, point in enumerate(inner_track):
                            dist = (point[0] - mouse_pos[0]) ** 2 + (point[1] - mouse_pos[1]) ** 2
                            if dist < min_dist or min_dist == -1:
                                min_dist = dist
                                index = i

                        inner_track[index] = pointer_pos
                        edit_mode = ""
                    case "move_pointer":
                        pointer_pos = (mouse_pos[0], mouse_pos[1])


            if just_right_clicked and not interacting_with_ui:
                match edit_mode:
                    case "draw_outer_track":
                        outer_track = outer_track[:-1]
                    case "draw_inner_track":
                        inner_track = inner_track[:-1]
                    case "draw_gates":
                        gate_point_2 = (mouse_pos[0], mouse_pos[1])

            if edit_mode == "draw_gates":
                if keys[pygame.K_RETURN]:
                    if gate_point_1 is not None and gate_point_2 is not None:
                        reward_gates.append((gate_point_1, gate_point_2))

                    gate_point_1 = None
                    gate_point_2 = None

                if gate_point_1 is not None:
                    pygame.draw.circle(win, (0, 0, 0), gate_point_1, 2)
                if gate_point_2 is not None:
                    pygame.draw.circle(win, (0, 0, 0), gate_point_2, 2)
                try:
                    pygame.draw.line(win, (255, 255, 255), gate_point_1, gate_point_2)
                except TypeError:
                    pass

        pygame.display.update()
        win.fill(grass_colour)

        if not player_playing and not editing_level:
            if time.time() - start_time > max_gen_time and max_gen_time > 0 and not game_paused:
                for i, g in enumerate(ge):
                    dist = math.sqrt((players[i].x - start_pos[0]) ** 2 + (players[i].y - start_pos[1]) ** 2)
                    ge[j].fitness += dist * dist_reward_multiplier

                    point_dist = math.sqrt(
                        (player.x - path_points[(player.target_gate) % len(path_points)][0]) ** 2 +
                        (player.y - path_points[(player.target_gate) % len(path_points)][1]) ** 2)
                    ge[j].fitness -= dist * path_point_dist_penalty_multiplier

                players = []
                ge = []
                nets = []

            if time.time() - start_time > fitness_cutoff_time and fitness_cutoff_time > 0 and not game_paused:
                for i, g in enumerate(ge):
                    if (g.fitness < fitness_cutoff_threshold):
                        dist = math.sqrt((players[i].x - start_pos[0]) ** 2 + (players[i].y - start_pos[1]) ** 2)
                        g.fitness += dist * dist_reward_multiplier

                        point_dist = math.sqrt(
                            (players[i].x - path_points[(players[i].target_gate) % len(path_points)][0]) ** 2 +
                            (players[i].y - path_points[(players[i].target_gate) % len(path_points)][1]) ** 2)
                        g.fitness -= dist * path_point_dist_penalty_multiplier

                        g.fitness += cutoff_penalty
                        players.pop(i)
                        nets.pop(i)
                        ge.pop(i)

            if frames_passed > max_gen_frames and max_gen_frames > -1:
                for i, g in enumerate(ge):
                    dist = math.sqrt((players[i].x - start_pos[0]) ** 2 + (players[i].y - start_pos[1]) ** 2)
                    ge[j].fitness += dist * dist_reward_multiplier

                    point_dist = math.sqrt(
                        (player.x - path_points[(player.target_gate) % len(path_points)][0]) ** 2 +
                        (player.y - path_points[(player.target_gate) % len(path_points)][1]) ** 2)
                    ge[j].fitness -= dist * path_point_dist_penalty_multiplier

                players = []
                ge = []
                nets = []

            for i, player in enumerate(players):
                if abs(player.vel) <= 0.001 and abs(player.x_vel) <= 0.001 and abs(player.y_vel) <= 0.001 and player.acc == 0:
                    dist = math.sqrt((player.x - start_pos[0]) ** 2 + (player.y - start_pos[1]) ** 2)
                    ge[i].fitness += dist * dist_reward_multiplier

                    point_dist = math.sqrt(
                        (player.x - path_points[(player.target_gate) % len(path_points)][0]) ** 2 +
                        (player.y - path_points[(player.target_gate) % len(path_points)][1]) ** 2)
                    ge[i].fitness -= dist * path_point_dist_penalty_multiplier

                    players.pop(i)
                    nets.pop(i)
                    ge.pop(i)

        for g in ge:
            if g.fitness > best_fitness:
                best_fitness = g.fitness

        if len(players) == 0 and not editing_level:
            if False:
                with open("fitnesses.txt", "a") as f:
                    f.write("GEN " + str(GEN) + ": " + str(round(best_fitness * 1000) / 1000) + "\n")

            break
            is_running = False

        clock.tick(fps)
        if not game_paused:
            frames_passed += 1


def replay_genome(config_path, genome_path="player-model.pickle"):
    global GEN

    # Load required NEAT config
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    # Unpickle saved winner
    with open(genome_path, "rb") as f:
        genome = pickle.load(f)


    GEN = int('0' + ''.join(c for c in genome_path if c.isnumeric()))

    # Convert loaded genome into required data structure
    genomes = [(1, genome)]

    # Call game with only the loaded genome
    main(genomes, config)


def replay_checkpoint(config_path, checkpoint_path, save_path, save_model=True):
    run(config_path, 1, False, True, save_model,
        checkpoint_path=checkpoint_path, model_save_path=save_path)


def mass_replay_genome(config_path, file_path):
    models = [f for f in listdir(file_path)]
    models = sorted(models, key=lambda x: int(re.search(r'\d+', x).group()))
    print(models)
    for model in models:
        print(model)
        replay_genome(config_path, file_path + "/" + model)


def mass_replay_checkpoints(config_path, file_path, save_prefix, save_model=True):
    checkpoints = [f for f in listdir(file_path)]
    print(checkpoints)
    for checkpoint in checkpoints:
        path = file_path + "/" + checkpoint
        print(path)
        replay_checkpoint(config_path, path, save_prefix + "-" + checkpoint + ".pickle", save_model)


def run(config_path, iterations, save_checkpoints=True, load_checkpoints=False, save_model=True, checkpoint_interval=10,
        checkpoint_prefix="checkpoints/neat-checkpoint", checkpoint_path=checkpoint_path,
        model_save_path="player-model.pickle"):
    global GEN

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    if load_checkpoints:
        p = neat.checkpoint.Checkpointer.restore_checkpoint(checkpoint_path)
    else:
        p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))

    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    if save_checkpoints:
        checkpointer = neat.checkpoint.Checkpointer(generation_interval=checkpoint_interval,
                                                    filename_prefix=checkpoint_prefix)
        p.add_reporter(checkpointer)

    if load_checkpoints:
        print(checkpoint_path, checkpoint_prefix)
        GEN = int(checkpoint_path.replace(checkpoint_prefix, ''))
    else:
        GEN = 0

    winner = p.run(main, iterations)
    if save_model:
        with open(model_save_path, "wb") as f:
            pickle.dump(winner, f)



if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "NEAT-info.txt")

    with open("fitnesses.txt", "r") as f:
        stored_fitnesses = f.readlines()

    ordered_fitnesses = [0] * len(stored_fitnesses)
    print(stored_fitnesses)
    print(ordered_fitnesses)

    for encoding in stored_fitnesses:
        gen, fitness = encoding.split(': ')
        gen = gen.split(' ')[1]
        fitness = fitness[:-1]
        # print(gen, fitness)

        ordered_fitnesses[int(gen) - 1] = fitness

    print(ordered_fitnesses)

    # for fitness in ordered_fitnesses:
    #     with open("ordered_fitnesses.txt", "a") as f:
    #         f.write(fitness + "\n")

    highest_fitness = 0
    for i in range(len(ordered_fitnesses) - 1):
        if i == 500:
            highest_fitness = 0
        # print(i, ordered_fitnesses[i])
        if ordered_fitnesses[i] != ordered_fitnesses[i + 1]:
            pass
        if float(ordered_fitnesses[i]) > highest_fitness:
            # print(i)
            highest_fitness = float(ordered_fitnesses[i])

    all_textboxes = []
    all_textboxes += home_settings_textboxes
    all_textboxes += game_settings_textboxes
    all_textboxes += edit_textboxes

    for textbox in all_textboxes:
        box_code = textbox.code

        match box_code:
            case "max_gen_time":
                textbox.text = str(max_gen_time)
            case "fitness_cutoff_time":
                textbox.text = str(fitness_cutoff_time)
            case "max_gen_frames":
                textbox.text = str(max_gen_frames)
            case "checkpoint_prefix":
                textbox.text = checkpoint_prefix
            case "checkpoint_path":
                textbox.text = checkpoint_path
            case "model_path":
                textbox.text = saved_model_path
            case "training_generations":
                textbox.text = str(generations)
            case "checkpoint_interval":
                textbox.text = str(checkpoint_interval)
            case "level_name":
                textbox.text = level_name
            case "start_rot":
                textbox.text = float(start_rot)

    is_running = True

    while is_running:
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()

        user_input = ""
        hit_backspace = False
        interacting_with_ui = False

        for event in events:
            # Checks if the player quit the program
            if event.type == pygame.QUIT:
                is_running = False
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    is_left_clicking = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    is_left_clicking = True
            elif event.type == pygame.KEYDOWN:
                user_input += event.unicode
                if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    user_input.upper()

                if event.key == pygame.K_BACKSPACE:
                    hit_backspace = True

        if keys[pygame.K_ESCAPE]:
            game_settings_open = False
            menu_settings_open = False

        win.fill(menu_colour)

        visible_buttons = []
        visible_text = []
        visible_textboxes = []

        if game_settings_open:
            visible_buttons += game_settings_buttons
            visible_text += game_settings_text
        elif menu_settings_open:
            visible_buttons += home_settings_buttons
            visible_text += home_settings_text
            visible_textboxes += home_settings_textboxes
        else:
            visible_buttons += home_buttons

        for button in visible_buttons:
            if is_left_clicking:
                if button.x < mouse_pos[0] < button.x + button.w:
                    if button.y < mouse_pos[1] < button.y + button.h:
                        interacting_with_ui = True
                        button_code = button.code

                        match button_code:
                            case "quit":
                                is_running = False
                                pygame.quit()
                                quit()
                            case "train":
                                fps = train_fps

                                player_playing = False
                                replay_best = False

                                run(config_path, iterations=generations, save_checkpoints=save_checkpoints,
                                    load_checkpoints=load_checkpoints, save_model=save_best,
                                    checkpoint_interval=checkpoint_interval, checkpoint_prefix=checkpoint_prefix,
                                    checkpoint_path=checkpoint_path, model_save_path=saved_model_path)

                                print("FINISHED TRAINING")
                                is_left_clicking = False
                                game_settings_open = False
                                exit_training = False
                            case "play":
                                fps = play_fps

                                player_playing = True
                                replay_best = False

                                # run(config_path, 1, False, False, 1,
                                #     None, None, None)
                                main(None, config_path)

                                print("FINISHED PLAYING")
                                is_left_clicking = False
                                game_settings_open = False
                                exit_training = False
                            case "replay_model":
                                fps = play_fps

                                player_playing = False
                                replay_best = True

                                replay_genome(config_path, saved_model_path)

                                print("FINISHED MODEL REPLAY")
                                is_left_clicking = False
                                game_settings_open = False
                                exit_training = False
                            case "replay_checkpoint":
                                fps = play_fps

                                player_playing = False
                                replay_best = False
                                save_checkpoint_to_model = False

                                replay_checkpoint(config_path, checkpoint_path, None, False)

                                print("FINISHED CHECKPOINT REPLAY")
                                is_left_clicking = False
                                game_settings_open = False
                                exit_training = False
                            case "save":
                                fps = train_fps

                                player_playing = False
                                replay_best = False
                                save_checkpoint_to_model = True

                                replay_checkpoint(config_path, checkpoint_path, saved_model_path, True)

                                print("FINISHED SAVING")
                                is_left_clicking = False
                                game_settings_open = False
                                exit_training = False
                            case "mass_save_models":
                                fps = train_fps

                                player_playing = False
                                replay_best = False
                                save_checkpoint_to_model = False

                                mass_replay_checkpoints(config_path, "checkpoints_copy", "saved_models/player_model", True)

                                is_left_clicking = False
                                game_settings_open = False
                                exit_training = False
                            case "mass_replay_models":
                                fps = play_fps

                                player_playing = False
                                replay_best = True
                                save_checkpoint_to_model = False

                                mass_replay_genome(config_path, "final_model")

                                is_left_clicking = False
                                game_settings_open = False
                                exit_training = False

                                player_playing = False
                                replay_best = True
                                save_checkpoint_to_model = False

                                level_name = "Track 3"
                                mass_replay_genome(config_path, "improved_models_trackthree")

                                is_left_clicking = False
                                game_settings_open = False
                                exit_training = False
                            case "edit_level":
                                editing_level = True
                                edit_mode = ""
                                player_playing = False

                                main(None, config_path)

                                is_left_clicking = False
                                editing_level = False
                                exit_training = False
                            case "open_menu_settings":
                                menu_settings_open = True
                            case "close_menu_settings":
                                menu_settings_open = False
                            case "save_checkpoints":
                                save_checkpoints = True
                            case "no_save_checkpoints":
                                save_checkpoints = False
                            case "load_checkpoints":
                                load_checkpoints = True
                            case "no_load_checkpoints":
                                load_checkpoints = False
                            case "save_best":
                                save_best = True
                            case "no_save_best":
                                save_best = False
                            case _:
                                print("WARNING: Button code '" + button_code + "' is not recognized. Are you sure it's correct?")

            button.draw(win, mouse_pos, is_left_clicking)

        for text in visible_text:
            text_code = text.code

            match text_code:
                case "save_checkpoints":
                    text.text = "Yes" if save_checkpoints else "No"
                case "load_checkpoints":
                    text.text = "Yes" if load_checkpoints else "No"
                case "save_best":
                    text.text = "Yes" if save_best else "No"

            text.draw(win)
        # print(checkpoint_path, saved_model_path)
        for textbox in visible_textboxes:
            if textbox.x < mouse_pos[0] < textbox.x + textbox.w:
                if textbox.y < mouse_pos[1] < textbox.y + textbox.h:
                    interacting_with_ui = True
                    box_code = textbox.code

                    match box_code:
                        case "max_gen_time":
                            if user_input.isnumeric() or user_input in ['.', '-']:
                                textbox.text += user_input
                            if hit_backspace:
                                textbox.text = textbox.text[:-1]

                            try:
                                max_gen_time = float(textbox.text)
                            except ValueError:
                                pass
                        case "fitness_cutoff_time":
                            if user_input.isnumeric() or user_input in ['.', '-']:
                                textbox.text += user_input
                            if hit_backspace:
                                textbox.text = textbox.text[:-1]

                            try:
                                fitness_cutoff_time = float(textbox.text)
                            except ValueError:
                                pass
                        case "max_gen_frames":
                            if user_input.isnumeric() or user_input in ['.', '-']:
                                textbox.text += user_input
                            if hit_backspace:
                                textbox.text = textbox.text[:-1]

                            try:
                                max_gen_frames = float(textbox.text)
                            except ValueError:
                                pass
                        case "checkpoint_prefix":
                            if hit_backspace:
                                checkpoint_prefix = checkpoint_prefix[:-1]
                            elif user_input.isprintable():
                                checkpoint_prefix += str(user_input)

                            textbox.text = checkpoint_prefix
                        case "checkpoint_path":
                            if hit_backspace:
                                checkpoint_path = checkpoint_path[:-1]
                            elif user_input.isprintable():
                                checkpoint_path += str(user_input)

                            textbox.text = checkpoint_path
                        case "model_path":
                            if hit_backspace:
                                saved_model_path = saved_model_path[:-1]
                            elif user_input.isprintable():
                                saved_model_path += str(user_input)

                            textbox.text = saved_model_path
                        case "training_generations":
                            if user_input.isnumeric():
                                textbox.text += user_input
                            if hit_backspace:
                                textbox.text = textbox.text[:-1]

                            try:
                                generations = int(textbox.text)
                            except ValueError:
                                pass
                        case "checkpoint_interval":
                            if user_input.isnumeric():
                                textbox.text += user_input
                            if hit_backspace:
                                textbox.text = textbox.text[:-1]

                            try:
                                checkpoint_interval = int(textbox.text)
                            except ValueError:
                                pass
                        case _:
                            print("WARNING: Textbox code '" + box_code + "' is not recognized. Are you sure it's correct?")

            textbox.draw(win)

        pygame.display.update()

        clock.tick(play_fps)

    # if replay_best:
    #     replay_genome(config_path, saved_model_path)
    # elif save_checkpoint_to_model:
    #     checkpoint_to_model(config_path, checkpoint_path, saved_model_path)
    # else:
    #     run(config_path, iterations=generations, save_checkpoints=save_checkpoints,
    #         load_checkpoints=load_checkpoints, checkpoint_interval=checkpoint_interval,
    #         checkpoint_prefix=checkpoint_prefix, checkpoint_path=checkpoint_path, model_save_path=saved_model_path)
