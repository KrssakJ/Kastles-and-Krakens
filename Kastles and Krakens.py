import pygame, pytmx
import time, math
import os, csv, json

pygame.init()

pygame.display.set_caption("Kastles and Krakens")

class MainGame():
    def __init__(self):
        #pygame.init()
        self.running = True
        self.game_WIDTH = 1280
        self.game_HEIGHT = 960
        self.main_screen = pygame.display.set_mode((self.game_WIDTH, self.game_HEIGHT))
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.prev_time = time.time()
        
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
        
        self.load_rooms_better()

    def get_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # arrow keys - debug commands (kinda)
                """
                if event.key == pygame.K_UP:
                    self.ow_posY -= 1
                elif event.key == pygame.K_DOWN:
                    self.ow_posY += 1
                elif event.key == pygame.K_LEFT:
                    self.ow_posX -= 1
                elif event.key == pygame.K_RIGHT:
                    self.ow_posX += 1
                #print(self.ow_pos)
                """
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
        ## TO DO:
        # Based on the player's current position, load the enemies in each room
        self.cur_ow_pos = [self.ow_posX, self.ow_posY]
        if self.cur_ow_pos == self.prev_ow_pos:
            return
        self.map_image = self.world_data[self.ow_posY][self.ow_posX][0].load_map()
        self.cur_room = self.world_data[self.ow_posY][self.ow_posX][1]
        self.load_sprites()
        self.load_enemies(self.world_data[self.ow_posY][self.ow_posX][2])
        self.prev_ow_pos = self.cur_ow_pos
        print(str(self.game_sprites))
        

        #self.mapid = self.room.get_room(self.ow_posX, self.ow_posY) #returns a text file that contains the name of the room
        

        #self.room_dir = os.path.join("room_bgs")
        #self.roomname = os.path.join(self.room_dir, self.mapid)
        #self.map = TileMap(self.roomname)
        #self.map_image = self.map.load_map() #loads the map into the self.map_image variable
        #self.prev_ow_pos = self.cur_ow_pos

    def load_rooms_better(self):
        self.load_mapfile()
        self.world_data = []
        self.room_dir = os.path.join("room_bgs")

        self.voidname = os.path.join(self.room_dir, "void.tmx")
        self.void = TileMap(self.voidname)

        for f in self.mapdata:
            rowlist = []
            for r in f:
                if r == "void":
                    roomdata = [self.void, [], []]
                    rowlist.append(roomdata)
                else:
                    r += ".tmx"
                    self.roomname = os.path.join(self.room_dir, r)
                    self.map = TileMap(self.roomname)
                    self.map.render_map()
                    roomdata = [self.map, self.map.wall_list, self.map.enemy_list]
                    rowlist.append(roomdata)
            self.world_data.append(rowlist)
        #print(self.world_data)
        
    def load_rooms(self):
        ### TO DO:
        # Unify room_list and wall_list
        # Desired structure: list (rows) of lists (rooms) of lists (room_name; wall_list; maybe enemy_list?) of lists (individual walls/ individual enemies) - 4(!) layers of lists
        # What if I tracked the number of walls in each room to improve readability?

        self.load_mapfile()
        # Basic setup, will use all of these later
        self.world_data = []

        self.room_list = []
        self.wall_list = []
        self.enemy_list = []
        self.room_dir = os.path.join("room_bgs")

        # Void needs to be loaded in separately, to reduce memory usage (from 141MB to 70MB)
        self.voidname = os.path.join(self.room_dir, "void.tmx")
        self.void = TileMap(self.voidname)
        self.void_image = self.void.load_map()

        for f in self.mapdata:
            #print(f)
            rowlist = []
            wall_rowlist = []
            enemy_rowlist = []
            # f variable is a list, we need a way to cycle through each row
            for r in f:
                # r variable should be the specific room
                if r == "void":
                    rowlist.append(self.void_image)
                    wall_rowlist.append(self.void.wall_list)
                    enemy_rowlist.append([])
                else:
                    r += ".tmx"
                    self.roomname = os.path.join(self.room_dir, r)
                    self.map = TileMap(self.roomname)
                    self.map_image = self.map.load_map()
                    #print(self.map.wall_list)
                    wall_rowlist.append(self.map.wall_list)
                    for enemy in self.map.enemy_list:
                        loaded_enemy = NPC(self, enemy[0], enemy[1], enemy[2], enemy[3], 4)
                        enemy_rowlist.append(loaded_enemy)

                    rowlist.append(self.map_image)
            self.room_list.append(rowlist)
            self.wall_list.append(wall_rowlist)
            self.enemy_list.append(enemy_rowlist)

            self.world_data.append(rowlist)

            
        self.row_length = len(rowlist)

        
        #print(self.row_length)
        #print(self.room.mapdata)
        #print(self.room_list)
        #print(self.wall_list)
        print(self.enemy_list)

    def load_mapfile(self):
        with open("maplist.csv") as r:
            loaded = csv.reader(r)  # reads the file, returns idk a number?
            self.mapdata = list(loaded)  # takes that number and turns it into a list (that we can work with)

    def load_sprites(self):
        self.game_sprites = pygame.sprite.Group()
        self.game_sprites.add(self.player)

    def load_enemies(self, enemy_list):
        if len(enemy_list) == 0:
            print("there are no enemies in this room.")
        else:
            print("there are some enemies in this room!")
            for enemy in enemy_list:
                enemy = Enemy(self, enemy[0], enemy[1], enemy[2], enemy[3], 4, enemy[0])
                self.game_sprites.add(enemy)
        
    # Source: Christian Duenas - Pygame Framerate Independence
    # https://www.youtube.com/watch?v=XuyrHE6GIsc
    def get_dt(self):
        now = time.time()
        self.dt = now - self.prev_time
        self.prev_time = now
        
    def game_loop(self):
        while self.running:
            self.clock.tick(60)
            self.get_events()
            self.change_pos()
            self.get_dt()
            #self.main_screen.fill((0,0,0))
            self.main_screen.blit(self.map_image, (0,0))
            self.game_sprites.update()
            self.game_sprites.draw(self.main_screen)
            #self.player.draw_player(self.player.position_x, self.player.position_y)
            pygame.display.flip()

