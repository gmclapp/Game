import pygame
import json
import constants
import random
import component
import os

game_obj = None

def init_classes(GO):
    global game_obj
    game_obj = GO
    
class loot_table():
    def __init__(self, table):
        '''This class is initiated with a text file that has a list of
        dictionaries where each list element is an item. Each item is defined
        by a dictionary with keywords "name" and "rarity." from that data
        the loot table is constructed.'''
        self.table = table
        with open(table,"r") as f:
            self.loot_list = json.load(f)

        self.rarity_sum = 0  
        prev_max = -1
        for item in self.loot_list:
            self.rarity_sum += int(item["rarity"])
            item["range_min"] = prev_max+1
            item["range_max"] = prev_max+int(item["rarity"])
            prev_max = item["range_max"]

    def roll(self):
        result = random.randint(0,self.rarity_sum-1)
        print("roll: {}".format(result))
        for item in self.loot_list:
            if item["range_min"]<=result<=item["range_max"]:
                return(item)
        print("Invalid roll!")
            
class struct_tile():
    def __init__(self, tile_number):
        self.serial_no = tile_number
        with open("data\\tiles.txt","r") as f:
            tile_list = json.load(f)
            for t in tile_list:
                if t["serial_no"] == self.serial_no:
                    self.name = t["name"]
                    self.block_path = t["block_path"]
                    self.art = pygame.image.load(t["art"])

    def attach_to_mouse(self):
        game_obj.vars["mouse_attachment"] = self
        print("Attached {} to mouse.".format(self.name))

    def set_xy(self,x,y):
        self.x = x
        self.y = y
        
    def draw(self, surf):
        surf.blit(self.art, (self.x, self.y))
            

class element():
    def __init__(self,
                 x,
                 y,
                 scene,
                 sprite=None,
                 player=False,
                 ai=None,
                 name=None,
                 storage=None):
        
        self.x = x
        self.y = y
        self.scene = scene
        self.sprite = sprite
        self.clicked = False

        self.player = player
        
        self.ai = ai
        if ai:
            ai.owner = self
        self.name = name

        
        self.storage = storage
        if storage:
            storage.owner = self
            
    def draw(self,surf):
        if self.scene == game_obj.vars["current_scene"]:
            surf.blit(self.sprite, (self.x*constants.RES, self.y*constants.RES))
            if self.clicked:
                surf.blit(constants.S_SELECTOR, (self.x*constants.RES, self.y*constants.RES))
            

    def is_clicked(self,x,y):
        dx = (self.x+0.5)*constants.RES - x
        dy = (self.y+0.5)*constants.RES - y

        if (dx**2 + dy**2 ) < (constants.RES/2)**2:
            self.clicked = True
        else:
            self.clicked = False
            
class obj_item(element):
    def __init__(self, x,y, scene,serial_num, inst_name,sprite):
        super().__init__(x,y,scene,sprite)
        self.sn = serial_num
        self.inst_name = inst_name
        self.base_atk = 0.0
        self.base_def = 0.0

    def set_implicit(self, affected_stat, stat_val):
        if affected_stat == "attack":
            self.base_atk += float(stat_val)
        elif affected_stat == "defense":
            self.base_def += float(stat_val)
        else:
            print("Invalid value for affected stat")

    def deposit(self,destination):
        if len(destination.storage.inventory)<destination.storage.max_slots:
            destination.storage.inventory.append(self)
            self.container = destination
            return(True)
        else:
            game_obj.log_message("Inventory full!")
            return(False)
        
    def move(self,source,destination):
        if len(destination.storage.inventory)<destination.storage.max_slots:
            destination.storage.inventory.append(item)
            source.storage.inventory.remove(item)
            self.container=destination
            
            return(True)
        else:
            game_obj.log_message("Inventory full!")
            return(False)

    def set_xy(self,mx,my):
        self.x = mx
        self.y = my
        
class actor(element):
    def move(self, dx, dy):
        try:
            dest_tile = game_obj.scene_list[game_obj.vars["current_scene"]]["map"][self.y+dy][self.x+dx]
            for t in game_obj.tile_list:
                if t.serial_no == dest_tile:
                    break
                else:
                    pass
            if not t.block_path:
                self.x += dx
                self.y += dy
                return(True)
                
            else:
                game_obj.log_message("Can't walk there. It's a {}.".format(t.name))
                return(False)
                
                
        except IndexError:
            print("Tile out of range")
            return(False)
            
            
        
