import pygame, pytmx
import time as t
import math as m
import random as r
import os, csv, json

pygame.init()

pygame.display.set_caption("Kastles and Krakens")

class MainGame():
    def __init__(self):
        ### TO DO:
        # Differentiating between sprites and battle_sprites using a trigger
        # Battle phase, at least something
        self.running = True
        self.game_WIDTH = 1280
        self.game_HEIGHT = 960
        self.main_screen = pygame.display.set_mode((self.game_WIDTH, self.game_HEIGHT))
        self.clock = pygame.time.Clock()
        self.prev_time = t.time()
        
        self.key_w = False
        self.key_a = False
        self.key_s = False
        self.key_d = False
        self.key_p = False

        self.player = Player(self, "player", 624, 600, 0, 4)
        
        # player's current position in relation to the overworld, X and Y variables
        self.ow_posX = 2
        self.ow_posY = 1
        self.cur_ow_pos = [self.ow_posX, self.ow_posY]
        self.prev_ow_pos = []
        
        self.states = ["roaming", "battle", "menu"]
        self.game_state = self.states[0]

        self.load_rooms_betterer()

    def get_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.key_w = True
                elif event.key == pygame.K_a:
                    self.key_a = True
                elif event.key == pygame.K_s:
                    self.key_s = True
                elif event.key == pygame.K_d:
                    self.key_d = True
                elif event.key == pygame.K_p:
                    self.player.spr_update()
                
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.key_w = False
                elif event.key == pygame.K_a:
                    self.key_a = False
                elif event.key == pygame.K_s:
                    self.key_s = False
                elif event.key == pygame.K_d:
                    self.key_d = False
                elif event.key == pygame.K_p:
                    self.key_p = False
    
    def change_pos(self):
        # Checks if the player has gone into a different room
        # If the player has moved between room, the function loads a new room from scratch
        self.cur_ow_pos = [self.ow_posX, self.ow_posY]
        if self.cur_ow_pos == self.prev_ow_pos:
            return
        self.cur_room = self.world_data[self.ow_posY][self.ow_posX]
        self.cur_map_image = self.cur_room.map.load_map()
        self.cur_wall_list = self.cur_room.wall_list
        self.load_sprites()
        self.load_enemies(self.cur_room.enemy_list)
        self.prev_ow_pos = self.cur_ow_pos

    def load_rooms_betterer(self):
        self.load_mapfile()
        self.world_data = []
        self.room_dir = os.path.join("room_bgs")

        self.voidname = os.path.join(self.room_dir, "void.tmx")
        self.void = Room(self, "void")

        for f in self.mapdata:
            rowlist = []
            for r in f:
                if r == "void":
                    roomdata = self.void
                    rowlist.append(roomdata)
                else:
                    roomdata = Room(self, r)
                    rowlist.append(roomdata)
            self.world_data.append(rowlist)
        #print(self.world_data)
        
    def load_mapfile(self):
        with open("maplist.csv") as r:
            loaded = csv.reader(r)  # reads the file, returns idk a number?
            self.mapdata = list(loaded)  # takes that number and turns it into a list (that we can work with)

    def load_sprites(self):
        self.game_sprites = pygame.sprite.Group()
        self.game_sprites.add(self.player)

    def load_enemies(self, enemy_list):
        # enemy_data = [object.x, object.y, object.properties["enemy_sprite"], object.properties["enemy_type"], object.properties["movement_range"], object.properties["movement_speed"]]
        for enemy in enemy_list:
            if enemy[3] == "walker":
                enemy = Walker(self, enemy[2], enemy[0], enemy[1], enemy[4], 4, enemy[5])
            elif enemy[3] == "charger":
                enemy = Charger(self, enemy[2], enemy[0], enemy[1], enemy[4], 8, enemy[5])
            #enemy = Enemy(self, enemy[0], enemy[1], enemy[2], enemy[3], 4, enemy[0])
            self.game_sprites.add(enemy)
        
    # Source: Christian Duenas - Pygame Framerate Independence
    # https://www.youtube.com/watch?v=XuyrHE6GIsc
    def get_dt(self):
        # so far relatively unnecessary, likely to be removed in the future
        now = t.time()
        self.dt = now - self.prev_time
        self.prev_time = now
        #print(self.dt)
        
    def game_loop(self):
        while self.running:
            self.clock.tick(60)
            self.get_dt()
            self.get_events()
            self.change_pos()
            self.main_screen.blit(self.cur_map_image, (0,0))
            self.game_sprites.update()
            #self.battle_sprites.update()
            self.game_sprites.draw(self.main_screen)
            #self.battle_sprites.draw(self.main_screen)
            #### IF overworld: x, elif battlephase: Y

            pygame.display.flip()

