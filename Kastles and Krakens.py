from tkinter import Menu
import pygame, pytmx
import time as t
import math as m
import random as r
import os, csv, json

pygame.init()

pygame.display.set_caption("Kastles and Krakens")

class MainGame():
    def __init__(self):
        self.load_variables()
        self.load_rooms()

    def load_variables(self):
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
        self.key_j = False
        self.key_p = False

        self.player = Player(self, "player", 624, 600, 0, 4)
        self.battle_bg_file = pygame.image.load("battle_background.png")
        self.cur_battle_bg = pygame.Surface((1280,960))
        self.cur_battle_bg.blit(self.battle_bg_file,(0,0))
        self.game_battle_sprites = pygame.sprite.Group()
        
        # battle text variables: font, text list, etc.
        self.font = pygame.font.SysFont("arial", 40)
        self.text_list = []
        self.text_delay = 0
        self.battleloop_var = 1
        self.battleloop_phase_delay = 0

        # in-game variables: health, stamina, special points, etc.
        self.player_health = 100
        self.enemy_health = 100
        

        # player's current position in relation to the overworld, X and Y variables
        self.ow_posX = 2
        self.ow_posY = 1
        self.cur_ow_pos = [self.ow_posX, self.ow_posY]
        self.prev_ow_pos = []
        
        self.roaming = True
        #self.game_state = self.states[0]

    def get_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.key_w = True
                    self.attack(0)
                elif event.key == pygame.K_a:
                    self.key_a = True
                    self.attack(1)
                elif event.key == pygame.K_s:
                    self.key_s = True
                    self.attack(2)
                elif event.key == pygame.K_d:
                    self.key_d = True
                    self.attack(3)
                elif event.key == pygame.K_j:
                    self.attack(4)
                    self.do_menu_thing()
                elif event.key == pygame.K_k:
                    self.attack(5)
                elif event.key == pygame.K_b:
                    self.B_player.state_idle = False
                    self.B_player.state_lightattack = True
                    self.B_player.cur_frame = 0
                elif event.key == pygame.K_n:
                    self.B_player.state_idle = False
                    self.B_player.state_heavyattack = True
                    self.B_player.cur_frame = 0
                elif event.key == pygame.K_m:
                    self.B_player.defend()
                    
                elif event.key == pygame.K_p:
                    self.instakill_enemy()
                
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.key_w = False
                elif event.key == pygame.K_a:
                    self.key_a = False
                elif event.key == pygame.K_s:
                    self.key_s = False
                elif event.key == pygame.K_d:
                    self.key_d = False
                #elif event.key == pygame.K_j:
                    #self.key_j = False
                #elif event.key == pygame.K_p:
                    #self.roaming = True
    
    def change_pos(self):
        # Checks if the player has gone into a different room
        # If the player has moved between room, the function loads a new room from scratch
        self.cur_ow_pos = [self.ow_posX, self.ow_posY]
        if self.cur_ow_pos == self.prev_ow_pos:
            return
        #print(self.ow_posX, self.ow_posY)
        self.cur_room = self.world_data[self.ow_posY][self.ow_posX]
        self.cur_map_image = self.cur_room.map.load_map()
        self.cur_wall_list = self.cur_room.wall_list
        self.load_sprites()
        self.load_enemies(self.cur_room.enemy_list)
        self.prev_ow_pos = self.cur_ow_pos

    def load_rooms(self):
        self.load_mapfile()
        self.world_data = []
        self.room_dir = os.path.join("room_bgs")
        self.enemy_count = 0
        #self.voidname = os.path.join(self.room_dir, "void.tmx")
        void = Room(self, "void")

        for f in self.mapdata:
            rowlist = []
            for r in f:
                if r == "void":
                    roomdata = void
                    rowlist.append(roomdata)
                else:
                    roomdata = Room(self, r)
                    self.enemy_count += len(roomdata.enemy_list)
                    #print(roomdata.enemy_list)
                    rowlist.append(roomdata)
            self.world_data.append(rowlist)
        #print(self.world_data)
        print("Enemies left:", self.enemy_count)
        
    def load_mapfile(self):
        with open("maplist.csv") as r:
            loaded = csv.reader(r)  # reads the file, returns idk a number?
            self.mapdata = list(loaded)  # takes that number and turns it into a list (that we can work with)

    def trigger_battle_phase(self, enemy):
        self.enemy = enemy
        self.roaming = not self.roaming
        self.load_battle_sprites()

    def battle_loop(self):
        ## Battle phase has 5 different parts that cycle endlessly until one character dies
        # 1) Menu phase: player controls a menu and picks what they want to do
        # 2) Attack phase: player plays a short quick-time event while an attack animation plays
        # 3) Tally phase 1: health is updated, text appears on screen
        # 4) Defend phase: enemy attacks the player, player plays a quick-time event to defend against the attack
        # 5) Tally phase 2: health is updated, text appears on screen
        ## At the end of Tally phase 2, battle_loop loops back to the start

        ## since battle_loop() triggers every frame, integer/time-sensitive variables should be handled by individual classes to prevent a softlock

        # Phase 1
        if self.battleloop_var == 1:
            #print("phase 1")
            self.B_player.state_idle = True
            self.B_enemy.state_idle = True
        # Phase 2
        elif self.battleloop_var == 2:
            #print("phase 2")
            self.B_player.state_idle = False
            self.menu.active_attack = True
        # Phase 3
        elif self.battleloop_var == 3:
            self.B_player.state_idle = True
            self.B_player.state_lightattack = False
            self.B_player.state_heavyattack = False
            self.menu.active_attack = False
            self.draw_text()
        # Phase 4 WIP
        elif self.battleloop_var == 4:
            self.B_player.state_idle = False
            self.B_player.state_duck = True
            self.B_enemy.state_idle = False
            self.B_enemy.state_attackA = True
            #self.menu.defend()
            self.menu.active_defend = True
        # Phase 5 WIP
        elif self.battleloop_var == 5:
            self.B_player.state_idle = True
            self.B_player.state_duck = False
            self.B_enemy.state_idle = True
            self.B_enemy.state_attackA = False
            self.menu.active_defend = False
            self.draw_text()
        else:
            self.battleloop_var = 1
        pass

    def do_menu_thing(self):
        if self.battleloop_var == 1:
            self.battleloop_var += 1
            print(self.battleloop_var)
            func = self.menu.menu_list[self.menu.selection]
            func()
            

    def attack(self, input_var):
        if self.roaming:
            return
        # passed = the player is in the battle phase
        if self.B_player.state_idle:
            # the player is in the menu, picking an attack
            if input_var == 1:
                # player pressed A
                self.menu.selection -= 1
            elif input_var == 3:
                # player pressed D
                self.menu.selection += 1
        elif self.menu.active_attack or self.menu.active_defend:
            self.menu.combo.append(input_var)
            print(self.menu.combo)
            num_pos = len(self.menu.combo)-1
            if num_pos >= len(self.menu.qt_event): # the combo is over
                return
            elif input_var != self.menu.qt_event[num_pos]:
                self.menu.combo_feedback(input_var, num_pos, False) # 1 failed hit
            else:
                self.menu.combo_feedback(input_var, num_pos, True) # 1 successful hit

    def tally(self, maxdmg_enemy, maxdmg_player):
        ## first the function is going to check how many successful hits the player got
        # proportionally to the total length of the combo
        ## then the function is going to calculate the appropriate amount of damage, 
        # proportionally to the maximum possible damage (and convert it into an integer)
        # if the player got every single hit on time, blit an additional "Critical hit!" textbox and deal 1.5*damage
        ## and lastly the function will allocate an appropriate amount of damage to each character's health
        success_hits = self.menu.hits
        combo_length = len(self.menu.qt_event)
        dmg_multiplier = 1
        hit_ratio = success_hits/combo_length
        if hit_ratio == 1: # perfect combo
            dmg_multiplier = 1.5
            if maxdmg_enemy != 0: # enemy dealt critical hit
                self.animate_text("Critical hit!",3)
            else: # player hit critical hit
                self.animate_text("Critical hit!",2)
            print("perfect combo!")
        enemydmg_total = int(maxdmg_enemy*hit_ratio*dmg_multiplier)
        self.player_health += enemydmg_total
        if enemydmg_total != 0:
            self.animate_text(enemydmg_total,0) # player takes damage
        playerdmg_total = int(maxdmg_player*hit_ratio*dmg_multiplier)
        self.enemy_health += playerdmg_total
        if playerdmg_total != 0:
            self.animate_text(playerdmg_total,1) # enemy takes damage
        # check if any character has died
        if self.player_health <= 0:
            print("you died")
        elif self.enemy_health <= 0:
            print("you won!")
            self.game_battle_sprites.remove(self.B_enemy)
            self.enemy.alive = False

    def animate_text(self, damage, text_type):
        ## text types: 0-player damaged, 1-enemy damaged, 2-critical hit player, 3-critical hit enemy, 4-potion
        if damage == 0:
            return
        self.text_delay = pygame.time.get_ticks()
        colour = (200,0,0)
        if type(damage) == int and damage > 0:
            colour = (0,200,0)

        text = self.font.render(str(damage), True, colour)
        
        textwidth = text.get_size() # is this actually that important?

        if text_type == 0 or text_type == 4: # player took damage or drank a potion
            text_coords = [210,535]
        elif text_type == 1: # enemy took damage
            text_coords = [1000,450]
        elif text_type == 2: # player dealt a critical hit
            text_coords = [1000,400]
        elif text_type == 3: # enemy dealt a critical hit
            text_coords = [210,485]
        else: # default text coordinates
            text_coords = [0,0]
        textfile = Text(text, textwidth, text_coords)
        self.text_list.append(textfile)

    def draw_text(self):
        # could move this into battle_loop
        #print("drawing text")
        now = pygame.time.get_ticks()
        if self.B_player.state_idle and now - self.text_delay > 1000:
            # text only stays on screen for 1 second
            self.text_list.clear()
            self.battleloop_var += 1
            if self.battleloop_var == 4:
                self.menu.defend()
        for i in self.text_list:
            #text_coords = text[1]
            self.main_screen.blit(i.text, (i.coords[0],i.coords[1]))

    def instakill_enemy(self):
        if len(self.game_battle_sprites) == 0:
            return
        self.game_battle_sprites.remove(self.B_enemy)
        self.enemy.alive = False

    def load_battle_sprites(self):
        self.B_player = BattlePlayer(self, 100, 800)
        self.game_battle_sprites.add(self.B_player)
        self.menu = BattleMenu(self, self.player_health)
        self.game_battle_sprites.add(self.menu)
        

        if self.enemy.sourcefile == "red_enemy_sprites.png":
            self.B_enemy = BattleGoblin(self, 1000, 650)
        elif self.enemy.sourcefile == "blue_enemy_sprites.png":
            self.B_enemy = BattleSkeleton(self, 1240, 800)
        elif self.enemy.sourcefile == "fireworm_sprites.png":
            self.B_enemy = BattleWorm(self,1000, 650)
        else:
            self.B_enemy = BattleGoblin(self, 1000, 650)
        self.game_battle_sprites.add(self.B_enemy)

    def load_sprites(self):
        self.game_sprites = pygame.sprite.Group()
        self.game_sprites.add(self.player)

    def load_enemies(self, enemy_list):
        # enemy_data = [object.x, object.y, object.properties["enemy_sprite"], object.properties["enemy_type"], object.properties["movement_range"], object.properties["movement_speed"], object.id]
        for enemy in enemy_list:
            if enemy[3] == "walker":
                enemy = Walker(self, enemy[2], enemy[0], enemy[1], enemy[4], 4, enemy[5], enemy[6])
            elif enemy[3] == "charger":
                enemy = Charger(self, enemy[2], enemy[0], enemy[1], enemy[4], 8, enemy[5], enemy[6])
            self.game_sprites.add(enemy)
        #print(self.game_sprites)
        
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
            if self.roaming == True:
                self.victory_banner()
                self.main_screen.blit(self.cur_map_image, (0,0))
                self.game_sprites.update()
                self.game_sprites.draw(self.main_screen)
            else:
                self.check_for_battle()
                
                self.main_screen.blit(self.cur_battle_bg, (0,0))
                self.game_battle_sprites.update()
                self.game_battle_sprites.draw(self.main_screen)
                self.battle_loop()
                #self.draw_text()
            #print(self.roaming)
            
            
            #self.battle_sprites.draw(self.main_screen)
            #### IF overworld: x, elif battlephase: Y

            pygame.display.flip()

    def check_for_battle(self):
        # could potentially move this to battle_loop
        if len(self.game_battle_sprites) <= 2:
            #print("aight we're done")
            self.game_battle_sprites.empty()
            self.roaming = True

    def victory_banner(self):
        if self.enemy_count != 0:
            return
        self.game_sprites.empty()
        pygame.display.set_caption("Congratulations!")
        
