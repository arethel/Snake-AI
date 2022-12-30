# importing libraries
import pygame
import time
import random
import numpy as np
# from visualize import Agent



snake_speed = 15

# Window size
window_x = 720
window_y = 480

# defining colors
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)


class Snake:
    
    def __init__(self,wx,wy) -> None:
        self.wx=wx
        self.wy=wy
        self.iteration = 0
        self.snake_position = [random.randrange(20, (window_x//10)-20)*10, random.randrange(20, (window_y//10)-20)*10]
        self.snake_body = [self.snake_position.copy()]
        k = 0
        while k<2:
            r = random.randrange(0, 2)
            pn = random.randrange(0, 2)
            new_pos = [self.snake_body[-1][0]+(1-r)*10*np.power(-1,pn),self.snake_body[-1][1]+(r)*10*np.power(-1,pn)]
            if new_pos not in self.snake_body:
                k+=1
                self.snake_body.append(new_pos)
        
        self.fruit_position = self.generate_pos_for_fruit()
        self.fruit_spawn = True
        
        self.direction = 'RIGHT'
        if self.snake_position[0]+10==self.snake_body[1][0]:
            self.direction='LEFT'

        self.change_to = self.direction
        
        self.score = 0
        
        self.game_over=False
        
        
    def generate_pos_for_fruit(self):
        new_pos = [random.randrange(1, (self.wx//10)) * 10,
                    random.randrange(1, (self.wy//10)) * 10]
        while new_pos in self.snake_body:
            new_pos = [random.randrange(1, (self.wx//10)) * 10,
                    random.randrange(1, (self.wy//10)) * 10]
        return new_pos
    
    def set_direction(self,change_to):
        self.change_to=change_to
        if change_to == 'UP' and self.direction != 'DOWN':
            self.direction = 'UP'
        if change_to == 'DOWN' and self.direction != 'UP':
            self.direction = 'DOWN'
        if change_to == 'LEFT' and self.direction != 'RIGHT':
            self.direction = 'LEFT'
        if change_to == 'RIGHT' and self.direction != 'LEFT':
            self.direction = 'RIGHT'
    
    def step(self,direction):
        
        if self.game_over==True or self.iteration>len(self.snake_body)*100:
            self.game_over=True
            return -10
            
        self.iteration+=1
        reward = 0
        
        self.set_direction(direction)
        if self.direction == 'UP':
            self.snake_position[1] -= 10
        if self.direction == 'DOWN':
            self.snake_position[1] += 10
        if self.direction == 'LEFT':
            self.snake_position[0] -= 10
        if self.direction == 'RIGHT':
            self.snake_position[0] += 10
        self.snake_body.insert(0, list(self.snake_position))
        if self.snake_position[0] == self.fruit_position[0] and self.snake_position[1] == self.fruit_position[1]:
            self.score += 10
            self.fruit_spawn = False
            reward=10
        else:
            self.snake_body.pop()
            
        if not self.fruit_spawn:
            self.fruit_position = self.generate_pos_for_fruit()
            
        self.fruit_spawn = True
        
        if self.snake_position[0] < 0 or self.snake_position[0] > self.wx-10:
            self.game_over=True
        if self.snake_position[1] < 0 or self.snake_position[1] > self.wy-10:
            self.game_over=True

        # Touching the snake body
        
        for block in self.snake_body[1:]:
            if self.snake_position[0] == block[0] and self.snake_position[1] == block[1]:
                self.game_over=True
        
        return reward



# agent = Agent(Snake)

# agent.model.load()

def visualize(agent):
    pygame.init()

    # Initialise game window
    pygame.display.set_caption('Snake')

    snake_game = agent.game

    game_window = pygame.display.set_mode((window_x, window_y))

    # FPS (frames per second) controller
    fps = pygame.time.Clock()

    # displaying Score function
    def show_score(choice, color, font, size,score):

        # creating font object score_font
        score_font = pygame.font.SysFont(font, size)
        
        # create the display surface object
        # score_surface
        score_surface = score_font.render('Score : ' + str(score), True, color)
        
        # create a rectangular object for the text
        # surface object
        score_rect = score_surface.get_rect()
        
        # displaying text
        game_window.blit(score_surface, score_rect)

    # game over function
    def game_over(score):

        # creating font object my_font
        my_font = pygame.font.SysFont('times new roman', 50)
        
        # creating a text surface on which text
        # will be drawn
        game_over_surface = my_font.render(
            'Your Score is : ' + str(score), True, red)
        
        # create a rectangular object for the text
        # surface object
        game_over_rect = game_over_surface.get_rect()
        
        # setting position of the text
        game_over_rect.midtop = (window_x/2, window_y/4)
        
        # blit will draw the text on screen
        game_window.blit(game_over_surface, game_over_rect)
        pygame.display.flip()
        
        # after 2 seconds we will quit the program
        time.sleep(2)
        
        # deactivating pygame library
        pygame.quit()
        
        # quit the program
        quit()

    change_to=snake_game.change_to
    # Main Function
    while True:
        
        # handling key events
        # for event in pygame.event.get():
        #     if event.type == pygame.KEYDOWN:
        #         if event.key == pygame.K_UP:
        #             change_to = 'UP'
        #         if event.key == pygame.K_DOWN:
        #             change_to = 'DOWN'
        #         if event.key == pygame.K_LEFT:
        #             change_to = 'LEFT'
        #         if event.key == pygame.K_RIGHT:
        #             change_to = 'RIGHT'

        state_old = agent.get_state()
        move = agent.get_action(state_old)
        
        move_ = 'UP'
        
        if move[1]==1:
            move_ = 'DOWN'
        if move[2]==1:
            move_ = 'RIGHT'
        if move[3]==1:
            move_ = 'LEFT'
            
        reward = agent.game.step(move_)
        
        game_window.fill(black)
        for pos in snake_game.snake_body:
            pygame.draw.rect(game_window, green,
                            pygame.Rect(pos[0], pos[1], 10, 10))
        pygame.draw.rect(game_window, white, pygame.Rect(
        snake_game.fruit_position[0], snake_game.fruit_position[1], 10, 10))
        
        
        if snake_game.game_over:
            game_over(snake_game.score)
        
        # displaying score countinuously
        show_score(1, white, 'times new roman', 20,snake_game.score)

        # Refresh game screen
        pygame.display.update()

        # Frame Per Second /Refresh Rate
        fps.tick(snake_speed)


# visualize(agent)