class Spritesheet():
    def __init__(self, filename):
        ### TO DO:
        # Currently only works if every sprite has their individual folder with their spritesheet
        # May need to create a single, fixed folder that contains EVERY spritesheet in the game
        self.filename = filename
        #print(self.filename)
        self.jsonfilename = self.filename.replace("png","json")
        self.sprite_dir = os.path.join("spritesheets")
        self.sprite_sheet = pygame.image.load(os.path.join(self.sprite_dir, self.filename)).convert()
        self.meta_data = os.path.join(self.sprite_dir, self.jsonfilename)
        with open(self.meta_data) as f:
            self.data = json.load(f)
        f.close()

    def get_sprite(self, x, y, width, height):
        # Draws the sprite on a small surface
        sprite = pygame.Surface((width, height))
        sprite.set_colorkey((0,0,0)) # Sets the sprite alpha channel
        sprite.blit(self.sprite_sheet, (0,0), (x,y,width,height))
        return sprite
        
    def parse_sprite(self, name):
        # Cuts out the sprite image from the spritesheet
        # Returns the image
        sprite = self.data["frames"][name]["frame"]
        x = sprite["x"]
        y = sprite["y"]
        width = sprite["w"]
        height = sprite["h"]
        image = self.get_sprite(x, y, width, height)
        return image

class Room():
    # Room object, stores info about walls/enemies/room properties (mainly for the purposes of readibility)
    def __init__(self, game, roomname):
        self.game = game
        self.roomname = os.path.join(self.game.room_dir, (roomname + ".tmx"))
        self.map = TileMap(self.roomname)
        self.map.render_map()
        
        self.wall_list = self.map.wall_list
        self.enemy_list = self.map.enemy_list


