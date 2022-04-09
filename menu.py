#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun  5 16:48:16 2021

@author: nahuel
"""
import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.animation import Animation
import os
from libb import *
from datetime import datetime

"""
DataThread
"""
import threading
import time
import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations

def reset():
    import kivy.core.window as window
    from kivy.base import EventLoop
    if not EventLoop.event_listeners:
        from kivy.cache import Cache
        window.Window = window.core_select_lib('window', window.window_impl, True)
        Cache.print_usage()
        for cat in Cache._categories:
            Cache._objects[cat] = {}

#Define our different screens
class MenuWindow(Screen):
    pass

class CalibracionWindow(Screen):
    pass

class MachineLearningWindow(Screen):
    pass

class RealtimeWindow(Screen):
    pass

class ConfiguracionCalibracionWindow(Screen):
    pass


class LabelTime (threading.Thread):
    def __init__(self, stack, time):
        threading.Thread.__init__ (self)
        self.stack = stack
        self.time = time
        print("--inicio--")
        print(self.stack)
        
    def run(self):
        labels=None
        #time.sleep(self.time//2)
        for x in self.stack:
            ts = time.time()
            print(x, ' ', ts, ' - ', datetime.fromtimestamp(ts))
            label=np.array( [ [ts], [x] ] )
            if labels is None:
                labels = label
            else:
                labels = np.append(labels, label, axis=1)
            #print("paso.. ", x, " - time: ", self.time, ts)
            time.sleep(self.time)
        return labels
            
class DataThread (threading.Thread):
    def __init__ (self, board, board_id, stack, time, path):
        threading.Thread.__init__ (self)
        self.eeg_channels = BoardShim.get_eeg_channels(board_id)
        self.sampling_rate = BoardShim.get_sampling_rate(board_id)
        self.keep_alive = True
        self.labels = None
        self.board = board
        self.path = path
        self.stack = stack
        self.sleep_time = time
        print(path)
    
    def run (self):
        #sleep_time = 1
        count=1
        total_data = None
        posiciones = None
        labels=None
        #self.stack = self.stack.reverse()
        print("stack: ", self.stack)
        while self.keep_alive:
            if self.stack != [] :
                x = self.stack.pop()
                ts = time.time()
                print(x, ' ', ts, ' - ', datetime.fromtimestamp(ts))
                label=np.array( [ [ts], [x] ] )
                if labels is None:
                    labels = label
                else:
                    labels = np.append(labels, label, axis=1)
                
            time.sleep(self.sleep_time)
            data = self.board.get_board_data()
            count=count+1
            if total_data is None:
                total_data = data                
            else:
                total_data = np.append(total_data, data, axis=1)
            print(count, ': Data Shape ', total_data.shape, ' timestamp: ', datetime.fromtimestamp(total_data[22][0]) )
               
        
        #Seleccionamos lista de timestamps
        lista_ts = total_data[22, :]
        
        labels = labels.transpose() 
        print(labels)
        #Recuperamos los labels desde el main()
        #labels=self.labels
        #Buscamos posicion del evento por proximidad ts
        for x in labels:
            resta = abs(lista_ts - x[0])
            pos = np.where(min(resta) == resta)[0]
            if posiciones is None:
                posiciones = pos
            else:
                posiciones = np.append(posiciones, pos)
                
        
        #Con las posiciones creamos matriz de eventos pos x zero x event
        events = np.zeros((len(labels) , 3), int)
        events[:, 0] = posiciones.astype(int)
        events[:, 2] = labels[:,1].astype(int)
        print(labels)
        print(events)
        
        
        print("keep_alive: ", self.keep_alive)
        print("--Fin--")
        #Seleccionamos los canales egg        
        data = total_data[1:9, :]
        #Guardamos los datos crudos
        np.save(self.path + '/data.npy', data)
        np.save(self.path + '/events.npy', events)
        np.save(self.path + '/total_data.npy', total_data)
        np.save(self.path + '/lista_ts.npy', lista_ts)
        np.save(self.path + '/labels.npy', labels)
        raw = loadDatos(data, 'ch_names.txt')
        raw.pick_channels(['P3', 'P4', 'C3', 'C4','P7', 'P8', 'O1', 'O2'])        
        #Seteamos la ubicacion de los canales segun el 
        montage = make_standard_montage('standard_1020')
        raw.set_montage(montage)
        raw.save("raw_eeg.fif", overwrite=True)
        mne.write_events("raw_eeg-eve.fif", events)
        print("chau!!!")


class StartCalibracionWindow(Screen):
            
    def animate_it(self, *args):
        #self.on_recording()
        animate = self.my_animation(self.ids.bar)
        animate.bind(on_start=lambda x,y:self.on_recording(),
                     on_complete=lambda x,y:self.on_stopping() )
        #animate.bind( on_complete=lambda x,y:self.on_stopping() )
        animate.start(self.ids.bar)

    def on_recording(self):
        print("--on_recoring--")
        #label = LabelTime(self.stack, self.time_trial)
        #label.start()
        #ret=label.join()
        #print(ret)
        
        #Calculamos name del directorio nuevo.
        path='DATA/T5'
        #Creamos directorio
        os.makedirs(path, exist_ok=True)
        
        BoardShim.enable_board_logger()
    
        params = BrainFlowInputParams()
        params.serial_port = '/dev/ttyUSB0'
        board_id = BoardIds.CYTON_BOARD.value
        
        self.board = BoardShim(board_id, params)
        self.board.prepare_session()
        self.board.start_stream()        
        self.data_thead = DataThread(self.board, board_id, self.stack, self.time_trial, path)
        self.data_thead.start()
    
    def on_stopping(self):
        print("--on_stopping--")
        self.data_thead.keep_alive = False
        self.data_thead.join()
        self.board.stop_stream()
        self.board.release_session()

    def on_rigth(self):
        print("--on_rigth--")                
        
    def on_left(self):
        print("--on_left--")         
        
    def my_animation(self, in_widget, *args):
        self.time_trial = 8
        self.run_n = 1
        self.trial_per_run = 4
        self.time_pause = 10
        self.stack = []
        
        animate = Animation(duration=0)        
        for i in range(self.run_n):
            print('\nCorrida N#: ', i)
            #Se crea lista de stack
            left  = [0] * (self.trial_per_run // 2)
            rigth = [1] * (self.trial_per_run // 2)
            self.stack = left + rigth
            #print(stack)
            random.shuffle(self.stack)
            print(self.stack)
            for x in self.stack:
                if x == 0:
                    animate = self.izquierda(animate)
                else:
                    animate = self.derecha(animate)
            animate = self.pausa(animate)
        return animate

    def derecha(self, animate):
        animate += Animation(animated_color=(0,0,1), duration=0)
        #animate += Animation( size_hint_x = 0.7, duration=self.time_trial//2 )
        animate += Animation( size_hint_x = 0.7, duration=4 )
        animate += Animation( size_hint_x = 0, duration=4 )
        return animate
    
    def izquierda(self, animate):
        animate += Animation(animated_color=(1,0,0), duration=0)
        animate += Animation( size_hint_x = -0.7, duration=4 )
        animate += Animation( size_hint_x = 0, duration=4 )
        return animate
    
    def pausa(self, animate):
        animate += Animation(animated_color=(0,0,1), duration=self.time_pause)
        #animate.start(in_widget)
        #print("pausa: ", self.time_pause)
        #time beep
        #os.system('play -nq -t alsa synth {} sine {}'.format(1, 440)) #beep
        return animate

class WindowManager(ScreenManager):
    pass

#Designate Our .kv design file
kv = Builder.load_file('menu.kv')

class AwesomeApp(App):
    def build(self):
        return kv
    
if __name__ == '__main__':
    reset()
    AwesomeApp().run()