class Text():
    def __init__(self, text, size, coords):
        #Text structure: str(actual text), [size of text], [position of text]
        self.text = text
        self.size = size
        self.coords = coords

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
        self.map.render_objects()
        
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
    
    def render_objects(self):
        #for layer in self.tmxdata.visible_layers:
            #if isinstance(layer, pytmx.TiledObjectGroup):
            # if there are multiple object layers, the program will go through every object multiple times
        for object in self.tmxdata.objects:
            # object properties: id (integer); name,type (strings); x,y,width,height (floats); object.properties (dictionary)
            # object.properties is a dictionary that displays pairs of data
            if object.type == "wall":
                # The 32px offset is no longer necessary as the current rect is 48*48px (the previous rect was 16*16px)
                temp_rect = pygame.Rect(object.x, object.y, object.width, object.height)
                self.wall_list.append(temp_rect)
            if object.type == "enemy":
                #print("I'm loading an enemy!")
                enemy_data = [object.x, object.y, object.properties["enemy_sprite"], object.properties["enemy_type"], object.properties["movement_range"], object.properties["movement_speed"], object.id]
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
        self.position_x = anch_x
        self.direction_y = 0
        self.position_y = anch_y
        self.animation_time = 0
        self.size_coef = 3 # default sprite size
        #print(self.position_x, self.position_y)

        self.load_frames(sourcefile, frames_per_side)
        self.rect = self.image.get_rect(topleft = (anch_x, anch_y), width=(self.size[0]*self.size_coef), height =(self.size[1]*self.size_coef))
        #print(self.rect.x, self.rect.y)
        #print(self.rect.height)

    def load_frames(self, sourcefile, frames_per_side):
        spritesheet = Spritesheet(self.sourcefile)
        self.frames_down = []
        self.frames_up = []
        self.frames_left = []
        self.frames_right = []
        self.frames = [self.frames_down, self.frames_up, self.frames_left, self.frames_right]
        self.sides = ["_front","_back","_left","_right"]
        side_list_pos = 0
        for framelist in self.frames:
            for frame in range(frames_per_side):
                parsed_frame = spritesheet.parse_sprite(sourcefile + self.sides[side_list_pos] + str(frame+1) + ".png")
                framelist.append(parsed_frame)
            side_list_pos += 1
        self.frames.clear()
        self.cur_frame = 0
        self.image = self.frames_down[self.cur_frame]
        self.cur_sprlist = self.frames_down
        self.size = self.image.get_size()

    def update(self):
        self.check_for_death()
        self.draw_NPC()
        self.move()

    def check_for_death(self):
        pass

    def draw_NPC(self):
        # most sprites are 48*48px
        self.set_state()
        self.animate()
        self.bigger_sprite = pygame.transform.scale(self.base_sprite, (self.size[0]*self.size_coef, self.size[1]*self.size_coef))
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
        self.base_sprite = self.cur_sprlist[self.cur_frame]

    def move(self):
        # I don't know what to put here right now, but this will most likely get handled by individual enemy classes
        pass

    def check_wallsX(self):
        #print(self.direction_x)
        for wall in self.cur_wall_list:
            if self.rect.colliderect(wall):
                #print("i'm touching a wall")
                if self.direction_x > 0:
                    #print("collision right side")
                    self.rect.right = wall.left
                    self.position_x = wall.left-self.rect.width
                elif self.direction_x < 0:
                    #print("collision left side")
                    self.rect.left = wall.right
                    self.position_x = wall.right
                elif self.direction_x == 0:
                    # This acts as a workaround for an issue with wall collision. As I do not have enough information about the way pygame's colliderect function works, this workaround may end up permanent. I don't care.
                    self.rect.right = wall.left
                    self.position_x = wall.left-self.rect.width
                    

    def check_wallsY(self):
        for wall in self.cur_wall_list:
            if self.rect.colliderect(wall):
                if self.direction_y > 0:
                    #print("collision bottom side")
                    self.rect.bottom = wall.top
                    self.position_y = wall.top-self.rect.height
                elif self.direction_y < 0:
                    #print("collision top side")
                    self.rect.top = wall.bottom
                    self.position_y = wall.bottom
                elif self.direction_y == 0:
                    self.rect.bottom = wall.top
                    self.position_y = wall.top-self.rect.height
                


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
        self.position_x += self.direction_x * 3 * self.game.dt * 60
        self.rect.x = int(self.position_x)
        #print(self.rect.x)
        self.check_wallsX()
        self.position_y += self.direction_y * 3 * self.game.dt * 60
        self.rect.y = int(self.position_y)
        #print(self.rect.y)
        self.check_wallsY()
        #print("X: ", str(self.position_x), ", Y: ", str(self.position_y))
        #print("X: ", str(self.rect.x), ", Y: ", str(self.rect.y))
        
        self.check_edge()

    def check_edge(self):
        ### TO DO:
        # Check the player's position using the self.rect variable
        if self.position_x <= 16: #player approaches left side
            self.game.ow_posX -= 1
            self.position_x = 1180
            self.rect.x = 1180
            #print("moving left")
        elif self.position_x >= 1232: #player approaches right side
            self.game.ow_posX += 1
            self.position_x = 80
            #print("moving right")
        elif self.position_y <= 8: #player approaches top side
            self.game.ow_posY -= 1
            self.position_y = 880
            self.rect.y = 880
            #print("moving up")
        elif self.position_y >= 920: #player approaches bottom side
            self.game.ow_posY += 1
            self.position_y = 48
            self.rect.y = 48
            #print("moving down")


