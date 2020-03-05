import os
import pygame
import constants
import json
import random
import component
from classes import *
        
def quit_nicely():
    game_obj.save()
    pygame.display.quit()
    pygame.quit()

def handle_cheat_code():
    game_obj.log_message(game_obj.vars["cheat_text"])
    args = game_obj.vars["cheat_text"].split()
    try:
        if args[0] == 'tp':
            x = args[2]
            y = args[3]

            if args[1] == 'me':
                game_obj.actor_list[0].x = int(x)
                game_obj.actor_list[0].y = int(y)
                game_obj.log_message("Teleported player to {},{}".format(x,y))
                
            elif args[1] == 'them':
                print("Teleport someone else. X={}, Y={}".format(x,y))
        elif args[0] == 'help':
            print("tp <target> <x> <y> teleports a target to an x,y destination.")
            print("for example: \"tp me 0 0 \" teleports the player to the top left corner of the scene.")

        elif args[0] == 'roll':
            if args[1] == 'currency':
                print("rolling currency")
                game_obj.roll_loot("currency")
                
            elif args[1] == 'gear':
                print("rolling gear")
                game_obj.roll_loot("gear")

        elif args[0] == 'set':
            if args[1] == 'gamemode':
                if args[2] == 'normal':
                    game_obj.vars["game_mode"] = 'normal'
                    for b in game_obj.side_menu.edit_mode_buttons:
                        b.deactivate()
                elif args[2] == 'edit':
                    game_obj.vars["game_mode"] = 'edit'
                    for b in game_obj.side_menu.edit_mode_buttons:
                        b.activate()
                else:
                    print("Invalid game mode.")

        else:
            print(args)
    except IndexError:
        game_obj.log_message("No cheat code entered.")
##        print("No cheat code entered.")
        
def draw_game():

    # Background fill to erase previous frame
    game_obj.SURFACE_MAIN.fill(constants.DEFAULT_BG)

    # Render the current scene
    for y,row in enumerate(game_obj.scene_list[game_obj.vars["current_scene"]]["map"]):
        for x,tile in enumerate(row):
            for t in game_obj.tile_list:
                if t.serial_no == tile:
                    game_obj.SURFACE_MAIN.blit(t.art,(x*constants.RES,y*constants.RES))

    # Draw the side bar menu
    game_obj.side_menu.draw(game_obj.SURFACE_MAIN)

    # Draw props
    for p in game_obj.prop_list:
        p.draw(game_obj.SURFACE_MAIN)
        
    # draw the character and other actors
    for a in game_obj.actor_list:
        a.draw(game_obj.SURFACE_MAIN)
        
    # Define input box characteristics, this should be moved such that it doesn't happen
    # every frame.
    input_box_hgt = 32
    input_box = pygame.Rect(0,
                            constants.GAME_HEIGHT-constants.INPUT_BOX_HEIGHT,
                            constants.GAME_WIDTH,
                            constants.INPUT_BOX_HEIGHT)

    # Draw the cheat code box if cheat mode is active.
    if game_obj.vars["cheat_codes"]:
        pygame.draw.rect(game_obj.SURFACE_MAIN, constants.CHEAT_TXT_BOX_BG,input_box, 0)
        txt_surface = game_obj.font.render(game_obj.vars["cheat_text"],True,constants.CHEAT_TXT)
        game_obj.SURFACE_MAIN.blit(txt_surface,(input_box.x+5,input_box.y+5))

    game_obj.draw_messages()
                

    # Draw debug information if debug mode is active.
    if game_obj.vars["debug"]:
        debug_text = game_obj.font.render(game_obj.vars["debug_text"],True,constants.DEBUG_TXT)
        game_obj.SURFACE_MAIN.blit(debug_text,(0,0))

    # Draw the mouse attachment if there is one.
    if game_obj.vars["mouse_attachment"]:
        game_obj.SURFACE_MAIN.blit(game_obj.vars["mouse_attachment"].sprite,(game_obj.vars["mouse_attachment"].x,
                                                                             game_obj.vars["mouse_attachment"].y))
        
    # Flip the display to show the next frame
    pygame.display.flip()