# Source: KidsCanCode - Tile-based game part 12: Loading Tiled Maps
# https://www.youtube.com/watch?v=QIXyj3WeyZM
class TileMap():
    # Pytmx podporuje nepozmenene spritesheets, lze pouzit puvodni upravenou mapu, zatez na CPU je vicemene stejna
    def __init__(self, mapfile):
        self.wall_list = []
        self.enemy_list = []
        tm = pytmx.load_pygame(mapfile, pixelalpha = True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm
    
    def render_map(self):
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                for object in self.tmxdata.objects:
                    # object properties: id (integer); name,type (strings); x,y,width,height (floats); object.properties (dictionary)
                    # object.properties is a dictionary that displays pairs of data
                    if object.type == "wall":
                        # The 32px offset is due to the colliderect function - it's based off of the coordinates of the top left corner
                        temp_rect = pygame.Rect(object.x - 32, object.y - 32, object.width + 32, object.height + 32)
                        self.wall_list.append(temp_rect)
                    if object.type == "enemy":
                        #print(str(object.properties["hor_enemy"]))
                        enemy_data = [object.x, object.y, object.properties["enemy_sprite"], object.properties["enemy_type"], object.properties["movement_range"], object.properties["movement_speed"]]
                        self.enemy_list.append(enemy_data)
                        #print(self.enemy_list)
    
    def load_map(self):
        temp_surface = pygame.Surface((self.width, self.height))
        self.draw_map(temp_surface)
        return temp_surface

    def draw_map(self, surface):
        tilecommand = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = tilecommand(gid)
                    if tile:
                        surface.blit(tile, (x*self.tmxdata.tilewidth, y*self.tmxdata.tileheight))

class NPC(pygame.sprite.Sprite):
    # Parent class for every character in the game (player, enemies, shopkeepers, etc.)
    # Contains basic spritesheet functions, basic animation, collision with walls
    def __init__(self, game, sourcefile, anch_x, anch_y, range, frames_per_side):
        super().__init__()
        self.game = game
        self.sourcefile = sourcefile + "_sprites.png"
        
        self.state_idle = True
        self.direction_x = 0
        self.direction_y = 0
        self.animation_time = 0
        self.size_coef = 3 # default sprite size

        self.load_frames(sourcefile, frames_per_side)
        self.rect = self.image.get_rect(topleft = (anch_x, anch_y))

    def load_frames(self, sourcefile, frames_per_side):
        self.spritesheet = Spritesheet(self.sourcefile)
        self.frames_down = []
        self.frames_up = []
        self.frames_left = []
        self.frames_right = []
        self.frames = [self.frames_down, self.frames_up, self.frames_left, self.frames_right]
        self.sides = ["_front","_back","_left","_right"]
        side_list_pos = 0
        for framelist in self.frames:
            for frame in range(frames_per_side):
                parsed_frame = self.spritesheet.parse_sprite(sourcefile + self.sides[side_list_pos] + str(frame+1) + ".png")
                framelist.append(parsed_frame)
            side_list_pos += 1
        self.frames.clear()
        self.cur_frame = 0
        self.image = self.frames_down[self.cur_frame]
        self.cur_sprlist = self.frames_down

    def update(self):
        self.draw_NPC()
        self.move()

    def draw_NPC(self):
        # most sprites are 48*48px
        self.set_state()
        self.animate()
        self.size = self.image.get_size()
        self.bigger_sprite = pygame.transform.scale(self.image, (self.size[0]*self.size_coef, self.size[1]*self.size_coef))
        self.image = self.bigger_sprite

    def set_state(self):
        # Detects whether the NPC is moving or not
        if self.direction_x != 0 or self.direction_y != 0:
            self.state_idle = False
        else:
            self.state_idle = True

    def animate(self):
        # If the NPC is idle, the program doesn't iterate through the list of frames
        if self.state_idle:
            self.cur_frame = 0
        else:
            # Updates the current frame/cur_frame variable based on the amount of time that has passed
            now = pygame.time.get_ticks()
            if now - self.animation_time > 200:
                self.animation_time = now
                self.cur_frame = (self.cur_frame + 1) % len(self.cur_sprlist)

            if self.direction_x > 0:
                self.cur_sprlist = self.frames_right
            elif self.direction_x < 0:
                self.cur_sprlist = self.frames_left
            elif self.direction_y > 0:
                self.cur_sprlist = self.frames_down
            elif self.direction_y < 0:
                self.cur_sprlist = self.frames_up
        self.image = self.cur_sprlist[self.cur_frame]

    def move(self):
        # I don't know what to put here right now, but this will most likely get handled by individual enemy classes
        pass

    def check_wallsX(self):
        for wall in self.cur_wall_list:
            if self.rect.colliderect(wall):
                if self.direction_x > 0:
                    #print("collision right side")
                    self.rect.right = wall.left
                elif self.direction_x < 0:
                    #print("collision left side")
                    self.rect.left = wall.right

    def check_wallsY(self):
        for wall in self.cur_wall_list:
            if self.rect.colliderect(wall):
                if self.direction_y > 0:
                    #print("collision bottom side")
                    self.rect.bottom = wall.top
                elif self.direction_y < 0:
                    #print("collision top side")
                    self.rect.top = wall.bottom


class Player(NPC):
    ### TO DO:
    # Instead of moving between rooms based on specific coordinates, find a way to move between rooms based on collisions between custom rects
    # Maybe even add a small animation? That'd be nice
    def __init__(self, game, sourcefile, anch_x, anch_y, range, frames_per_side):
        super().__init__(game, sourcefile, anch_x, anch_y, range, frames_per_side)
        

    # Source: Christian Duenas - Pygame Game States Tutorial
    # https://www.youtube.com/watch?v=b_DkQrJxpck
    def move(self):
        self.cur_wall_list = self.game.cur_wall_list
        
        self.direction_x = self.game.key_d - self.game.key_a
        self.direction_y = self.game.key_s - self.game.key_w
        
        # rect coordinates are integers, not floats;
        # round() is an attempt to implement delta_time without breaking the game
        self.rect.x += round(self.direction_x * 3 * self.game.dt * 60)
        self.check_wallsX()
        self.rect.y += round(self.direction_y * 3 * self.game.dt * 60)
        self.check_wallsY()
        #print("X: ", str(self.direction_x), ", Y: ", str(self.direction_y))
        #print("X: ", str(self.rect.x), ", Y: ", str(self.rect.y))
        
        self.check_edge()

    def check_edge(self):
        ### TO DO:
        # Check the player's position using the self.rect variable
        if self.rect.x <= 16: #player approaches left side
            self.game.ow_posX -= 1
            self.rect.x = 1180
        elif self.rect.x >= 1232: #player approaches right side
            self.game.ow_posX += 1
            self.rect.x = 80
        elif self.rect.y <= 16: #player approaches top side
            self.game.ow_posY -= 1
            self.rect.y = 880
        elif self.rect.y >= 912: #player approaches bottom side
            self.game.ow_posY += 1
            self.rect.y = 80


class Enemy(NPC):
    ## TO DO:
    # wander() function to move randomly around an anchor point
    # Multiple enemy types; different move_enemy() functions
    def __init__(self, game, sourcefile, anch_x, anch_y, range, frames_per_side, movement_speed):
        # Since the enemy's position is written in world_data, enemies don't need to track their position (at least in theory)
        super().__init__(game, sourcefile, anch_x, anch_y, range, frames_per_side)
        self.range = int(range)
        self.anch_x = int(anch_x)
        self.anch_y = int(anch_y)
        #self.new_pos = [self.rect.x,self.rect.y]
        self.at_home = True
        self.player_spotted = False
        self.wandering = False
        self.wander_delay = False
        self.wander_time = 0.0
        self.alive = True


    

    def move(self):
        self.check_for_home()
        self.check_for_player() # this is going to check if the player is within some arbitrary range
        if self.player_spotted == True:
            self.chase_player() # this is going to use a pathfinding algorithm to chase the player
        else:
            if self.at_home == False:
                #print("I'm going home")
                self.return_home()
            else:
                #print("I'm wandering")
                self.wander()
        #self.find_pos() # this is going to find a new position to move to (within range)
        #self.move_enemy() # this is going to move the enemy to a new position after some arbitrary length of time has passed

    def check_for_home(self):
        if ((self.anch_x - self.range) <= self.rect.x <= (self.anch_x + self.range)):
            #print("i am home")
            self.at_home = True
        elif ((self.anch_y - self.range) <= self.rect.y <= (self.anch_y + self.range)):
            #print("i am home")
            self.at_home = True
        else:
            #print("i am not home")
            self.at_home = False

    def check_for_player(self):
        # calculates the distance between the enemy's rect and the player's rect
        self.distance = m.hypot(self.rect.x - self.game.player.rect.x, self.rect.y - self.game.player.rect.y)
        if self.distance <= self.range:
            self.player_spotted = True
            #print("I see you!")
        else:
            self.player_spotted = False
            #print("where did you go?")

    def return_home(self):
        self.new_pos = [self.anch_x, self.anch_y]
        self.move_to_new_pos()

    def wander(self):
        if self.range == 0:
            pass
        elif self.wander_delay == True:
            self.time_delay()
        elif self.wandering == False:
            self.find_pos()
            self.move_to_new_pos()
        else:
            self.move_to_new_pos()

    def find_pos(self):
        # finds a new target position within range of anchor
        
        direction = self.find_direction()
        self.find_distance(direction)
    def find_direction(self):
        directions = ["up", "down", "left", "right"]
        new_direction = r.choice(directions)
        return new_direction
    def find_distance(self, direction):
        # this code is intentionally ugly, right now I just want this to work
        # the purpose of bottom_range/top_range is to ensure that the sprite doesn't walk off screen
        # I WILL OPTIMIZE THIS LATER I PROMISE
        if direction == "up":
            bottom_range = int(self.anch_y-self.range)
            if bottom_range < 0:
                bottom_range = 0
            random_pos = r.randint(bottom_range, self.rect.y)
            self.new_pos = [self.rect.x, random_pos]
        elif direction == "down":
            top_range = int(self.anch_y+self.range)
            if top_range > (self.game.game_HEIGHT - (self.size[1]*self.size_coef)):
                top_range = self.game.game_HEIGHT - (self.size[1]*self.size_coef)
            random_pos = r.randint(self.rect.y, top_range)
            self.new_pos = [self.rect.x, random_pos]
        elif direction == "left":
            bottom_range = int(self.anch_x-self.range)
            if bottom_range < 0:
                bottom_range = 0
            random_pos = r.randint(bottom_range, self.rect.x)
            self.new_pos = [random_pos, self.rect.y]
        elif direction == "right":
            top_range = int(self.anch_x+self.range)
            if top_range > (self.game.game_WIDTH - (self.size[0]*self.size_coef)):
                top_range = self.game.game_WIDTH - (self.size[0]*self.size_coef)
            random_pos = r.randint(self.rect.x, top_range)
            self.new_pos = [random_pos, self.rect.y]

    def move_to_new_pos(self):
        # first, check if the target has been reached
        if (self.new_pos[0] == self.rect.x) and (self.new_pos[1] == self.rect.y):
            # reset directions
            self.direction_x = 0
            self.direction_y = 0
            self.wandering = False
            self.time_delay()
        else:
            self.wandering = True
            self.create_new_direction()
            self.move_enemy()

    def create_new_direction(self):
        rough_direction_x = self.new_pos[0] - self.rect.x
        if rough_direction_x > 0:
            self.direction_x = 1
        elif rough_direction_x == 0:
            self.direction_x = 0
        else:
            self.direction_x = -1

        rough_direction_y = self.new_pos[1] - self.rect.y
        if rough_direction_y > 0:
            self.direction_y = 1
        elif rough_direction_y == 0:
            self.direction_y = 0
        else:
            self.direction_y = -1
    def move_enemy(self):
        pass

    def time_delay(self):
        time_delay = 1
        dt = self.game.dt
        self.wander_time += dt
        if self.wander_time > time_delay:
            #print("it's been 1 second")
            self.wander_delay = False
            self.wander_time = 0
        else:
            self.wander_delay = True

class Walker(Enemy):
    # Simple enemy; if the player is spotted, it will follow the player in a straight line
    # Skeleton: slow walker
    # Flying Eye: medium/fast walker
    # Goblin: fast walker
    def __init__(self, game, sourcefile, anch_x, anch_y, range, frames_per_side, movement_speed):
        super().__init__(game, sourcefile, anch_x, anch_y, range, frames_per_side, movement_speed)
        #self.mvms = movement_speed
        self.mvms = 1
        # mvmtimer limits enemies to 30FPS in order to input custom movement speeds
        self.mvmtimer = 0

    def chase_player(self):
        # calculates the direction the enemy will move in during a chase
        self.detecX = self.game.player.rect.x - self.rect.x
        self.detecY = self.game.player.rect.y - self.rect.y

        if self.detecX < 0:
            self.direction_x = -1
        elif self.detecX > 0:
            self.direction_x = 1
        if self.detecY < 0:
            self.direction_y = -1
        elif self.detecY > 0:
            self.direction_y = 1

        self.approximate_direction()
        """
        now = pygame.time.get_ticks()
        if now - self.stopping_time > 2000:
            self.stopping_time = now
        elif now - self.stopping_time > 1000:
        """    
            
        self.move_enemy()
        #print(str(self.sourcefile) + str(now))
            

    def move_enemy(self):
        # a general movement function, direction depends on whether the enemy is chasing or idle
        # skoleton - 0.75, eye - 1.00, goblin - 1.25/1.50?
        """
        if self.mvmtimer == 1:
            self.rect.x += round(self.direction_x * self.mvms * self.game.dt * 60)
            #self.check_wallsX()
            self.rect.y += round(self.direction_y * self.mvms * self.game.dt * 60)
            #self.check_wallsY()
            self.mvmtimer = 0
        else:
            self.mvmtimer += 1
        """
        self.rect.x += round(self.direction_x * self.mvms * self.game.dt * 60)
            #self.check_wallsX()
        self.rect.y += round(self.direction_y * self.mvms * self.game.dt * 60)

        #print("Rect_X: ", self.rect.x, "Rect_Y: ", self.rect.y)

    def approximate_direction(self):
        # stops the sprite from "vibrating" (a.k.a. oscillating)
        if self.detecX <= 2 and self.detecX >= -2:
            self.direction_x = 0
        if self.detecY <= 2 and self.detecY >= -2:
            self.direction_y = 0

    def wander_alt(self):
        # idle movement, plays while the player is out of range
        self.direction_x, self.direction_y = 0, 0
        self.state_idle = True

        self.find_pos()
        self.move_enemy()

    def return_home_alt(self):
        pass

class Charger(Enemy):
     #Complicated enemy; if the player is spotted, it will stay in place for 2 seconds, mark the player's location, and charge in a straight line
     #Mushroom/Fungus: slow charger
     #Worm: slow/medium charger, medium/large size
    def __init__(self, game, sourcefile, anch_x, anch_y, range, frames_per_side, movement_speed):
        super().__init__(game, sourcefile, anch_x, anch_y, range, frames_per_side, movement_speed)
        self.mvms = movement_speed
        self.size_coef = 4
        
    
    def load_frames(self, sourcefile, frames_per_side):
        self.spritesheet = Spritesheet(self.sourcefile)
        self.frames_left = []
        self.frames_right = []
        self.frames = [self.frames_left, self.frames_right]
        self.sides = ["_left","_right"]
        side_list_pos = 0
        for framelist in self.frames:
            for frame in range(frames_per_side):
                parsed_frame = self.spritesheet.parse_sprite(sourcefile + self.sides[side_list_pos] + str(frame+1) + ".png")
                framelist.append(parsed_frame)
            side_list_pos += 1
        self.frames.clear()
        self.cur_frame = 0
        self.image = self.frames_right[self.cur_frame]
        self.cur_sprlist = self.frames_right



    def chase_player(self):
        self.play_charging_animation()
        now = pygame.time.get_ticks()
        if now - self.prev_time > 3000:
            self.charge()

    def play_charging_animation(self):
        pass

    def charge(self):
        pass

    def return_home(self):
        pass

    def wander(self):
        pass

#class Frog(Enemy):
    # Complicated enemy; if the player is spotted, it will mark the player's direction and jump towards them
    # Do I actually want to do this one? idk how it'd work with sprites
    # Slime?






























g = MainGame()
g.game_loop()
