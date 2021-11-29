import pygame, pytmx, time, os, csv, json

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

        self.player = Player(self)
        
        # player's current position in relation to the overworld, X and Y variables
        self.ow_posX = 2
        self.ow_posY = 1
        self.cur_ow_pos = [self.ow_posX, self.ow_posY]
        self.prev_ow_pos = []
        
        self.room = Room()
        self.load_rooms()
        self.load_enemies()

        self.game_sprites = pygame.sprite.Group()
        self.game_sprites.add(self.player)
        
        for i in self.enemy_list:
            self.game_sprites.add(i)

        #print(self.ow_pos)
        #self.scr_pos_x = self.game_WIDTH/2
        #self.scr_pos_y = self.game_HEIGHT/2
        #print(self.scr_pos_x)
        #print(self.scr_pos_y)
        
        




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
        ### TO DO:
        # Add an if/else statement that will check the player's current position
        # If it doesn't match the player's previous position (moving between rooms), the function will load in a new room
        # GOAL: reduce CPU usage by avoiding having to constantly reload the exact same room
        self.cur_ow_pos = [self.ow_posX, self.ow_posY]
        if self.cur_ow_pos == self.prev_ow_pos:
            return
        self.map_image = self.room_list[self.ow_posY][self.ow_posX]
        self.prev_ow_pos = self.cur_ow_pos
        

        #self.mapid = self.room.get_room(self.ow_posX, self.ow_posY) #returns a text file that contains the name of the room
        

        #self.room_dir = os.path.join("room_bgs")
        #self.roomname = os.path.join(self.room_dir, self.mapid)
        #self.map = TileMap(self.roomname)
        #self.map_image = self.map.load_map() #loads the map into the self.map_image variable
        #self.prev_ow_pos = self.cur_ow_pos
        
    def load_rooms(self):
        # Basic setup, will use all of these later
        self.room_list = []
        self.wall_list = []
        self.enemy_list = []
        self.room_dir = os.path.join("room_bgs")

        # Void needs to be loaded in separately, to reduce memory usage (from 141MB to 70MB)
        self.voidname = os.path.join(self.room_dir, "void.tmx")
        self.void = TileMap(self.voidname)
        self.void_image = self.void.load_map()

        for f in self.room.mapdata:
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
            
        self.row_length = len(rowlist)

        
        #print(self.row_length)
        #print(self.room.mapdata)
        #print(self.room_list)
        #print(self.wall_list)
        print(self.enemy_list)

    def load_enemies(self):
        return
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
    
    def render_map(self, surface):
        tilecommand = self.tmxdata.get_tile_image_by_gid
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
                        enemy_data = []
                        #print("I found an enemy!")
                        #self.enemy_list.append(object.properties["enemy_type"])
                        enemy_data.append(object.properties["enemy_type"])
                        enemy_data.append(object.x)
                        enemy_data.append(object.y)
                        enemy_data.append(object.properties["movement_range"])
                        
                        
                        #if object.properties["enemy_type"] == "red_enemy":
                            # object.properties is a dictionary that displays pairs of data
                            #print("I found their enemy type!")
                            #print("object id: " + str(object.id))
                        self.enemy_list.append(enemy_data)
                        print(self.enemy_list)
                #if layer == "collisions":
                
                    #for x, y, width, height, tile in layer:
                    #    wall = Wall(x, y, width, height)
                    #    self.wall_list.append(wall) 
            
            elif isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = tilecommand(gid)
                    if tile:
                        surface.blit(tile, (x*self.tmxdata.tilewidth, y*self.tmxdata.tileheight))
        #print(self.wall_list)
    def load_map(self):
        temp_surface = pygame.Surface((self.width, self.height))
        self.render_map(temp_surface)
        return temp_surface



class Room():
    def __init__(self):
        with open("maplist.csv") as r:
            loaded = csv.reader(r)  # reads the file, returns idk a number?
            self.mapdata = list(loaded)  # takes that number and turns it into a list (that we can work with)
        
    def get_room(self, positionX, positionY):
        # Using the converted .csv map file (now self.room_list) + self.ow_posX + self.ow_posY, return file name of current room
        # NOTE: Getting the data directly using multiple [] parentheses causes a small bit of lag
        cur_row = self.mapdata[positionY]
        roomname = cur_row[positionX]
        roomname += ".tmx"
        ### NOTE: Rooms named void.tmx are an empty void, not meant to be accessible to the player
        return roomname
    
"""
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = "player_front1.png"
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2, HEIGHT/2)

    def update(self):
        self.rect.x += 5
"""

