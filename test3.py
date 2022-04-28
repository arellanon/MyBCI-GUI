#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 27 23:07:25 2022

@author: nahuel
"""
import random

config = {'time_trial': 8, 'run_n': 2, 'trial_per_run': 4, 'time_pause': 10}
print(config)
print(type(config['time_trial']))


run_n = config['run_n']
trial_per_run = config['trial_per_run']
time_pause= config['time_pause']
total_stack = []
for i in range(run_n):
    print('\nCorrida N#: ', i)
    left  = [0] * (trial_per_run // 2)
    rigth = [1] * (trial_per_run // 2)
    stack = left + rigth
    #print(stack)
    random.shuffle(stack)
    total_stack.append(stack)
    print(stack)
print(total_stack)

config['stack'] = total_stack
print(config)