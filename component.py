import random
import constants

game_obj = None

def initialize(GO):
    global game_obj
    game_obj = GO
    
class simple_ai():
    def take_turn(self):
        decision = random.randint(0,4)
        if decision == 0: # Don't move
            pass
        elif decision == 1: # Move right
            self.owner.move(1,0)
        elif decision == 2: # Move left
            self.owner.move(-1,0)
        elif decision == 3: # Move up
            self.owner.move(0,-1)
        elif decision == 4: # Move down
            self.owner.move(0,1)
        else:
            print("Indecision!")

class slot():
    def __init__(self,number,owner):
        self.owner=owner
        self.number=number
        self.width = constants.RES
        self.height = constants.RES
        
    def set_anchor(self,x,y):
        '''Takes an x and y argument denoting the offset from the storage
        anchor to the slot anchor in pixels'''
        self.anchor_x = x
        self.anchor_y = y
        
class storage():
    def __init__(self, max_slots = 8, inventory = None):
        self.max_slots = max_slots
        for i in range(self.max_slots):
            self.slots=slot(i,self)
            
        if inventory:
            self.inventory = inventory
        else:
            self.inventory = []

    def set_inv_art(self, inv_art):
        '''Set the background art for the storage and its location releative
        to the prop on screen'''
        self.inv_art = inv_art
        self.anchor_x = self.owner.x*constants.RES - 50
        self.anchor_y = self.owner.y*constants.RES - 75
        self.width = 145
        self.height = 75
        
            
class bipedal_body():
    def __init__(self):
        self.head = body_part(10)
        self.torso = body_part(10)
        self.left_arm = body_part(10)
        self.right_arm = body_part(10)
        self.left_leg = body_part(10)
        self.right_leg = body_part(10)

class body_part():
    def __init__(self,hp):
        self.hp = hp