class Spritesheet():
    def __init__(self, filename):
        ### TO DO:
        # Currently only works if every sprite has their individual folder with their spritesheet
        # May need to create a single, fixed folder that contains EVERY spritesheet in the game
        self.filename = filename
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
        # alfa kanal pro sprite
        sprite.set_colorkey((0,0,0))
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
                #print("I'm in the object layer!")
                for object in self.tmxdata.objects:
                    # object properties: id (integer); name,type (strings); x,y,width,height (floats); object.properties (dictionary)

                    #print("I found an object! It's a " + object.type + " and has a width of " + str(object.width))
                    #print("Double width: " + str(object.width*2))
                    #print("it has an id " + str(object.id))

                    if object.type == "wall":
                        # The 32px offset is due to the colliderect function - it's based off of the coordinates of the top left corner
                        temp_rect = pygame.Rect(object.x - 32, object.y - 32, object.width + 32, object.height + 32)
                        self.wall_list.append(temp_rect)
                    if object.type == "enemy":
                        enemy_data = [object.properties["enemy_type"], object.x, object.y, object.properties["movement_range"]]
                        #print("I found an enemy!")
                        #self.enemy_list.append(object.properties["enemy_type"])
                        #enemy_data.append(object.properties["enemy_type"])
                        #enemy_data.append(object.x)
                        #enemy_data.append(object.y)
                        #enemy_data.append(object.properties["movement_range"])
                        
                        
                        #if object.properties["enemy_type"] == "red_enemy":
                            # object.properties is a dictionary that displays pairs of data
                            #print("I found their enemy type!")
                            #print("object id: " + str(object.id))
                        self.enemy_list.append(enemy_data)
                        print(self.enemy_list)
            
            
        #print(self.wall_list)
    
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
# you know what I can just copy a bunch of stuff from the player class
    def __init__(self, game, sourcefile, anch_x, anch_y, range, frames_per_side):
        super().__init__()
        self.game = game
        self.sourcefile = sourcefile + "_sprites.png"
        self.load_frames(sourcefile, frames_per_side)

        self.rect = self.image.get_rect(topleft = (anch_x, anch_y))

        self.state_idle = True
        self.direction_x = 0
        self.direction_y = 0
        self.prev_time = 0
        self.cur_sprlist = self.frames_down


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
        self.cur_frame = 0
        self.image = self.frames_down[self.cur_frame]

    def update(self):
        self.draw_NPC()
        self.move()

    def draw_NPC(self):
        self.set_state()
        self.animate()
        self.size = self.image.get_size()
        self.bigger_sprite = pygame.transform.scale(self.image, (self.size[0]*3, self.size[1]*3))
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
            if now - self.prev_time > 200:
                self.prev_time = now
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
        #self.cur_room = self.game.wall_list[self.game.ow_posY][self.game.ow_posX]
        # I don't know what to put here right now, but this will most likely get handled by individual enemy classes
        pass

    def check_wallsX(self):
        for wall in self.cur_room:
            if self.rect.colliderect(wall):
                if self.direction_x > 0:
                    #print("collision right side")
                    self.rect.right = wall.left
                elif self.direction_x < 0:
                    #print("collision left side")
                    self.rect.left = wall.right

    def check_wallsY(self):
        for wall in self.cur_room:
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
        self.cur_room = self.game.cur_room
        
        self.direction_x = self.game.key_d - self.game.key_a
        self.direction_y = self.game.key_s - self.game.key_w
        
        self.rect.x += self.direction_x * 3
        self.check_wallsX()
        self.rect.y += self.direction_y * 3
        self.check_wallsY()
        
        self.check_edge()
        #print("X: " + str(self.rect.x) + " and Y: " + str(self.rect.y))

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
    # Fix the "vibrating enemy" issue
    # Fix the lingering animation DONE
    def __init__(self, game, sourcefile, anch_x, anch_y, range, frames_per_side, enemy_type):
        # Since the enemy's position is written in world_data, enemies don't need to track their position (at least in theory)
        super().__init__(game, sourcefile, anch_x, anch_y, range, frames_per_side)
        self.range = range
        #print("i made an enemy")
        #print("X: ", str(self.rect.x), "Y: ", self.rect.y)
        self.player_spotted = False
        #self.cur_room = self.game.cur_room

    def move(self):
        self.check_for_player() # this is going to check if the player is within some arbitrary range
        if self.player_spotted == True:
            self.chase_player() # this is going to use a pathfinding algorithm to chase the player
        elif self.player_spotted == False:
            self.direction_x, self.direction_y = 0, 0
            self.state_idle = True
        #self.find_pos() # this is going to find a new position to move to (within range)
        #self.move_enemy() # this is going to move the enemy to a new position after some arbitrary length of time has passed

    def check_for_player(self):
        # calculates the distance between the enemy's rect and the player's rect
        self.distance = math.hypot(self.rect.x - self.game.player.rect.x, self.rect.y - self.game.player.rect.y)
        if self.distance <= self.range:
            self.player_spotted = True
            #print("I see you!")
        else:
            self.player_spotted = False
            #print("where did you go?")

    def chase_player(self):
        # calculates the direction the enemy will move in during a chase
        self.detecX = self.game.player.rect.x - self.rect.x
        self.detecY = self.game.player.rect.y - self.rect.y
        # okay so the detection works fine, but the enemy is moving in the opposite direction
        if self.detecX < 0:
            self.direction_x = -1
            #print("you're on my left!")
        elif self.detecX > 0:
            self.direction_x = 1
            #print("you're on my right!")
        if self.detecY < 0:
            self.direction_y = -1
            #print("you're above me!")
        elif self.detecY > 0:
            self.direction_y = 1
            #print("you're below me!")
        self.approximate_direction()
        self.move_enemy()

    def approximate_direction(self):
        # stops the sprite from "vibrating" (a.k.a. oscillating)
        if self.detecX <= 2 and self.detecX >= -2:
            self.direction_x = 0
        if self.detecY <= 2 and self.detecY >= -2:
            self.direction_y = 0

    def move_enemy(self):
        # a general movement function, direction depends on whether the enemy is chasing or idle
        self.rect.x += self.direction_x * 1
        #self.check_wallsX()
        self.rect.y += self.direction_y * 1
        #self.check_wallsY()










#class Walker(Enemy)
#class Frog(Enemy)































g = MainGame()
g.game_loop()