class Enemy(NPC):
    ## TO DO:
    # wander() function to move randomly around an anchor point
    # Multiple enemy types; different move_enemy() functions
    def __init__(self, game, sourcefile, anch_x, anch_y, range, frames_per_side, movement_speed, id):
        # Since the enemy's position is written in world_data, enemies don't need to track their position (at least in theory)
        super().__init__(game, sourcefile, anch_x, anch_y, range, frames_per_side)
        self.range = int(range)
        self.anch_x = int(anch_x)
        self.anch_y = int(anch_y)
        self.id = id
        self.at_home = True
        self.player_spotted = False
        self.wandering = False
        self.wander_delay = False
        self.wander_time = 0.0
        self.charge_delay = True
        self.alive = True

    def check_for_death(self):
        if self.alive == False:
            self.kill()
            for entity in self.game.cur_room.enemy_list:
                if entity[6] == self.id:
                    self.game.cur_room.enemy_list.remove(entity)
                    self.game.enemy_count -= 1
                    print("Enemies left:", self.game.enemy_count)
            

    def move(self):
        self.check_for_home()
        self.check_for_player() # this is going to check if the player is within some arbitrary range
        if self.player_spotted == True:
            #print("I see you!")
            self.reset_timers()
            self.chase_player() # this is going to use a pathfinding algorithm to chase the player
            self.check_for_collision()
        else:
            #print("I'm walking.")
            if self.at_home == False:
                #print(self.sourcefile, "I'm going home")
                self.return_home()
            else:
                #print(self.sourcefile, "I'm home")
                self.wander()
        #self.find_pos() # this is going to find a new position to move to (within range)
        #self.move_enemy() # this is going to move the enemy to a new position after some arbitrary length of time has passed
    
    def approximate_direction(self):
        # stops the sprite from "vibrating" (a.k.a. oscillating)
        # this function needs to be expanded to include the return_home() function
        if self.new_pos[0]-3 <= self.rect.x <= self.new_pos[0]+3:
            self.direction_x = 0
            #print("X is close enough")
        if self.new_pos[1]-3 <= self.rect.y <= self.new_pos[1]+3:
            self.direction_y = 0
            #print("Y is close enough")

    def check_for_home(self):
        if ((self.anch_x - self.range) <= self.position_x <= (self.anch_x + self.range)) and ((self.anch_y - self.range) <= self.rect.y <= (self.anch_y + self.range)):
            #print("i am home")
            self.at_home = True
        else:
            #print("i am not home")
            self.at_home = False

    def check_for_player(self):
        # calculates the distance between the enemy's rect and the player's rect
        self.distance = m.hypot(self.position_x - self.game.player.rect.x, self.position_y - self.game.player.rect.y)
        if self.distance <= self.range:
            self.player_spotted = True
            #print("I see you!")
        else:
            self.player_spotted = False
            #print("where did you go?")

    def check_for_collision(self):
        if self.rect.colliderect(self.game.player) and self.alive == True:
            self.game.trigger_battle_phase(self)



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
        # this needs to be broader, likely candidate for the oscillation issue IT TOTALLY FUCKING WAS LET'S GO
        if ((self.new_pos[0]-2) <= self.rect.x <= (self.new_pos[0]+2)) and (self.new_pos[1]-2) <= self.rect.y <= (self.new_pos[1]+2):
            #print("I reached my target")
            # reset directions
            self.direction_x = 0
            self.direction_y = 0
            self.wandering = False
            if self.charge_delay == False:
                self.charge_delay = True
            self.time_delay()
        else:
            if self.player_spotted == False:
                #print("I'm wandering")
                self.wandering = True
            self.create_new_direction()
            self.approximate_direction()
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
        #print("I'm waiting")
        time_delay = 1
        dt = self.game.dt
        self.wander_time += dt
        if self.wander_time > time_delay:
            #print("it's been 1 second")
            self.reset_timers()
        else:
            self.wander_delay = True
    def reset_timers(self):
        self.wander_delay = False
        self.wander_time = 0