class prop(element):
    def __init__(self,x,y,scene,prop_type,state,sprite=None,player=False,ai=None,storage=None):
        super().__init__(x,y,scene,sprite=sprite,player=player,ai=ai,storage=storage)
        self.state = state
        self.prop_type = prop_type
        
    def interact(self):
        
        self.update()
        
        # This value is checked in order to determine if a player turn is complete
        return(True)

    def update(self):
        pass

class container(prop):
    def interact(self,actor):
        if self.y == actor.y - 1 and self.x == actor.x:
            if self.state == "closed":
                self.state = "open"
            elif self.state == "open":
                self.state = "closed"
            self.update()
            return(True)
        else:
            game_obj.log_message("You must stand in front of {} to interact with it.".format(self.prop_type))
            return(False)
            
    def update(self):
        if self.prop_type == "chest" and self.state == "closed":
            for i in self.storage.inventory:
                print(i)
            self.sprite = constants.S_CHEST
        elif self.prop_type == "chest" and self.state == "open":
            self.sprite = constants.S_CHEST_OPEN

    def draw(self,surf):
        super().draw(surf)
        if self.state == "open":
            surf.blit(self.storage.inv_art,(self.storage.anchor_x,
                                            self.storage.anchor_y))
            for n, i in enumerate(self.storage.inventory):
                surf.blit(i.sprite,(self.storage.anchor_x + (n%4)*(constants.RES + 3)+4,
                                    int(n/4)*(constants.RES+3) + self.storage.anchor_y + 4))
        elif self.state == "closed":
            pass
        else:
            print("invalid container state")

    def is_clicked(self,x,y):
        super().is_clicked(x,y)
        dx = x-self.storage.anchor_x
        dy = y-self.storage.anchor_y
        if 0 < dx < self.storage.width and 0 < dy < self.storage.height:
            print("dx: {}\ndy: {}".format(dx,dy))
            slot_click = int(dx/constants.RES) + 4*int(dy/constants.RES)
            print("Clicked slot {}".format(slot_click))
            if game_obj.vars["mouse_attachment"]:
                print("There's a thing on the mouse.")
            else:
                game_obj.vars["mouse_attachment"] = self.storage.inventory[slot_click]
                self.storage.inventory.pop(slot_click)
        
##
##        if (dx**2 + dy**2 ) < (constants.RES/2)**2:
##            self.clicked = True
##        else:
##            self.clicked = False

class portal(prop):
    def __init__(self,x,y,scene,prop_type,state,dest_scene,dest_x,dest_y,sprite=None,player=False,ai=None):
        
        super().__init__(x,y,scene,prop_type,state,sprite,player,ai)
        self.dest_scene = dest_scene
        self.dest_x = dest_x
        self.dest_y = dest_y
        
    def interact(self,actor):
        if self.y == actor.y - 1 and self.x == actor.x:
            if self.state == "closed":
                self.state = "open"
            elif self.state == "open":
                self.state = "closed"
            self.travel(actor)
            return(True)
        else:
            game_obj.log_message("You must stand in front of {} to interact with it.".format(self.prop_type))
            return(False)

    def travel(self,actor):
        game_obj.vars["current_scene"] = self.dest_scene
        game_obj.get_props()
        actor.x = self.dest_x
        actor.y = self.dest_y
        actor.scene = self.dest_scene
        
    def update(self):
        if self.prop_type == "door" and self.state == "closed":
            self.sprite = constants.S_DOOR
        elif self.prop_type == "door" and self.state == "open":
            self.sprite = constants.S_DOOR_OPEN
        
