import pygame, pytmx, time, os, csv

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
        self.ow_posX = 1
        self.ow_posY = 0
        
        self.room = Room(self.ow_posX, self.ow_posY)
        
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
                """
                if event.key == pygame.K_UP:
                    self.ow_pos -= 3
                elif event.key == pygame.K_DOWN:
                    self.ow_pos += 3
                elif event.key == pygame.K_LEFT:
                    self.ow_pos -= 1
                elif event.key == pygame.K_RIGHT:
                    self.ow_pos += 1
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
        # Split self.ow_pos into self.ow_posX and self.ow_posY
        
        self.mapid = self.room.get_room(self.ow_posX, self.ow_posY) #returns a text file that contains the name of the room
        self.map = TileMap(os.path.join(self.mapid))
        self.map_image = self.map.load_map() #loads the map into the self.map_image variable
        
        
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
            pygame.display.flip()
"""
class Spritesheet():
    def __init__(self, filename):
        self.filename = filename
        self.sprite_sheet = pygame.image.load(filename).convert()

    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface((width, height))
        # alfa kanal pro sprite
        sprite.set_colorkey((0,0,0))
        sprite.blit(self.sprite_sheet, (0,0), (x,y,width,height))
        return sprite       
"""
        
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
    ### TO DO:
    # Add a hook that will load the .csv map file upon initilization
    # Futher tasks: get_room()
    def __init__(self, positionX, positionY):
        self.positionX = positionX
        self.positionY = positionY
#       self.mapid = mapid
        with open("maplist.csv") as r:
            loaded = csv.reader(r)  # reads the file, returns idk a number?
            self.mapdata = list(loaded)  # takes that number and turns it into a list (that we can work with)
        
    def get_room(self, positionX, positionY):
        ### TO DO:
        # Using the converted .csv map file (now self.room_list) + self.ow_posX + self.ow_posY, return file name of current room
        cur_row = self.mapdata[positionY]
        roomname = cur_row[positionX]
        roomname += ".tmx"
        return roomname

class Player():
    def __init__(self, game):
        self.game = game
        self.position_x = 624
        self.position_y = 600
        self.player_dir = os.path.join("player")
        self.player_sprite = pygame.image.load(os.path.join(self.player_dir, "player_front1.png")).convert_alpha()
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
        player_image = self.game.main_screen.blit(self.bigger_sprite, (self.position_x, self.position_y))








































g = MainGame()
g.game_loop()
