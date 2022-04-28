#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 17:39:28 2022

@author: nahuel
"""
import numpy as np
import mne
from libb import *
import random



def getStack(run_n, trial_per_run):
    result=[]
    for i in range(run_n):
        print('\nCorrida N#: ', i)
        #Se crea lista de stack
        left  = [0] * (trial_per_run // 2)
        rigth = [1] * (trial_per_run // 2)
        stack = left + rigth
        random.shuffle(stack)
        result.append(stack)
    return(result)

print("hola mundo!")
#event = mne.make_fixed_length_events()
path_raiz = 'DATA/'
name = 'T5'
path = path_raiz + name

data = np.load(path + '/data.npy')
lista_ts = np.load(path + '/lista_ts.npy')
#raw = loadDatos(data, 'ch_names.txt')


#event = mne.make_fixed_length_events(raw, id=1, start=0, stop=None, duration=1.0, first_samp=True, overlap=0.0)
#events = np.load(path +'/events.npy')
labels = np.load(path + '/labels.npy')

#Recuperamos los labels desde el main()
#labels=self.labels
#Buscamos posicion del evento por proximidad ts
"""
posiciones=None
for x in labels:
    print("x: ", x)
    resta = abs(lista_ts - x[0])
    pos = np.where(min(resta) == resta)[0]
    if posiciones is None:
        posiciones = pos
    else:
        posiciones = np.append(posiciones, pos)


print(raw.times)
print(raw.ch_names)
print(raw.n_times)
print(len(raw.times))
print(raw.times[2])
"""


configuration = { "time_trial" : 8, "run_n" : 1, "trial_per_run" : 4, "time_pause" : 10, "time_pause_initial" : 5}
print(configuration)
stack = getStack(configuration["run_n"], configuration["trial_per_run"])
print(stack)