class game_object():
    def __init__(self):
        self.SURFACE_MAIN = None
        self.font = pygame.font.Font(None,32)
        self.actor_list = []
        self.prop_list = []
        self.scene_list = []
        self.tile_list = []
        self.vars = {"cheat_codes": False,
                     "cheat_text": '',
                     "page":1,
                     "debug": False,
                     "turn": 0,
                     "current_scene":0,
                     "serial_number_counter":0,
                     "game_mode":"normal",
                     "mouse_attachment":None,
                     "messages":["Hello world."]}
        

    def load(self):
        print("Loading tile data...")
        # Load the data which tells the game what art to render and what
        # The properties of a tile are given a serial number; contains no
        # map data.
        with open("data\\tiles.txt","r") as f:
            tile_data = json.load(f)
            num_tiles = len(tile_data)
        for i in range(num_tiles):
            self.tile_list.append(struct_tile(i))

        # Load the map data, and append tile structures to a list of scenes
        print("Loading scene...")
        for i in range(len([f for f in os.listdir("scenes")])):
            path = "scenes\\" + str(i) + ".txt"
            with open(path,"r") as f:
                self.scene_list.append(json.load(f))

    def save(self):
        for i in range(len([f for f in os.listdir("scenes")])):
            path = "scenes\\" + str(i) + ".txt"
            with open(path,"w") as f:
                f.write(json.dumps(self.scene_list[i],indent=4))
           
    def build_tables(self):
        self.currency_table = loot_table(constants.TABLE_CURRENCY)
        self.gear_table = loot_table(constants.TABLE_GEAR)
        self.tier_table = loot_table(constants.TABLE_TIER)
        with open(constants.LOOT_PROPERTIES) as f:
            self.loot_properties = json.load(f)

    def roll_loot(self,loot_type):
        if loot_type == 'currency':
            currency = self.currency_table.roll()
            if currency["name"] != "nothing":
                for i in self.loot_properties:
                    if i["name"] == currency["name"]:
                        if i["name"] == "gold coin":
                            sprite = constants.S_GOLD_COIN
                            break
                        elif i["name"] == "silver coin":
                            sprite = constants.S_SILVER_COIN
                            break
                        elif i["name"] == "bronze coin":
                            sprite = constants.S_BRONZE_COIN
                            break
                            
                new_item = obj_item(0,0,
                                    self.vars["current_scene"],
                                    self.vars["serial_number_counter"],
                                    i["name"],
                                    sprite)
                
                self.vars["serial_number_counter"] += 1
                return(new_item)
            else:
                return(None)

        elif loot_type == 'gear':
            gear = self.gear_table.roll()
            tier = self.tier_table.roll()
##            print("Rolled a {}!".format(gear["base"]))
##            print("It is tier {}!".format(tier["tier"]))
            if gear["base"] != "nothing":
                for i in self.loot_properties:
                    if i["name"] == gear["base"]:
                        if i["name"] == "sword":
                            sprite = constants.S_SWORD
                            break
                        elif i["name"] == "shield":
                            sprite = constants.S_SHIELD
                            break
                        elif i["name"] == "boots":
                            sprite = constants.S_BOOTS
                            break
                        elif i["name"] == "gloves":
                            sprite = constants.S_GLOVES
                            break
                        elif i["name"] == "helmet":
                            sprite = constants.S_HELMET
                            break
                        elif i["name"] == "belt":
                            sprite = constants.S_BELT
                            break
                        elif i["name"] == "shoulders":
                            sprite = constants.S_SHOULDERS
                            break
                        elif i["name"] == "bracers":
                            sprite = constants.S_BRACERS
                            break
                            
                for t in i["tier"]:
                    if t == tier["tier"]:
                        min_roll,max_roll = i["tier"][t].split("-")
                        stat = random.randint(int(min_roll), int(max_roll))
##                        print("Rolled a stat of {}!".format(stat))
                        break
                            
                new_item = obj_item(0,0,
                                    self.vars["serial_number_counter"],
                                    self.vars["current_scene"],
                                    i["name"],
                                    sprite)
                self.vars["serial_number_counter"] += 1
                new_item.set_implicit(i["implicit"],str(stat))
                return(new_item)

    def get_props(self):
        self.prop_list = []
        
        for p in self.scene_list[self.vars["current_scene"]]["props"]:
            if p["type"] == "chest":
                inventory = []
                for entry in p["inventory"]:
                    new_item = self.roll_loot(entry)
                    
                    if new_item:
##                        print("Rolled {}!".format(new_item.inst_name))
                        inventory.append(new_item)
                
                new_container = container(p["x"],
                                          p["y"],
                                          self.vars["current_scene"],
                                          p["type"],
                                          p["state"],
                                          storage=component.storage())
                for i in inventory:
                    if(i.deposit(new_container)):
                        print("Successfully deposited {}".format(i.inst_name))

                new_container.storage.set_inv_art(constants.CHEST_INVENTORY)
                    
                self.prop_list.append(new_container)

            elif p["type"] == "door":
                self.prop_list.append(portal(p["x"],
                                             p["y"],
                                             self.vars["current_scene"],
                                             p["type"],
                                             p["state"],
                                             p["destination_scene"],
                                             p["destination_x"],
                                             p["destination_y"]))
                
            else:
                print("No data for that kind of prop!")

        for p in self.prop_list:
            p.update()

    def log_message(self,message):
        self.vars["messages"].append(message)
        
    def print_to_screen(self,message, x, y):
        txt_surface = self.font.render(message,True,constants.CHEAT_TXT)
        self.SURFACE_MAIN.blit(txt_surface,(x,y))
        
    def draw_messages(self):
        if len(self.vars["messages"]) > 0:
            try:
                for i in range(min(len(self.vars["messages"]),5)):
                    message = self.vars["messages"][-(i+1)]
                    self.print_to_screen(message, 0, constants.GAME_HEIGHT-constants.INPUT_BOX_HEIGHT-(32*(i+1)))
            except IndexError:
                print("Invalid index")
                