class Walker(Enemy):
    # Simple enemy; if the player is spotted, it will follow the player in a straight line
    # Skeleton: slow walker
    # Flying Eye: medium/fast walker
    # Goblin: fast walker
    def __init__(self, game, sourcefile, anch_x, anch_y, range, frames_per_side, movement_speed, id):
        super().__init__(game, sourcefile, anch_x, anch_y, range, frames_per_side, movement_speed, id)
        #self.mvms = movement_speed
        self.mvms = 1
        # mvmtimer limits enemies to 30FPS in order to input custom movement speeds
        self.mvmtimer = 0

    def chase_player(self):
        # marks the player's position and moves towards it
        self.new_pos = [self.game.player.rect.x, self.game.player.rect.y]
        #self.approximate_direction()
        self.move_to_new_pos()

    def move_enemy(self):
        # a general movement function, direction depends on whether the enemy is chasing or idle
        # skeleton - 0.75, eye - 1.00, goblin - 1.25/1.50?
        ### I actually kind of like the variable movement speed in the Charger function, may end up adding it here as the game gets fleshed out
        self.cur_wall_list = self.game.cur_wall_list
        """
        if self.mvmtimer == 1:
            self.position_x += self.direction_x * self.mvms * self.game.dt * 60
            self.rect.x = int(self.position_x)
            self.check_wallsX()
            self.position_y += self.direction_y * self.mvms * self.game.dt * 60
            self.rect.y = int(self.position_y)
            self.check_wallsY()
            self.mvmtimer = 0
        else:
            self.mvmtimer += 1
        """
        self.position_x += self.direction_x * self.mvms * self.game.dt * 60
        #print(int(self.game.dt * 60))
        self.rect.x = int(self.position_x)
        self.check_wallsX()
        self.position_y += self.direction_y * self.mvms * self.game.dt * 60
        self.rect.y = int(self.position_y)
        self.check_wallsY()
        
        #print("Rect_X: ", self.rect.x, "Rect_Y: ", self.rect.y)




