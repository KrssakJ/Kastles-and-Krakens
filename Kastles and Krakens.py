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
        
        self.player = Player(self)
        
        # player's current position in relation to the overworld, X and Y variables
        self.ow_posX = 2
        self.ow_posY = 1
        self.cur_ow_pos = [self.ow_posX, self.ow_posY]
        self.prev_ow_pos = []
        
        self.room = Room()
        
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
                
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.key_w = False
                elif event.key == pygame.K_a:
                    self.key_a = False
                elif event.key == pygame.K_s:
                    self.key_s = False
                elif event.key == pygame.K_d:
                    self.key_d = False
    
    def change_pos(self):
        ### TO DO:
        # Add an if/else statement that will check the player's current position
        # If it doesn't match the player's previous position (moving between rooms), the function will load in a new room
        # GOAL: reduce CPU usage by avoiding having to constantly reload the exact same room
        self.cur_ow_pos = [self.ow_posX, self.ow_posY]
        if self.cur_ow_pos == self.prev_ow_pos:
            return
        else:
            self.mapid = self.room.get_room(self.ow_posX, self.ow_posY) #returns a text file that contains the name of the room
            self.room_dir = os.path.join("room_bgs")
            self.roomname = os.path.join(self.room_dir, self.mapid)
            self.map = TileMap(self.roomname)
            self.map_image = self.map.load_map() #loads the map into the self.map_image variable
        self.prev_ow_pos = self.cur_ow_pos
        
        
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
            self.player.draw_player(self.player.position_x, self.player.position_y)
            pygame.display.update()

class Spritesheet():
    def __init__(self, filename, spritesource):
        ### TO DO:
        # Currently only works if every sprite has their individual folder with their spritesheet
        # May need to create a single, fixed folder that contains EVERY spritesheet in the game
        self.filename = filename
        self.sprite_dir = os.path.join(str(spritesource))
        self.sprite_sheet = pygame.image.load(os.path.join(self.sprite_dir, self.filename)).convert()
        self.meta_data = self.filename.replace("png","json")
        with open(self.meta_data) as f:
            self.data = json.load(f)
        f.close()

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface((width, height))
        # alfa kanal pro sprite
        sprite.set_colorkey((0,0,0))
        sprite.blit(self.sprite_sheet, (0,0), (x,y,width,height))
        return sprite
        
    def parse_sprite(self, name):
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
        tm = pytmx.load_pygame(mapfile, pixelalpha = True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm
    
    def render_map(self, surface):
        tilecommand = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = tilecommand(gid)
                    if tile:
                        surface.blit(tile, (x*self.tmxdata.tilewidth, y*self.tmxdata.tileheight))
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
        cur_row = self.mapdata[positionY]
        roomname = cur_row[positionX]
        roomname += ".tmx"
        ### NOTE: Rooms named void.tmx are an empty void, not meant to be accessible to the player
        return roomname

class Player(pygame.sprite.Sprite):
    ### TO DO:
    # The player is invisible for some reason idk why (but the position still updates)
    def __init__(self, game):
        super().__init__()
        self.spritesheet = Spritesheet("player_sprites.png","player")
        self.sprite_list = [self.spritesheet.parse_sprite("player_front1.png"), self.spritesheet.parse_sprite("player_front2.png"), self.spritesheet.parse_sprite("player_front3.png"), self.spritesheet.parse_sprite("player_front4.png")]
        self.spr_list_pos = 0
        self.game = game
        self.position_x = 624
        self.position_y = 600
        #self.player_dir = os.path.join("player")
        #self.player_sprite = pygame.image.load(os.path.join(self.player_dir, "player_front1.png")).convert_alpha()
        self.player_sprite = self.sprite_list[self.spr_list_pos] # THIS is what's causing the player to go invisible
        #self.player_sprite.set_colorkey((0,0,0))
        
    
    
    # Source: Christian Duenas - Pygame Game States Tutorial
    # https://www.youtube.com/watch?v=b_DkQrJxpck
    def move(self, dt):
        direction_x = self.game.key_d - self.game.key_a
        direction_y = self.game.key_s - self.game.key_w
        
        self.position_x += 60 * dt * direction_x * 3
        self.position_y += 60 * dt * direction_y * 3
       
    def check_edge(self):
        if self.position_x <= 16: #player approaches left side
            self.game.ow_posX -= 1
            self.position_x = 1180
        elif self.position_x >= 1232: #player approaches right side
            self.game.ow_posX += 1
            self.position_x = 80
        elif self.position_y <= 16: #player approaches top side
            self.game.ow_posY -= 1
            self.position_y = 880
        elif self.position_y >= 912: #player approaches bottom side
            self.game.ow_posY += 1
            self.position_y = 80
       
        
    
    def draw_player(self, localx, localy):
        dt = self.game.dt
        self.size = self.player_sprite.get_size()
        self.bigger_sprite = pygame.transform.scale(self.player_sprite, (self.size[0]*3, self.size[1]*3))
        current_pos = self.move(dt)
        self.check_edge()
        self.game.main_screen.blit(self.bigger_sprite, (self.position_x, self.position_y))

#class NPC():
# yeah, let's come back to this LATER






































g = MainGame()
g.game_loop()