def game_main_loop():
    game_quit = False
    new_click = False
    move_successful = False
    fpsClock = pygame.time.Clock()
    mx = 0
    my = 0

    page_forward = button(constants.GAME_WIDTH-constants.PAGE_TURN_HITBOX,
                          0,
                          constants.PAGE_TURN_HITBOX,
                          constants.PAGE_TURN_HITBOX,
                          action=game_obj.side_menu.advance_page)
    
    page_backward = button(constants.SCENE_WIDTH,
                           0,
                           constants.PAGE_TURN_HITBOX,
                           constants.PAGE_TURN_HITBOX,
                           action=game_obj.side_menu.return_page)

    game_obj.side_menu.add_button(page_forward)
    game_obj.side_menu.add_button(page_backward)

    game_obj.side_menu.edit_mode_buttons = []
    
    with open("data\\tiles.txt","r") as f:
        tile_list = json.load(f)
        for i, t in enumerate(tile_list):
            tile = struct_tile(i)
            temp_x = constants.SCENE_WIDTH+10+(42*(i%6))
            temp_y = constants.SIDE_HEADER_HEIGHT+42*int(i/6)
            tile.set_xy(temp_x,temp_y)
            new_button = button(temp_x,
                                temp_y,
                                32,32,
                                art = pygame.image.load(t["art"]),
                                action = tile.attach_to_mouse)
            

            new_button.deactivate()
            game_obj.side_menu.add_button(new_button)
            game_obj.side_menu.edit_mode_buttons.append(new_button)
        
                                                                                                                
    game_obj.get_props()
    
    while not game_quit:
        event_list = pygame.event.get()
        for p in game_obj.prop_list:
            pass
            
        for event in event_list:
            if event.type == pygame.QUIT:
                game_quit = True

            if event.type == pygame.KEYDOWN and game_obj.vars["cheat_codes"]:
                if event.key == pygame.K_RETURN:
                    handle_cheat_code()
                    game_obj.vars["cheat_text"] = ''
                    game_obj.vars["cheat_codes"] = not game_obj.vars["cheat_codes"]
                elif event.key == pygame.K_BACKSPACE:
                    game_obj.vars["cheat_text"] = game_obj.vars["cheat_text"][:-1]
                else:
                    game_obj.vars["cheat_text"] += event.unicode
                    
            elif event.type == pygame.KEYDOWN and not game_obj.vars["cheat_codes"]:
                if event.key == pygame.K_w:
                    move_successful = game_obj.actor_list[0].move(0,-1)
                if event.key == pygame.K_a:
                    move_successful = game_obj.actor_list[0].move(-1,0)
                if event.key == pygame.K_s:
                    move_successful = game_obj.actor_list[0].move(0,1)
                if event.key == pygame.K_d:
                    move_successful = game_obj.actor_list[0].move(1,0)
                if event.key == pygame.K_RETURN:
                    game_obj.vars["cheat_codes"] = not game_obj.vars["cheat_codes"]
                if event.key == pygame.K_F3:
                    game_obj.vars["debug"] = not game_obj.vars["debug"]
                if event.key == pygame.K_SPACE:
                    for a in game_obj.actor_list:
                        if a.clicked and not a.player:
                            print("Attack!")
                    for p in game_obj.prop_list:
                        if p.clicked:
                            move_successful = p.interact(game_obj.actor_list[0])
                if event.key == pygame.K_ESCAPE:
                    game_obj.vars["mouse_attachment"] = None
                            

            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                if game_obj.vars["mouse_attachment"]:
                    game_obj.vars["mouse_attachment"].set_xy(mx,my)    

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    new_click = True
                    left_click_x, left_click_y = event.pos
                    
            
        if move_successful:
            game_obj.vars["turn"] += 1
            move_successful = False
            for a in game_obj.actor_list:
                if not a.player and a.scene == game_obj.vars["current_scene"]:
                    a.ai.take_turn()

        mouse_tile_x = int(mx/constants.RES)
        mouse_tile_y = int(my/constants.RES)
        game_obj.vars["debug_text"] = "X: {} Y: {} TILE: ({},{}) TURN: {}".format(mx,my,
                                                                                 mouse_tile_x,
                                                                                 mouse_tile_y,
                                                                                 game_obj.vars["turn"])
        if new_click:

            if game_obj.side_menu.is_clicked(left_click_x,left_click_y):
                pass
            
            # Check scene area
            elif (0 < left_click_x < constants.SCENE_WIDTH
                and 0 < left_click_y < constants.SCENE_HEIGHT):

                if game_obj.vars["mouse_attachment"]:
                    game_obj.log_message("{} is already attached to the mouse!".format(game_obj.vars["mouse_attachment"].inst_name))
                else:
                    for a in game_obj.actor_list:
                        a.is_clicked(left_click_x,left_click_y)
                        
                        
                    for p in game_obj.prop_list:
                        p.is_clicked(left_click_x,left_click_y)
                    
                
            new_click = False
                
                 
        draw_game()
        fpsClock.tick(60)

    quit_nicely()
                
def game_initialize():
    os.environ['SDL_VIDEO_WINDOW_POS'] = "5,25"
    pygame.init()
    game_obj = game_object()

    game_obj.SURFACE_MAIN = pygame.display.set_mode((constants.GAME_WIDTH,
                                            constants.GAME_HEIGHT))
    game_obj.load()
    game_obj.build_tables()

    game_obj.actor_list.append(actor(1,1,0,constants.S_PLAYER,player=True,name="Player",storage=component.storage()))
    game_obj.actor_list.append(actor(15,15,0,constants.S_ENEMY,player=False,ai=component.simple_ai(),name="Enemy"))

    game_obj.side_menu = menu(constants.SCENE_WIDTH,0,constants.SIDE_BAR_WIDTH,constants.GAME_HEIGHT)

    # Tell the following modules about game_obj
    component.initialize(game_obj)
    init_classes(game_obj)
    
    return(game_obj)

if __name__ == "__main__":
    game_obj = game_initialize()

    
    game_main_loop()