class Charger(Enemy):
     #Complicated enemy; if the player is spotted, it will stay in place for 2 seconds, mark the player's location, and charge in a straight line
     #Mushroom/Fungus: slow charger
     #Worm: slow/medium charger, medium/large size
    def __init__(self, game, sourcefile, anch_x, anch_y, range, frames_per_side, movement_speed, id):
        super().__init__(game, sourcefile, anch_x, anch_y, range, frames_per_side, movement_speed, id)
        self.mvms = movement_speed
        self.size_coef = 4
        self.charge_time = 0.0
        #print("I made a worm")
        
    
    def load_frames(self, sourcefile, frames_per_side):
        spritesheet = Spritesheet(self.sourcefile)
        #spritelist = list(spritesheet.data["frames"])
        #print(spritelist)
        self.frames_left = []
        self.frames_right = []
        self.frames = [self.frames_left, self.frames_right]
        self.sides = ["_left","_right"]
        side_list_pos = 0
        for framelist in self.frames:
            for frame in range(frames_per_side):
                parsed_frame = spritesheet.parse_sprite(sourcefile + self.sides[side_list_pos] + str(frame+1) + ".png")
                framelist.append(parsed_frame)
            side_list_pos += 1
        self.frames.clear()
        self.cur_frame = 0
        self.image = self.frames_right[self.cur_frame]
        self.cur_sprlist = self.frames_right
        self.size = self.image.get_size()

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
        self.base_sprite = self.cur_sprlist[self.cur_frame]

    def move_enemy(self):
        # a general movement function, direction depends on whether the enemy is chasing or idle
        if self.player_spotted == True:
            mvms = self.mvms*2
        else:
            mvms = self.mvms
        self.position_x += self.direction_x * mvms * self.game.dt * 60
        self.rect.x = int(self.position_x)
        self.position_y += self.direction_y * mvms * self.game.dt * 60
        self.rect.y = int(self.position_y)
        #print("X: ", self.rect.x, self.position_x, ";Y: ", self.rect.y, self.position_y)

    def chase_player(self):
        #print("I see you!")
        if self.charge_delay == True:
            self.check_for_charge()
            self.play_charging_animation()
        else:
            self.charge()

    def play_charging_animation(self):
        pass


    def check_for_charge(self):
        self.set_sprite()
        dt = self.game.dt
        self.charge_time += dt
        if self.charge_time > 1.5:
            self.charge_delay = False
            self.charge_time = 0
            self.new_pos = [self.game.player.rect.x, self.game.player.rect.y]
            #print(self.new_pos)
            #print("I'm done charging")
        else:
            self.charge_delay = True
            #print("I'm still charging!")
    
    def set_sprite(self):
        if self.game.player.position_x - self.position_x < 0:
            self.cur_sprlist = self.frames_left
        else:
            self.cur_sprlist = self.frames_right
        self.base_sprite = self.cur_sprlist[3]

    def charge(self):
        self.move_to_new_pos()

    

#class Frog(Enemy):
    # Complicated enemy; if the player is spotted, it will mark the player's direction and jump towards them
    # Do I actually want to do this one? idk how it'd work with sprites
    # not entirely necessary, 2 enemy types is enough
    # Slime?

