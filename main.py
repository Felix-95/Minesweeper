import pygame
import os
import sys
from constants import SCRWIDTH, SCRHEIGHT, BLACK, WHITE, RED, FPS, BORDER_DISTANCE, WIN, GREY, LIGHT_BLUE
from obj import Field, Box
import eigmod
from eigmod import ButtonFunktionen
from eigmod import slider
from datetime import datetime


pygame.init()
pygame.display.set_caption("Space Game")
directory_of_file = os.path.normpath(sys.argv[0] + os.sep + os.pardir)


CLOCK = pygame.time.Clock()
message_font = pygame.font.SysFont("Ariel", 50)
time_font = pygame.font.SysFont("Ariel", 30)
    
start_value_slider = 20
bomb_rel = 0.12
inital_rows, inital_cols = start_value_slider,start_value_slider
f = Field(inital_rows, inital_cols, bomb_rel)

message_dict = {-1: "Game over",  1: "You won"}

def get_message(game_state):
    if game_state == 0:
        bombs_left = f.bomb_qty - f.flag_qty
        text = "bomb is left" if bombs_left == 1 else "bombs are left"
        message = f"{bombs_left} {text}"
    else:
        message = message_dict[game_state]
    return message

def add_zero(x):
    if len(str(x)) == 1:
        return "0" + str(x)
    return str(x)

def main():
    global f, bomb_rel
    width, height = 120, 40
    x, y =  BORDER_DISTANCE, BORDER_DISTANCE//2 - height//2
    reset_button = ButtonFunktionen.Buttons(WIN, SCRWIDTH, SCRHEIGHT, 0, 1, "Start new game", x = x, y = y, width=width, height = height, 
                                            with_draw_activation =False, umrandungs_dicke = 0, color_normal=GREY, color_active=LIGHT_BLUE,
                                            verschiebung_hintergrund=0, font_name="Ariel", font_size_height_rel= 0.6,nur_schrift=True)
    swidth, sheight = 110, 40
    sx, sy =  x + width + 120, BORDER_DISTANCE//2 - sheight//2
    size_slider = slider.Slider(sx,sy,swidth,height, value_display=True,
               value_range=(5, 50), scale_distance=5, only_values_scale=True,
               start_value = start_value_slider, font_name="Ariel", label = "Size")
    bwidth, bheight = 110, sheight
    bx, by =  sx + swidth + 180, sy
    bomb_slider = slider.Slider(bx, by,bwidth,bheight, value_display=True,
               value_range=(0.03,0.3), scale_distance=0.03, only_values_scale=True,
               start_value = bomb_rel, font_name="Ariel", label = "Bombs",)
    
    # size_slider = slider.Slider(sx,sy,swidth,height, value_display=True,value_range=[5, 100], 
    #                             scale_distance=5, only_values_scale=True)
    run = True
    game_state = 0 # -1 game over, 0 ingame, 1 gewonnen
    
    start_time = datetime.now()
    while run:
        CLOCK.tick(FPS)
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                pass
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                
                pos = pygame.mouse.get_pos()
                row, col = f.get_box_by_pos(pos)
                if event.button == 2:
                    f.set_status(row, col, -1)
                    f.update_all_bomb_counts()
                if event.button == 1:
                    
                    #### spielfeld
                    if game_state == 0 and f.rect.collidepoint(pos):
                        status = f.box_pressed(row, col)
                        if status == -1:
                            f.set_status(row, col, -2)
                            game_state = -1
                        elif status == 1:
                            game_state = 1
                    #### button
                    reset_pressed = reset_button.get_if_clicked(pos, True)
                    if reset_pressed:
                        bomb_rel = bomb_slider.current_value
                        f = Field(size_slider.current_value, size_slider.current_value, bomb_rel)
                        game_state = 0
                        start_time = datetime.now()
                    
                if event.button == 3:
                    f.flag(row, col)
                    
                if game_state != 0:
                    f.reveal_bombs()
                
                
                    
                f.update_all_bomb_counts()
                
        size_slider.update()
        bomb_slider.update()
        if game_state == 0:
            delta_time = datetime.now() - start_time
        

        ##### draw
        WIN.fill((0, 0, 0))
        f.draw(WIN)
        
        t_message = message_font.render(get_message(game_state),True, WHITE)
        x = SCRWIDTH//2-t_message.get_width()//2
        y = SCRHEIGHT - BORDER_DISTANCE + BORDER_DISTANCE//2 - t_message.get_height()//2
        WIN.blit(t_message, (x,y))
        
        minutes , seconds = add_zero(delta_time.seconds//60), add_zero(delta_time.seconds%60)
        t_delta_time = time_font.render(f"{minutes}:{seconds}",True, WHITE)
        ts, ty = BORDER_DISTANCE, y 
        WIN.blit(t_delta_time, (ts, ty))
        
        reset_button.draw()
        size_slider.draw(WIN)
        bomb_slider.draw(WIN)

        pygame.display.update()

main()
pygame.quit()
