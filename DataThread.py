#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  3 20:05:21 2022

@author: nahuel
"""
"""
DataThread
"""
import threading
import time
import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations
import os
from libb import *
from datetime import datetime

class DataThread (threading.Thread):
    def __init__ (self, board, board_id, config):
        threading.Thread.__init__ (self)
        self.eeg_channels = BoardShim.get_eeg_channels(board_id)
        self.sampling_rate = BoardShim.get_sampling_rate(board_id)
        self.path = config['path']
        self.total_stack = config['total_stack']
        self.time_trial = config['time_trial']
        self.time_pause= config['time_pause']
        self.time_initial = config['time_initial']
        self.keep_alive = True
        self.labels = np.ndarray(shape=(2, 0))
        self.total_data = np.ndarray(shape=(23, 0))
        self.board = board
   
    def run(self):
        print("stack: ", self.total_stack)
        self.getData(self.time_initial)
        while self.keep_alive:
            if self.total_stack != []:
                stack = self.total_stack.pop(0)
                print(stack)
                for x in stack:
                    ts = time.time()
                    print(x, ' ', ts, ' - ', datetime.fromtimestamp(ts))
                    label=np.array( [ [ts], [x] ] )
                    self.labels = np.append(self.labels, label, axis=1)
                    self.getData(self.time_trial)
                self.getData(self.time_pause)
            else:
                self.getData(1)
        #calculamos los eventos
        events = self.getEvent()
        #Seleccionamos los canales eeg        
        data_eeg = self.total_data[1:9, :]
        #grabamos
        self.save(data_eeg, events)
        print("--Fin--")
        
    def getData(self, ts):
        start_time = time.time()
        for i in range(ts):
            time.sleep(0.994)
            data = self.board.get_board_data()
            self.total_data = np.append(self.total_data, data, axis=1)
            #print(i,': data shape ', data.shape, ' - total_data shape ', self.total_data.shape, ' timestamp: ', datetime.fromtimestamp(data[22][0]) )
        elapsed_time = time.time() - start_time
        print("Elapsed time: %0.10f seconds." % elapsed_time)
        
    def getEvent(self):
        posiciones = np.array( [] )
        #Seleccionamos lista de timestamps
        lista_ts = self.total_data[22, :]
        self.labels = self.labels.transpose()
        #Recuperamos los labels desde el main()
        #Buscamos posicion del evento por proximidad ts
        for x in self.labels:
            resta = abs(lista_ts - x[0])
            pos = np.where(min(resta) == resta)[0]
            pos_1 = pos[0]
            posiciones = np.append(posiciones, pos_1)
        #Con las posiciones creamos matriz de eventos pos x zero x event
        events = np.zeros((len(self.labels) , 3), int)
        events[:, 0] = posiciones.astype(int)
        events[:, 2] = self.labels[:,1].astype(int)
        return events
    
    def save(self, data, events):
        #Creamos directorio
        os.makedirs(self.path, exist_ok=True)
        #Guardamos los datos crudos
        raw = loadDatos(data, 'ch_names.txt')
        raw.pick_channels(['P3', 'P4', 'C3', 'C4','P7', 'P8', 'O1', 'O2'])        
        #Seteamos la ubicacion de los canales segun el 
        montage = make_standard_montage('standard_1020')
        raw.set_montage(montage)
        raw.save(self.path + "/raw_eeg.fif", overwrite=True)
        mne.write_events(self.path + "/raw_eeg-eve.fif", events)