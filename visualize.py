import torch
import random
import numpy as np
from collections import deque
from snake import Snake
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR=0.001

window_x = 720
window_y = 480

class Agent:
    def __init__(self,game) -> None:
        self.game0=game
        self.game=self.game0(window_x,window_y)
        
        self.n_games=0
        self.epsilon=0
        self.gamma=0.9
        self.memory=deque(maxlen=MAX_MEMORY)
        
        self.model = Linear_QNet(len(self.get_state()),256,4)
        self.trainer = QTrainer(self.model,lr=LR,gamma=self.gamma)
    
    def get_state(self):
        
        returned_body_size = 10
        mx = int(np.ceil(np.log2(self.game.wx/10)))
        my = int(np.ceil(np.log2(self.game.wy/10)))
        state = []
        
        for n_of_body in range(returned_body_size):
            if n_of_body<len(self.game.snake_body):
                body_block = self.game.snake_body[n_of_body]
                bbx = ((((int(body_block[0]/10) & (1 << np.arange(mx)))) > 0).astype(int))[::-1]
                bby = ((((int(body_block[1]/10) & (1 << np.arange(my)))) > 0).astype(int))[::-1]
            else:
                bbx = np.zeros((mx,),dtype=int)
                bby = np.zeros((my,),dtype=int)
                
            state=np.concatenate((state,bbx,bby))
            
        fbx = ((((int(self.game.fruit_position[0]/10) & (1 << np.arange(mx)))) > 0).astype(int))[::-1]
        fby = ((((int(self.game.fruit_position[1]/10) & (1 << np.arange(my)))) > 0).astype(int))[::-1]
        state = np.concatenate((state,fbx,fby))
        
        
        return np.array(state, dtype=int)
    
    def get_action(self,state):
        self.epsilon= 80 - self.n_games/20
        final_move = [0,0,0,0]
        
        if random.randint(0,200)<self.epsilon:
            move = random.randint(0,3)
            final_move[move]=1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move]=1
        
        return final_move
    
    def train_long_memory(self):
        if len(self.memory)>BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample=self.memory
            
        state_olds, moves, rewards, state_news, dones = zip(*mini_sample)
        self.trainer.train_step(state_olds, moves, rewards, state_news, dones)
    
    def train_short_memory(self, state_old, move, reward, state_new, done):
            self.trainer.train_step(state_old, move, reward, state_new, done)
        
    def remember(self, state_old, move, reward, state_new, done):
            self.memory.append((state_old, move, reward, state_new, done))
    
    def reset(self):
        self.game=self.game0(window_x,window_y)
    

def train(agent):
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 20
    
    k = 0
    
    
    while k<500000:
        k+=1
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
        
        state_new = agent.get_state()
        
        agent.train_short_memory(state_old, move, reward, state_new, agent.game.game_over)
        agent.remember(state_old, move, reward, state_new, agent.game.game_over)
        
        
        if agent.game.game_over:
            score = agent.game.score
            
            agent.reset()
            agent.n_games+=1
            agent.train_long_memory()
            
            if score>record:
                record = score
                agent.model.save()
            
            
            print(k,'Game', agent.n_games,'Score',score,'Record:',record)
            
            # plot_scores.append(score)
            # total_score+=score
            # plot_mean_scores.append(total_score/agent.n_games)
            # plot(plot_scores, plot_mean_scores)
        

agent = Agent(Snake)
agent.model.load()

mps_device = torch.device("mps")
print(mps_device)
agent.model.to(mps_device)

train(agent)