class BattleNPC(pygame.sprite.Sprite):
    def __init__(self, game, anch_x, anch_y):
        # this is the basic battleNPC class
        # this class should contain basic functions that load frames, play idle animations, contain basic attack functions (that then blossom out based on enemy types)
        super().__init__()
        self.game = game
        self.sourcefile = "goblin"
        self.anch_x = anch_x
        self.anch_y = anch_y
        # NOTE self.anch_y should be stable, it should symbolise the "ground" level for battleNPC objects

        self.state_idle = True
        self.direction_x = 0
        self.direction_y = 0
        self.animation_time = 0
        self.delay_var = 0
        self.size_coef = 6
        self.frame_delay = 200

        self.state_duck = True
        self.state_roll = False      

    def load_frames(self):
        spritesheet = Spritesheet(self.sourcefile+"_idle.png")
        spritelist = list(spritesheet.data["frames"])
        #print(spritelist)
        self.frames_idle = []
        self.frames_move_left = []
        self.frames_move_right = []
        self.frames_attackA = []
        self.frames_attackB = []
        self.frames_attackC = []
        self.frames_hit = []
        self.frames_death = []
        self.frames_duck = []
        self.frames_roll = []
        frames = [self.frames_idle, self.frames_move_left, self.frames_move_right, self.frames_attackA, self.frames_attackB, self.frames_attackC, self.frames_hit, self.frames_death, self.frames_duck, self.frames_roll]
        framesuffixes = ["_idle", "_move_left", "_move_right", "_attackA", "_attackB", "_attackC", "_hit", "_death", "_duck", "_roll"]
        suffvar = 0
        for framelist in frames:
            frame_prefix = self.sourcefile+framesuffixes[suffvar]
            #print(frame_prefix)
            max_var = int(0)
            counting_var = 1
            for i in spritelist:
                if frame_prefix in i:
                    inumtemp = i.replace(frame_prefix, "")
                    inum = inumtemp.replace(".png", "")
                    if int(inum) > int(max_var):
                        max_var = inum
            while len(framelist) != int(max_var):
                for i in spritelist:
                    if i == frame_prefix + str(counting_var) + ".png":
                        parsed_frame = spritesheet.parse_sprite(i)
                        framelist.append(parsed_frame)
                        counting_var+=1
            suffvar+=1
        #print(frames)
        frames.clear()
        self.cur_frame = 0
        self.image = self.frames_idle[self.cur_frame]
        self.cur_sprlist = self.frames_idle
        self.size = self.image.get_size()

    def update(self):
        self.set_state()
        self.draw_BattleNPC()
    
    def draw_BattleNPC(self):
        self.set_state()
        self.animate()
        self.bigger_sprite = pygame.transform.scale(self.base_sprite, (self.size[0]*self.size_coef, self.size[1]*self.size_coef))
        self.calibrate_x()
        self.rect.y = self.anch_y - self.size[1]*self.size_coef # sets a stable ground level by changing the sprite's Y coordinate based on its height
        self.flip_sprite()
        
        self.image = self.bigger_sprite
        
    def calibrate_x(self):
        pass

    def flip_sprite(self):
        pass

    def set_state(self):
        pass
    
    def animate(self):
        if self.state_idle:
            #print(self.sourcefile, "i think i'm idle!")
            self.cur_sprlist = self.frames_idle
        now = pygame.time.get_ticks()
        if now - self.animation_time > self.frame_delay:
            self.animation_time = now
            self.cur_frame = (self.cur_frame + 1) % len(self.cur_sprlist)
            #print(self.sourcefile, self.cur_frame)
        self.base_sprite = self.cur_sprlist[self.cur_frame]
        self.size = self.base_sprite.get_size()
        

class BattlePlayer(BattleNPC):
    def __init__(self, game, anch_x, anch_y):
        super().__init__(game, anch_x, anch_y)
        self.sourcefile = "knight"
        self.size_coef = 6
        self.load_frames()
        self.rect = self.image.get_rect(bottomleft = (anch_x, anch_y), width = self.size[0], height = self.size[1])

        self.state_lightattack = False
        self.lightattack_states = [self.frames_move_right, self.frames_attackA, self.frames_move_left]
        self.lightattack_cur = 0

        self.state_heavyattack = False
        self.heavyattack_states = [self.frames_move_right, self.frames_roll, self.frames_move_right, self.frames_attackC, self.frames_move_left]
        self.heavyattack_cur = 0

    def set_state(self):
        if self.state_idle:
            self.cur_sprlist = self.frames_idle
        else:
            if self.state_lightattack:
                self.light_attack()
            elif self.state_heavyattack:
                self.heavy_attack()
            elif self.state_duck or self.state_roll:
                self.defend()
            else:
                self.cur_sprlist = self.frames_idle

        # self.state_idle = True
        # if self.state_idle == False: check if the player is attacking or being attacked

    def light_attack(self):
        #this is the light attack animation
        #player moves to the enemy, swipes and moves back
        #print("I used my light attack!")
        self.cur_sprlist = self.lightattack_states[self.lightattack_cur]
        if self.lightattack_cur == 0:
            if self.rect.x <= 750:
                self.rect.x += 4
            else:
                self.rect.x = 750
                self.lightattack_cur+=1
                self.cur_frame = 0
        elif self.lightattack_cur == 1:
            if self.cur_frame == 3:
                self.lightattack_cur+=1
                self.cur_frame = 0
        elif self.lightattack_cur == 2:
            if self.rect.x >= 100:
                self.rect.x -=4
            else:
                self.rect.x = 100
                self.cur_frame = 0
                self.lightattack_cur = 0
                self.game.battleloop_var += 1
                self.game.tally(0,-50)
        self.image = self.cur_sprlist[self.cur_frame]
        

    def heavy_attack(self):
        #this is the heavy attack animation
        #player rolls to the enemy, does a double-swipe, and runs back
        self.cur_sprlist = self.heavyattack_states[self.heavyattack_cur]
        if self.heavyattack_cur == 0:
            if self.rect.x <= 200:
                self.rect.x += 4
            else:
                self.rect.x = 200
                self.heavyattack_cur+=1
                self.cur_frame = 0
                self.frame_delay = 65
        elif self.heavyattack_cur == 1:
            self.rect.x += 4
            if self.cur_frame == 11:
                self.heavyattack_cur+=1
                self.cur_frame = 0
                self.frame_delay = 200
        elif self.heavyattack_cur == 2:
            if self.rect.x <= 750:
                self.rect.x += 4
            else:
                self.rect.x = 750
                self.heavyattack_cur+=1
                self.cur_frame = 0
                self.frame_delay = 100
        elif self.heavyattack_cur == 3:
            if self.cur_frame == 9:
                self.heavyattack_cur+=1
                self.cur_frame = 0
                self.frame_delay = 200
        elif self.heavyattack_cur == 4:
            if self.rect.x >= 100:
                self.rect.x -= 4
            else:
                self.rect.x = 100
                self.cur_frame = 0
                self.heavyattack_cur = 0
                self.game.battleloop_var += 1
                self.game.tally(0,-100)
        self.image = self.cur_sprlist[self.cur_frame]
        

    def defend(self):
        #this is the defend animation
        #2 variations based on enemy type: either a simple ducking motion, or a parry+riposte
        pass
        #print("I'm defending!")
        #self.state_idle = False
        #self.cur_frame = 0
        #if self.state_duck:
        #    self.cur_sprlist = self.frames_duck
        #else:
        #    self.cur_sprlist = self.frames_roll
        #self.image = self.frames_idle[self.cur_frame]
        





