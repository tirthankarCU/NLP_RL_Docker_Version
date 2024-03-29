import numpy as np 
import pandas as pd 
import time
# import utils as U
# import model as M
import torch 
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import matplotlib.pyplot as plt 
import json
import copy
import gym

import subprocess 
result = subprocess.run('pip install -e .', shell = True)
import sys 
import os
sys.path.append(f'{os.getcwd()}/gym-examples')
import gym_examples

action_indx = -1
def policyR(observation, number):
    global action_indx
    hundreth, tenth, unit = number//100, (number%100)//10, number%10
    best_actions = [0, 3]*hundreth + [1, 4]*tenth + [2, 5]*unit
    action_indx += 1
    return best_actions[action_indx]

dbg=True
episodes=1
number = 123
env = gym.make('gym_examples/RlNlpWorld-v0',render_mode="rgb_array")
for _ in range(episodes):
    cumulative_reward,steps=0,0
    observation = env.reset(set_no = number)
    mx_steps,cnt=20,0
    print(f'state[{observation["text"]}]')
    while steps<mx_steps:
        action = policyR(observation, number)  # User-defined policy function
        observation, reward, terminated, info = env.step(action)
        cumulative_reward+=reward
        steps+=1
        if dbg==True:
            print(f'cumulative_reward[{cumulative_reward}];' + \
                  f'action[{action}]; next_state[{observation["text"]}]')
        if terminated:
            break
    print(f'Cumulative Reward ~ {cumulative_reward}; TimeTaken ~ {steps}')
env.close()