class button():
    def __init__(self,x,y,width,height,art=None,action=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.art = art
        self.action = action
        self.active = True

    def draw(self,surf):
        if self.art and self.active:
            surf.blit(self.art, (self.x, self.y))

    def is_clicked(self,x,y):
        if (self.active and self.x < x < self.x+self.width) and (self.y < y < self.y+self.height):
            self.clicked = True
            return(True)
        else:
            self.clicked = False
            return(False)

    def update(self):
        if self.action:
            print("This happens")
            self.action()
        else:
            print("This button has no action!!")

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

class art():
    def __init__(self,art,x,y,active=True):
        self.x = x
        self.y = y
        self.art = art
        self.active = active
        
class menu():
    def __init__(self,x,y,width,height):
        self.button_list = []
        self.art = []
        self.page = 1
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.first_page = 1
        self.last_page = 4

        inventory_anchors = { 0:(774,658), 1:(809,658), 2:(844,658), 3:(880,658), 4:(915,658), 5:(949,658), 6:(984,658),
                              7:(774,692), 8:(809,692), 9:(844,692),10:(880,692),11:(915,692),12:(949,692),13:(984,692),
                             14:(774,727),15:(809,727),16:(844,727),17:(880,727),18:(915,727),19:(949,727),20:(984,727),
                             21:(774,762),22:(809,762),23:(844,762),24:(880,762),25:(915,762),26:(949,762),27:(984,762)}
        
        helmet_anchor = (880,513)
        shoulders_anchor = (915,513)
        armor_anchor = (880,549)
        belt_anchor = (880,584)
        weapon1_anchor = (844,549)
        weapon2_anchor = (915,549)
        gloves_anchor = (844,584)
        boots_anchor = (880,618)
        bracers_anchor = (915,584)

        gold_coin_anchor = (774,549)
        silver_coin_anchor = (774,584)
        bronze_coin_anchor = (774,618)

    def is_clicked(self,x,y):
        if (self.x < x < self.x+self.width) and (self.y < y < self.y+self.height):
            self.clicked = True
            for b in self.button_list:
                if b.is_clicked(x,y):
                    b.update()
            return(True)
        else:
            self.clicked = False
            return(False)

    def add_button(self, button):
        self.button_list.append(button)
        
    def draw(self,surf):
        # Draw background art
        surf.blit(constants.MENU_BACKGROUND,(constants.SCENE_WIDTH,constants.SIDE_HEADER_HEIGHT))

        if self.page == self.first_page:
            surf.blit(constants.MENU_FIRST_PAGE,
                      (constants.SCENE_WIDTH,0))

        elif self.page == self.last_page:
            surf.blit(constants.MENU_LAST_PAGE,
                      (constants.SCENE_WIDTH,0))

        else:
            surf.blit(constants.MENU_MIDDLE_PAGE,
                      (constants.SCENE_WIDTH,0))

        # Render text on top
        header_txt_surface = game_obj.font.render(constants.HEADER_1_STRING,True,constants.MENU_HEADER_TXT)
        game_obj.SURFACE_MAIN.blit(header_txt_surface,(constants.SCENE_WIDTH+constants.PAGE_TURN_HITBOX,
                                                       constants.PAGE_TURN_HITBOX))

        name_text = ""
        for a in game_obj.actor_list:
            if a.clicked:
                name_text = a.name
                break
        for p in game_obj.prop_list:
            if p.clicked:
                name_text = p.prop_type
                break
            
        name_txt_surface = game_obj.font.render(name_text,True,constants.MENU_HEADER_TXT)
        game_obj.SURFACE_MAIN.blit(name_txt_surface,(constants.SCENE_WIDTH+50,constants.SIDE_HEADER_HEIGHT+10))

        for b in self.button_list:
            b.draw(surf)

            

    def advance_page(self):
        self.page += 1
        if self.page > self.last_page:
            self.page = self.last_page

    def return_page(self):
        self.page -= 1
        if self.page < self.first_page:
            self.page = self.first_page