class Player(pygame.sprite.Sprite):
    ### TO DO:
    # As part of the move or check edge function, check if the player is touching a wall
    # If the movement would result in the player moving into a wall, cancel the movement
    def __init__(self, game):
        super().__init__()
        self.game = game
        #self.position_x = 624
        #self.position_y = 600
        self.sourcefile = "player_sprites.png"
        self.load_frames()
        self.rect = self.image.get_rect(center = (624,600))
        #self.rect.topleft = (self.position_x, self.position_y)
        #self.rect.center = (624, 600)
        self.prev_time = 0
        self.state_idle = True
        self.direction_x = 0
        self.direction_y = 0
        
        self.cur_sprlist = self.frames_down

    def load_frames(self):
        self.spritesheet = Spritesheet(self.sourcefile)
        self.frames_down = [self.spritesheet.parse_sprite("player_front1.png"), self.spritesheet.parse_sprite("player_front2.png"), self.spritesheet.parse_sprite("player_front3.png"), self.spritesheet.parse_sprite("player_front4.png")]
        self.frames_up = [self.spritesheet.parse_sprite("player_back1.png"), self.spritesheet.parse_sprite("player_back2.png"), self.spritesheet.parse_sprite("player_back3.png"), self.spritesheet.parse_sprite("player_back4.png")]
        self.frames_left = [self.spritesheet.parse_sprite("player_left1.png"), self.spritesheet.parse_sprite("player_left2.png"), self.spritesheet.parse_sprite("player_left3.png"), self.spritesheet.parse_sprite("player_left4.png")]
        self.frames_right = [self.spritesheet.parse_sprite("player_right1.png"), self.spritesheet.parse_sprite("player_right2.png"), self.spritesheet.parse_sprite("player_right3.png"), self.spritesheet.parse_sprite("player_right4.png")]
        #print(self.frames_down)
        self.cur_frame = 0
        self.image = self.frames_down[self.cur_frame]




    
    def update(self):
        # The dt is actually kind of useless, should I get rid of it?
        dt = self.game.dt
        self.cur_room = self.game.wall_list[self.game.ow_posY][self.game.ow_posX]
        self.draw_player(dt)
        self.move(dt)
        #self.reset_variables()
        #self.spr_update()
        
        
    def spr_update(self):
        #print("hey you're pressing p!")
        self.cur_frame = (self.cur_frame + 1) % len(self.frames_down)
        self.image = self.frames_down[self.cur_frame]

    def draw_player(self, dt):
        self.set_state()
        self.animate(dt)
        self.size = self.image.get_size()
        self.bigger_sprite = pygame.transform.scale(self.image, (self.size[0]*3, self.size[1]*3))
        self.image = self.bigger_sprite
        #self.game.main_screen.blit(self.bigger_sprite, (self.position_x, self.position_y))

    def set_state(self):
        # Detects whether the player is moving or not
        if self.direction_x != 0 or self.direction_y != 0:
            self.state_idle = False
            #print("player is moving")
        else:
            self.state_idle = True
            #print("player is idle")

    def animate(self, dt):
        # If the player is idle, the program doesn't iterate through the list of frames
        if self.state_idle:
            self.cur_frame = 0
        else:
            # Updates the current frame variable based on delta_time
            now = pygame.time.get_ticks()
            if now - self.prev_time > 200:
                self.prev_time = now
                self.cur_frame = (self.cur_frame + 1) % len(self.cur_sprlist)
            
                # Chooses list of frames based on where the player is facing
            if self.direction_x > 0:
                self.cur_sprlist = self.frames_right
            elif self.direction_x < 0:
                self.cur_sprlist = self.frames_left
            elif self.direction_y > 0:
                self.cur_sprlist = self.frames_down
            elif self.direction_y < 0:
                self.cur_sprlist = self.frames_up
        self.image = self.cur_sprlist[self.cur_frame]

    # Source: Christian Duenas - Pygame Game States Tutorial
    # https://www.youtube.com/watch?v=b_DkQrJxpck
    def move(self, dt):
        self.cur_room = self.game.wall_list[self.game.ow_posY][self.game.ow_posX]
        
        self.direction_x = self.game.key_d - self.game.key_a
        self.direction_y = self.game.key_s - self.game.key_w
        
        self.rect.x += self.direction_x * 3
        self.check_wallsX()

        self.rect.y += self.direction_y * 3
        self.check_wallsY()

        #print("X: " + str(self.rect.x) + " and Y: " + str(self.rect.y))
        
        #self.check_walls()
        self.check_edge()

    def check_wallsX(self):
        for wall in self.cur_room:
            if self.rect.colliderect(wall):
                if self.direction_x > 0:
                    print("collision right side")
                    self.rect.right = wall.left
                elif self.direction_x < 0:
                    print("collision left side")
                    self.rect.left = wall.right

    def check_wallsY(self):
        for wall in self.cur_room:
            if self.rect.colliderect(wall):
                if self.direction_y > 0:
                    print("collision bottom side")
                    self.rect.bottom = wall.top
                elif self.direction_y < 0:
                    print("collision top side")
                    self.rect.top = wall.bottom

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
        

class NPC(pygame.sprite.Sprite):
# you know what I can just copy a bunch of stuff from the player class
    def __init__(self, game, sourcefile, anch_x, anch_y, range, frames_per_side):
        super().__init__()
        self.game = game
        self.sourcefile = sourcefile + "_sprites.png"
        self.load_frames(sourcefile, frames_per_side)

        self.rect = self.image.get_rect(topleft = (anch_x, anch_y))

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
        return

    def draw_NPC(self):
        self.set_state()
        self.animate()
        self.size = self.image.get_size()

    def set_state(self):
        if self.direction_x != 0 or self.direction_y != 0:
            self.state_idle = False
        else:
            self.state_idle = True

    def animate(self):
        if self.state_idle:
            self.cur_frame = 0
        else:
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
        self.cur_room = self.game.wall_list[self.game.ow_posY][self.game.ow_posX]
        # I don't know what to put here right now, but this will most likely get handled by individual enemy classes
        pass

    def check_wallsX(self):
        for wall in self.cur_room:
            if self.rect.colliderect(wall):
                if self.direction_x > 0:
                    self.rect.right = wall.left
                elif self.direction_x < 0:
                    self.rect.left = wall.right

    def check_wallsY(self):
        for wall in self.cur_room:
            if self.rect.colliderect(wall):
                if self.direction_y > 0:
                    self.rect.bottom = wall.top
                elif self.direction_y < 0:
                    self.rect.top = wall.bottom

class Enemy(NPC):
    def __init__(self, game, sourcefile, anch_x, anch_y, range):
        super().__init__()
































g = MainGame()
g.game_loop()