class BattleEnemy(BattleNPC):
    def __init__(self, game, anch_x, anch_y):
        super().__init__(game, anch_x, anch_y)
        self.game.enemy_health = 150
        self.state_idle = True
        self.state_attackA = False
        self.state_attackB = False
        self.pos_x = self.anch_x

    def flip_sprite(self):
        # this is dumb, just delete it
        pass

    def calibrate_x(self):
        # maybe add self.pos_x to battleplayer?
        self.rect.x = self.pos_x - self.size[0]*self.size_coef
        


    def set_state(self):
        if self.state_idle:
            self.cur_sprlist = self.frames_idle
        else:
            if self.state_attackA:
                self.attackA()
            elif self.state_attackB:
                self.attackB()

    def attackA(self):
        pass

    def attackB(self):
        pass



class BattleGoblin(BattleEnemy):
    def __init__(self, game, anch_x, anch_y):
        super().__init__(game, anch_x, anch_y)
        self.sourcefile = "goblin"
        self.size_coef = 4
        self.game.enemy_health = 125
        self.load_frames()
        self.rect = self.image.get_rect(bottomleft = (anch_x, anch_y), width = self.size[0], height = self.size[1])
        

class BattleSkeleton(BattleEnemy):
    def __init__(self, game, anch_x, anch_y):
        super().__init__(game, anch_x, anch_y)
        self.sourcefile = "skeleton"
        self.size_coef = 6
        self.game.enemy_health = 175
        self.load_frames()
        self.rect = self.image.get_rect(bottomleft = (anch_x, anch_y), width = self.size[0], height = self.size[1])

        self.attackA_states = [self.frames_move_left, self.frames_attackA, self.frames_attackB, self.frames_move_right]
        self.attackA_cur = 0

    def attackA(self):
        self.cur_sprlist = self.attackA_states[self.attackA_cur]
        if self.attackA_cur == 0:
            if self.pos_x >= 600:
                # this could be higher, 600 is pretty good
                self.pos_x -= 4
            else:
                self.pos_x = 600
                self.attackA_cur+=1
                self.cur_frame = 0
                self.frame_delay = 100
        elif self.attackA_cur == 1:
            if self.cur_frame == 7:
                self.attackA_cur+=1
                self.cur_frame = 0
                self.frame_delay = 500 # THIS animation delay works
                #self.delay_var = pygame.time.get_ticks()
        elif self.attackA_cur == 2:
            # maybe add a small delay after the second swipe? to increase the impact
            if self.cur_frame == 1:
                self.frame_delay = 100
            elif self.cur_frame == 6:
                print("delay")
                self.frame_delay = 700
            elif self.cur_frame == 7:
                self.attackA_cur+=1
                self.cur_frame = 0
                self.frame_delay = 200 # THIS animation delay doesn't work for some reason
        elif self.attackA_cur == 3:
            if self.pos_x <= 1240:
                self.pos_x += 4
                #print(self.rect.x)
            else:
                self.pos_x = 1240
                self.cur_frame = 0
                self.attackA_cur = 0
                self.game.battleloop_var += 1
                self.game.tally(-20,0)
        self.image = self.cur_sprlist[self.cur_frame]


class BattleWorm(BattleEnemy):
    def __init__(self, game, anch_x, anch_y):
        super().__init__(game, anch_x, anch_y)
        self.sourcefile = "fireworm"
        self.size_coef = 6
        self.game.enemy_health = 250
        self.load_frames()
        self.rect = self.image.get_rect(bottomleft = (anch_x, anch_y), width = self.size[0], height = self.size[1])

