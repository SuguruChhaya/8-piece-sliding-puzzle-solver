from tkinter import *
from queue import PriorityQueue
import pygame
pygame.init()
from copy import deepcopy

#WIDTH = 400
#WIN = pygame.display.set_mode((WIDTH, WIDTH))
#*The puzzle itself will be solved on the screen itself. 
#pygame.display.set_caption("A* Puzzle Solving Algorithm")

#!Honestly, I kind of want a better setup window like Tim where I can click and input values in the table. 
RED = (255, 0, 0)
BLACK = (0, 0, 0)   
WHITE = (255, 255, 255)
number_font = pygame.font.SysFont('comicsans', 70)
class Spot():
    #This will be like the spot in Tim's video which will represent a box. 
    #!I have to revise how to make text labels in pygame even before I set this up. 
    def __init__(self, row, col, gap, rows):
        #*I would definitely want to know which spots are my neighbors. 
        self.row = row
        self.col = col
        self.gap = gap
        #!Need to make sure how x ys correspond to rows and columns!!
        self.x = col * self.gap
        self.y = row * self.gap
        self.color = WHITE
        self.neighbors = []
        self.num = ""

    def get_pos(self):
        return self.row, self.col
    
    def draw(self, window):
        #!Calculate it better so it shows in the middle of the spot. 
        pygame.draw.rect(window, self.color, (self.x, self.y, self.gap, self.gap))
        num_label = number_font.render(f'{self.num}', 1, BLACK)
        num_position = (self.x + (self.gap / 2) - (num_label.get_width() / 2), self.y + (self.gap / 2) - (num_label.get_height() / 2))
        window.blit(num_label, num_position)

    def make_num(self, input_num):
        #!Shouldn't really be blitted in a separate method because I only call it once so it immediately disappears from the screen!!
        #*Instead I should make this part of the draw method. 
        #!I should also be checking whether there was already a number inputted. 
        #*Since this only gets ran when self.num == "" anyways, I don't need to check. 

        self.num = str(input_num)
        if self.num == "9":
            self.color = RED

        #!Even when I click and it doesn't change, the number registered changes anyways. 
        #*I realized how the number changes are really dependent on what I clicked previously. 
        #*When I add, I input prev_spot.num +1 
        #*When I remove then add, I need to do prev_spot. 
        #*I need a way to manipulate all of this better. 
    def remove_num(self):
        self.num = ""
        self.color = WHITE



