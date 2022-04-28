#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 19:58:01 2022

@author: nahuel
"""
import numpy as np
from datetime import datetime
import time

stack = [0, 1, 1, 0]
#labels = np.array([])
#print(labels.shape)
labels = None
while stack:
    x = stack.pop()
    ts = time.time()
    label=np.array( [ [ts], [x] ] )
    #print(label)
    #print(label.shape)
    if labels is None:
        labels = label
        #print(labels.shape)
    else:
        labels = np.append(labels, label, axis=1)

print(labels)
print(labels.shape)
print(labels.ndim)


stack = [0, 1, 1, 0]
#labels = np.array( [[],[]] )
#labels = np.shape(2, 0)
print(labels.shape)
while stack:
    x = stack.pop()
    ts = time.time()
    label=np.array( [ [ts], [x] ] )
    #print(label)
    #print(label.shape)
    labels = np.append(labels, label, axis=1)
#labels = np.append(labels, label, axis=1)
print(labels)
print(labels.shape)



"""
    def run (self):
        #sleep_time = 1
        count=1
        total_data = None
        posiciones = None
        labels = np.array([])
        #self.stack = self.stack.reverse()
        print("stack: ", self.stack)
        while self.keep_alive:
            if self.stack != [] :
                x = self.stack.pop()
                ts = time.time()
                print(x, ' ', ts, ' - ', datetime.fromtimestamp(ts))
                label=np.array( [ [ts], [x] ] )
                labels = np.append(labels, label, axis=1)
                
            time.sleep(self.sleep_time)
            data = self.board.get_board_data()
            count=count+1
            if total_data is None:
                total_data = data                
            else:
                total_data = np.append(total_data, data, axis=1)
            print(count, ': Data Shape ', total_data.shape, ' timestamp: ', datetime.fromtimestamp(total_data[22][0]) )
               
"""        