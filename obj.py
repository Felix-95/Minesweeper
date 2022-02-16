import numpy as np
from constants import COLOR_DICT, SCRWIDTH, SCRHEIGHT, BORDER_DISTANCE,  WHITE, BLACK, WIN, RED
import pygame
import math
import random
import time
import sys
    
class Box:
    def __init__(self, status, lenght):
        self.status = status # -1 = bombe, 0 = neutral, 1 = aufgedeckt
        self.lenght = lenght
        self.bomb_count = 0
        self.draw_status = False
        self.flagged = False
        self.font = pygame.font.SysFont("Ariel", int(lenght//1))
        
        
    def draw(self, win, x, y):
        rect = pygame.Rect(x,y,self.lenght-1,self.lenght-1)
        pygame.draw.rect(win, COLOR_DICT[self.status], rect)
        if self.draw_status:
            t_bomb_count = self.font.render(str(self.bomb_count), True, WHITE)
            win.blit(t_bomb_count, (x + self.lenght//2 - t_bomb_count.get_width()//2,
                                    y + self.lenght//2 - t_bomb_count.get_height()//2))
        if self.flagged:
            side_length = round(self.lenght * 0.6)
            triangle_height = math.sqrt((side_length**2 - (0.5*side_length)**2))
            offset_x, offset_y = self.lenght//2-triangle_height//2,  triangle_height//6
            p1 = (x+offset_x, y+offset_y)
            p2 = (x+offset_x, y+offset_y+triangle_height)
            p3 = (x+offset_x+triangle_height, y+offset_y+triangle_height//2)
            pygame.draw.polygon(win, RED, [p1,p2,p3])
            p4 = (x+offset_x, y+offset_y+triangle_height*1.6)
            pygame.draw.line(win, BLACK, (p1), (p4), math.ceil(self.lenght//25))

class Field:
    def __init__(self, rows, cols, bomb_rel):
        self.rows = rows
        self.cols = cols
        self.box_lenght = self.get_box_length()
        self.create_grid()
        self.bomb_qty = int(round(rows*cols * bomb_rel))
        self.random_dist(self.bomb_qty)
        self.flag_qty = 0
        self.update_all_bomb_counts()
        self.rect = pygame.Rect(BORDER_DISTANCE, BORDER_DISTANCE, self.cols*self.box_lenght,self.rows*self.box_lenght)
        # self.set_bombs()
        
        sys.setrecursionlimit(int(rows*cols))
        
    def random_dist(self, n):
        for _ in range(n):
            empty = False
            
            while not empty:
                r, c = random.randint(0, self.rows-1), random.randint(0, self.cols-1)
                empty = True if self.grid[r][c].status != -1 else False
            self.set_status(r,c,-1)


    def create_grid(self):
        self.grid = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                start_status = 0
                b = Box(start_status, self.box_lenght)
                row.append(b)
            self.grid.append(row)
                
    def set_status(self, r,c, status):    
        self.grid[r][c].status = status   
        
    def get_status(self, r,c):
        return self.grid[r][c].status
        
    def set_bombs(self):
        self.set_status(7,7,-1)
        self.set_status(7,10,-1)
        self.set_status(10,12,-1)
        self.set_status(13,10,-1)
        self.set_status(13,7,-1)
        self.set_status(10,5,-1)
        
    def get_box_length(self):
        return int(round(min((SCRWIDTH - 2 * BORDER_DISTANCE)/self.cols ,
                            (SCRHEIGHT - 2 * BORDER_DISTANCE)/self.rows), 1))
        
    def draw(self, win):
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c].draw(WIN, BORDER_DISTANCE + c * self.box_lenght,
                                    BORDER_DISTANCE + r * self.box_lenght)
                
    def get_box_by_pos(self, pos):
        x, y = pos
        row = math.floor((y - BORDER_DISTANCE)/self.box_lenght)
        col = math.floor((x - BORDER_DISTANCE)/self.box_lenght)
        return row, col
    
    def get_neighbors(self, r, c):
        neighbors = []
        
        for d_r in range(-1, 2):
            for d_c in range(-1, 2):
                if d_r == 0 and d_c == 0:
                    continue
                elif -1 < (r + d_r) < self.rows and -1 < (c + d_c) < self.cols:
                    neighbors.append((r + d_r, c + d_c))
        
        return neighbors
    
    def get_surrounding_bombs(self, r, c):
        bombs = 0
        
        for b_r, b_c in self.get_neighbors(r, c):
            if self.get_status(b_r, b_c) <= -1:
                bombs += 1
                
        return bombs
        #             bombs += 1
        # start_c, end_c = max(0, c-1), min(c+2, self.cols)
        # start_r, end_r = max(0, r-1), min(r+2, self.rows)
        
        # bombs = 0
        
        # for r in range(start_r, end_r):
        #     for c in range(start_c, end_c):
        #         if self.get_status(r,c) == -1:
        #             bombs += 1
        # return bombs
    
    def update_all_bomb_counts(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c].bomb_count = self.get_surrounding_bombs(r,c)
                
                # star_boxes = self.get_star_boxes(r,c)
                # star_boxes_status = [self.get_status(sr,sc)==1 for sr,sc in star_boxes]
                # self.grid[r][c].draw_status = True if any(star_boxes_status) else False
                if self.grid[r][c].status == 1 and self.grid[r][c].bomb_count > 0:
                    self.grid[r][c].draw_status = True 
                else:
                    self.grid[r][c].draw_status = False 
                
                
    def box_pressed(self, r, c):
        if self.grid[r][c].flagged == False:
            if self.grid[r][c].status == -1:
                return -1
            elif self.grid[r][c].status == 0:
                self.clear_area(r,c)
                
                
            if self.is_completed():
                return 1
        
    def is_completed(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c].status == 0:
                    return False
        return True
            
    def clear_area(self,r,c):
        if self.grid[r][c].status != 0:
            return
        
        self.grid[r][c].status = 1
        # self.draw(WIN)
        # pygame.display.update()
        # time.sleep(0.3)
        if self.grid[r][c].bomb_count == 0:
            for new_r, new_c in self.get_neighbors(r,c):
                if not self.grid[new_r][new_c].flagged:
                    self.clear_area(new_r, new_c)
                
    def flag(self, r,c):
        if self.grid[r][c].status != 1:
            self.grid[r][c].flagged = not self.grid[r][c].flagged
            self.flag_qty += 1 if self.grid[r][c].flagged else -1
            
    def reveal_bombs(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c].status == -1:
                    self.grid[r][c].status = -3
        