class SetupWindow():
    def __init__(self):
        self.width = 400
        self.window = pygame.display.set_mode((self.width, self.width))
        pygame.display.set_caption("A* Puzzle Solving Algorithm")
        self.run = True
        self.rows = 3
        #Store all the spots. 
        self.grid = []
        #!At the initial input stage, I need to be able to tell which number the player is inputting. 
        self.input_num = 0
        #!No more mouse movements after start algorithm. 
        self.has_started = False
        self.correct_location = {
            "1": (0, 0), 
            "2": (0, 1), 
            "3": (0, 2),
            "4": (1, 0), 
            "5": (1, 1),
            "6": (1, 2),
            "7": (2, 0),
            "8": (2, 1),
            "9": (2, 2)
        }

    def mainloop(self):
        self.make_grid()
        #self.show_grid()
        while self.run:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                #self.show_grid()
                if self.has_started == False:
                    if pygame.mouse.get_pressed()[0]:      
                        pos = pygame.mouse.get_pos()
                        row, col = self.get_clicked_pos(pos, self.rows, self.width)
                        #*ROWS is pre-decided. 
                        #TODO The place I am suspiscious is the re-assigning of the the spot. Maybe the row and column are opposite somehow?
                        spot = self.grid[row][col]
                        #!Problem is not in reassigning but probably in the blitting. 
                        #self.show_grid()
                        if spot.num == "":
                            #!Probably should check whether the input num is smaller or equal to 9 or not. 
                            spot.make_num(self.find_input_num())
                            #!The new issue is that whenever I click on an old spot, input_num changes the value and the next placement becomes smaller. 
                            #*To prevent this, I can only enter this loop if number has not been initialized. 
                            #!New issue is that whenever I delete an old number and replace and start adding again it starts from old_number+1.
                            #*I think the overall best solution is to just loop through all the spots and find the maximum. 
                            self.grid[row][col] = spot
                            #self.show_grid()

                    elif pygame.mouse.get_pressed()[2]:
                        pos = pygame.mouse.get_pos()
                        row, col = self.get_clicked_pos(pos, self.rows, self.width)
                        spot = self.grid[row][col]
                        #*To prepare for next addition. 
                        spot.remove_num()
                        #!The self.grid won't be able to pickup changes made in objects. 
                        #*I need to update self.grid after making any changes in numbers. 
                        self.grid[row][col] = spot
                
                #print("pass1")
                #*Detect the space bar keyboard press. 
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and self.has_started == False and self.find_input_num() == "START":
                    #self.show_grid()
                    #*Run the algorithm based on where 9 is after checking inversion. 
                    #*For now ignore about the tkinter window. 
                    if self.is_inversion() == True:
                        #*Make a tkinter pop up and don't start algo. 
                        #!Calling a tkinter window inside mainloop might cause some problems. 
                        print("cannot solve")
                    else:
                        self.algorithm()

    def algorithm(self):
        count = 0
        open_set = PriorityQueue()
        #?Are lists mutable in priority queues? -> After I modify the array the whole thing freezes
        #?What if I put in multiple objects? -> NVM arrays are mutable so should make a copy before inputting. 
        #!Even when I rename there is a problem. 
        start = self.grid.copy()
        #*First argument is f-score: add up g_score and h_score
        #*Second argument is count: when inserted into the queue. 
        #*Third argument is the actual copy of the grid. 
        open_set.put((0, count, start))
        
        came_from = {}
        g_score = {}
        f_score = {}

        #!I don't have all the spots right in front of me so I have to find it generate all the options. 
        #*Probably skip the initial step. 

        #!Since arrays are not hashable, I think I should just join them into a string. 
        #*But since I have got a 2D array, I need to first flatten it and convert to string. 
        string_start = self.to_string(start)
        g_score[string_start] = 0
        #*I cannot keep track with just self.grid because need to create a lot of copies. 
        #*Work with parameters from now on. 
        f_score[string_start] = self.h(start)

        #!Even for the set, a list is unhashable so use the string version. 
        open_set_hash = {string_start}

        while not open_set.empty():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            current = open_set.get()[2]
            string_current = self.to_string(current)
            open_set_hash.remove(string_current)

            #*I can tell if reached end if h() returns 0. 
            if self.h(current) == 0:
                self.reconstruct(came_from)
                return 
            
            #*To figure out all the neightbor possible grids, I need to locate 9. 
            neighbors = []
            nine_row, nine_col = self.find_nine(current)
            #?Seems like current is changing when I am modifying temp. Is it?
            if nine_row == 0 or nine_row ==1:
                #!Shouldn't be copying from self.grid but rather current. 
                temp = deepcopy(current)
                temp[nine_row][nine_col], temp[nine_row+1][nine_col] = temp[nine_row+1][nine_col], temp[nine_row][nine_col]
                neighbors.append(temp)

            if nine_row == 1 or nine_row==2:
                #?Somehow temp is mutating so try making a deep copy. 
                temp = deepcopy(current)
                temp[nine_row][nine_col], temp[nine_row-1][nine_col] = temp[nine_row-1][nine_col], temp[nine_row][nine_col]
                neighbors.append(temp)

            if nine_col == 0 or nine_col == 1:
                temp = deepcopy(current)
                temp[nine_row][nine_col], temp[nine_row][nine_col+1] = temp[nine_row][nine_col+1], temp[nine_row][nine_col]
                neighbors.append(temp)

            if nine_col == 1 or nine_col == 2:
                temp = deepcopy(current)
                temp[nine_row][nine_col], temp[nine_row][nine_col-1] = temp[nine_row][nine_col-1], temp[nine_row][nine_col]
                neighbors.append(temp)

            for neighbor in neighbors:
                #*For hashing, I also have to convert neighbor into a string. 
                string_neighbor = self.to_string(neighbor)
                temp_g_score = g_score[string_current] + 1
                #!I cannot just use tim's code because I haven't created a g_score for the neighbor yet. 
                #*I have to first check if such number even exists. 

                #!When we don't have a key yet and when it is larger just does the same thing: overrides and changes the value. 
                if string_neighbor not in g_score.keys() or temp_g_score < g_score[string_neighbor]:
                    came_from[string_neighbor] = current
                    g_score[string_neighbor] = temp_g_score
                    f_score[string_neighbor] = g_score[string_neighbor] + self.h(neighbor)
                    if string_neighbor not in open_set_hash:
                        #!What exactly is the purpose of this count variable?? -> I honestly think we don't. 
                        count += 1
                        open_set.put((f_score[string_neighbor], count, neighbor))
                        open_set_hash.add(string_neighbor)
                        #TODO -> Check whether openset removes element after I "get()" it. -> It does. 

            #*I think make closed is just for the sake of visualization. 

    def to_string(self, grid):
        arr = []
        for row in grid:
            for spot in row:
                arr.append(spot.num)
        
        return "".join(arr)

    def h(self, grid):
        #*Loop through and see difference. 
        #*Use a dictionary to store locations and compare with correct location. 
        current_location = {}
        for row in range(len(grid)):
            for col in range(len(grid[0])):
                current_location[grid[row][col].num] = (row, col)
        
        difference = 0
        #*Loop through all keys and check for difference. 
        for key in self.correct_location.keys():
            difference += (abs(current_location[key][0] - self.correct_location[key][0]) + abs(current_location[key][1] - self.correct_location[key][1]))

        return difference

    def find_nine(self, grid):
        for row in range(len(grid)):
            for col in range(len(grid[0])):
                if grid[row][col].num == "9":
                    return row, col

    def reconstruct(self, came_from):
        pass

    def show_grid(self, grid):
        #?Somehow mutating
        arr = [['', '', ''], ['', '', ''], ['', '', '']]
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                arr[i][j] = grid[i][j].num
        print(arr)

    def is_inversion(self):
        
        #*First flatten the array into a temporary array. 
        arr = []
        #?Somehow the grid is appending in the wrong direction. 
        for row in self.grid:
            for spot in row:
                #!I cannot include 9 as an inversion. 
                if spot.num != "9":
                    arr.append(int(spot.num))
        
        inversion_count = 0
        for i in range(len(arr)):
            for j in range(i+1, len(arr)):
                if arr[i] > arr[j]:
                    inversion_count += 1
        
        if inversion_count % 2 == 0:
            return False
        else:
            return True


    '''
    def cannot_solve(self, root):
        error_font = font.Font(size=60, weight="bold")
        Label(root, text="Puzzle cannot be solved!!", font=error_font, fg="red").pack()
    '''
    #?Somehow this method is returning None which causes the label to be inputted as None. 
    def find_input_num(self):
        #*Run a forloop from 1 to 9 and check which smallest number is currently missing. 
        
        for i in range(1, 10):
            found = False
            for row in self.grid:
                for spot in row:
                    #!First check for blanks. 
                    if spot.num != "" and int(spot.num) == i:
                        found = True
                        #!I have to make sure I reset 'found' for every number. 
            if found == False:
                return i
        
        #*I can use this method to check whether all numbers are inputted as well to check whether the algo can start. 
        return "START"


    def get_clicked_pos(self, pos, rows, width):
        gap = width //rows
        #?Why y x though?
        #!Official docs also says return is (x, y)
        #*But when I correspond grid x, it will help determine column
        #?
        x, y = pos

        row = y // gap
        col = x // gap
        return row, col


    def make_grid(self):
        self.gap = self.width // self.rows
        for i in range(self.rows):
            self.grid.append([])
            for j in range(self.rows):
            #!Tim kind of confuses us by saying "width" in the spot class but it really should be gap.
                spot = Spot(i, j, self.gap, self.rows)
                self.grid[i].append(spot)
        

    def draw_grid(self):
        for i in range(self.rows):
            pygame.draw.line(self.window, BLACK, (0, i * self.gap), (self.width, i*self.gap))

        #?Tim puts all of this in a nested for-loop but I am not really sure which one is correct...
        for j in range(self.rows):
            pygame.draw.line(self.window, BLACK, (j*self.gap, 0), (j*self.gap, self.width))

    def draw(self):
        self.window.fill(WHITE)

        for row in self.grid:
            for spot in row:
                spot.draw(self.window)

        self.draw_grid()
        pygame.display.update()



a = SetupWindow()
a.mainloop()