class BattleMenu(pygame.sprite.Sprite):
    def __init__(self, game, player_health):
        super().__init__()
        self.game = game
        self.player_health = player_health
        self.load_variables()
        self.load_spritevariables()
    
    def load_variables(self):
        self.selection = 0
        self.menu_list = [self.attack, self.heavy_attack, self.items]
        self.len_var = len(self.menu_list)
        self.font = self.game.font
        self.active_attack = False
        self.active_defend = False


    def load_spritevariables(self):
        self.rect = pygame.Rect(50, 50, 1180, 100)
        self.image = pygame.Surface((1180, 100))
        self.create_buttons()
        self.create_text()
        self.load_qtbuttons()
        
        #self.balls = pygame.image.load("heavy rock.png")

    def create_buttons(self):
        self.button_attack = pygame.Surface((250, 50))
        self.button_heavyattack = pygame.Surface((250, 50))
        self.button_items = pygame.Surface((250, 50))
        self.button_list = [self.button_attack, self.button_heavyattack, self.button_items]
        for i in self.button_list:
            i.fill((100,100,100))

    def load_qtbuttons(self):
        spritesheet = Spritesheet("key_assets.png")
        spritelist = list(spritesheet.data["frames"])
        self.keys_correct = []
        self.keys_default = []
        self.keys_failed = []
        frames = [self.keys_correct, self.keys_default, self.keys_failed]
        framesuffixes = ["_correct", "_default", "_failed"]
        suffvar = 0
        for framelist in frames:
            frame_prefix = "key"+framesuffixes[suffvar]
            max_var = int(0)
            counting_var = int(0)
            for i in spritelist:
                if frame_prefix in i:
                    inumtemp = i.replace(frame_prefix, "")
                    inum = inumtemp.replace(".png", "")
                    if int(inum) > int(max_var):
                        max_var = inum
            while len(framelist) != int(max_var)+1:
                for i in spritelist:
                    if i == frame_prefix + str(counting_var) + ".png":
                        parsed_frame = spritesheet.parse_sprite(i)
                        pf_size = parsed_frame.get_size()
                        bigger_frame = pygame.transform.scale(parsed_frame, (pf_size[0]*2,pf_size[1]*2))
                        framelist.append(bigger_frame)
                        counting_var+=1
            suffvar+=1
        frames.clear()

    def create_qtbuttons(self, qt_list):
        self.key_sprites = []
        for i in qt_list:
            key = self.keys_default[i]
            self.key_sprites.append(key)
        self.key_num = len(self.key_sprites)
        self.gap = 1080//(self.key_num-1) # gap is an integer
        

    def create_text(self):
        name_list = ["Attack", "Heavy Attack", "Potion"]
        self.text_list = []
        for i in name_list:
            text = self.font.render(i, True, (0,0,0))
            textwidth = text.get_size()
            self.text_list.append(text)
            self.text_list.append(textwidth)

    def update(self):
        self.image.fill((30,55,150))
        self.pick_action()
        self.paint_buttons()

    def paint_buttons(self):
        if self.active_attack or self.active_defend:
            var = 18
            for key in self.key_sprites:
                size = key.get_size()
                self.image.blit(key, (var,82-size[1])) # second variable sets a ground level for every key
                var += self.gap
        else:
            var = 100
            text_var = 0
            for i in self.button_list:
                if i == self.button_list[self.selection]:
                    i.fill((100,100,100))
                else:
                    i.fill((200,200,200))
                pygame.draw.rect(i, (200,200,200), (5,5,240,40))
                self.image.blit(i, (var,25))
                text = self.text_list[text_var]
                t_size = self.text_list[text_var+1]
                self.image.blit(text, (var+125-t_size[0]/2, 50-t_size[1]/2))
                var += 365
                text_var+=2
        
    def pick_action(self):
        # this isn't going to work, it's better to just call the function through MainGame itself
        if self.selection < 0:
            self.selection = self.len_var - 1
        elif self.selection == self.len_var:
            self.selection = 0
        

    def attack(self):
        # creates a random combo of inputs
        #self.active_attack = True
        self.hits = 0
        self.combo = []
        self.qt_event = [3,0,3,4,5,1] # D W D J K A
        #self.qt_event = []
        #for i in range(6):
        #    x = r.randint(0,5)
        #    self.qt_event.append(x)
        self.create_qtbuttons(self.qt_event)
        self.game.B_player.state_lightattack = True
        
        print("I attack!")

    def heavy_attack(self):
        #self.active_attack = True
        self.hits = 0
        self.combo = []
        self.qt_event = [3,3,2,2,3,4,5,4,1] # ddssdjkja
        self.create_qtbuttons(self.qt_event)
        self.game.B_player.state_heavyattack = True
        
        print("I heavy attack!")

    def defend(self):
        print("I defend!")
        self.active_defend = True
        self.hits = 0
        self.combo = []
        self.qt_event = [1,1,2,3,2,1]
        self.create_qtbuttons(self.qt_event)
        ## There is no one defend state, there's a roll/duck animation
        #self.game.B_player.state_defend = True
        
        
        pass

    def items(self):
        self.game.tally(50,0)
        print("I picked items")

    def combo_feedback(self, button_val, button_pos, hit):
        # button_val is in integer that represents the value of the button
        # button_pos is an integer that represents the position of the button
        # hit is a bool that checks if the player successfully hit the button
        ## this function will 
        if hit:
            self.key_sprites[button_pos] = self.keys_correct[button_val]
            self.hits+=1
            #print("nice")
        else:
            self.key_sprites[button_pos] = self.keys_failed[button_val]
            #print("combo failed!")
        
        




























g = MainGame()
g.game_loop()
