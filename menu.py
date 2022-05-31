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
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations
from DataThread import *
from TrainML import *
from kivy.properties import StringProperty

"""
DataThread

import threading
import time
import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations
import os
from libb import *
from datetime import datetime
"""

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
    
    def start_train(self, *args):
        print("test!")
        train = TrainML()
        train.run()

class ConfiguracionMachineLearningWindow(Screen):
    def load_it(self, *arg):
        config_train_ml = loadConfig("config.ini", "TRAIN_ML")
        self.ids.tmin.text = str(config_train_ml['tmin'])
        self.ids.tmax.text = str(config_train_ml['tmax'])
        self.ids.path.text = config_train_ml['path']
        
    def save_it(self, *arg):
        config_train_ml = {}
        config_train_ml['tmin'] = self.ids.tmin.text
        config_train_ml['tmax'] = self.ids.tmax.text
        config_train_ml['path'] = self.ids.path.text
        print(config_train_ml)
        saveConfig("config.ini", 'TRAIN_ML', config_train_ml)

class RealtimeWindow(Screen):
    pass

class ConfiguracionCalibracionWindow(Screen):
    #config_calibration = loadConfig("config.ini", "CALIBRATION")
    def __init__(self, **kwargs):
        super(ConfiguracionCalibracionWindow, self).__init__(**kwargs)
        print(self.ids)
        
    def load_it(self, *arg):
        config_calibration = loadConfig("config.ini", "CALIBRATION")
        self.ids.time_initial.text = str(config_calibration['time_initial'])
        self.ids.time_trial.text = str(config_calibration['time_trial'])
        self.ids.run_n.text = str(config_calibration['run_n'])
        self.ids.trial_per_run.text = str(config_calibration['trial_per_run'])
        self.ids.time_pause.text = str(config_calibration['time_pause'])
        self.ids.path.text = config_calibration['path']
        
    def save_it(self, *arg):
        config_calibration = {}
        config_calibration['time_initial']= int(self.ids.time_initial.text)
        config_calibration['time_trial']= int(self.ids.time_trial.text)
        config_calibration['run_n']= int(self.ids.run_n.text)
        config_calibration['trial_per_run']= int(self.ids.trial_per_run.text)
        config_calibration['time_pause']= int(self.ids.time_pause.text)
        config_calibration['path']= self.ids.path.text
        print(config_calibration)
        saveConfig("config.ini", 'CALIBRATION', config_calibration)

class StartCalibracionWindow(Screen):
            
    def animate_it(self, *args):
        config_calibration = loadConfig("config.ini", "CALIBRATION")
        #self.config = {'time_initial': 5, 'time_trial': 8, 'run_n': 1, 'trial_per_run': 10, 'time_pause': 10, 'path': 'DATA/T11'}
        self.config = config_calibration
        self.total_stack = self.calculate_stack()
        print(self.config)
        animate = self.my_animation(self.ids.bar)
        animate.bind(on_start=lambda x,y:self.on_recording(),
                     on_complete=lambda x,y:self.on_stopping() )
        animate.start(self.ids.bar)
                
    def on_recording(self):
        print("--on_recoring--")
        BoardShim.enable_board_logger()
    
        params = BrainFlowInputParams()
        params.serial_port = '/dev/ttyUSB0'
        board_id = BoardIds.CYTON_BOARD.value
        
        self.board = BoardShim(board_id, params)
        self.board.prepare_session()
        self.board.start_stream()
        self.data_thead = DataThread(self.board, board_id, self.config, self.total_stack)
        self.data_thead.start()
    
    def on_stopping(self):
        print("--on_stopping--")
        self.data_thead.keep_alive = False
        self.data_thead.join()
        self.board.stop_stream()
        self.board.release_session()
        
    def my_animation(self, in_widget, *args):        
        #total_stack = self.config['total_stack']
        total_stack = self.total_stack
        time_initial = self.config['time_initial']
        #time_initial = 0
        
        animate = Animation(duration=time_initial)
        for stack in total_stack:
            for x in stack:
                if x == 0:
                    animate = self.izquierda(animate)
                else:
                    animate = self.derecha(animate)
            animate = self.pausa(animate)
        return animate

    def derecha(self, animate):
        time_trial = self.config['time_trial']        
        animate += Animation(animated_color=(0,0,1), duration=0)
        animate += Animation( size_hint_x = 0.7, duration=time_trial//2 )
        animate += Animation( size_hint_x = 0, duration=time_trial//2 )
        return animate
    
    def izquierda(self, animate):
        time_trial = self.config['time_trial']
        animate += Animation(animated_color=(1,0,0), duration=0)
        animate += Animation( size_hint_x = -0.7, duration=time_trial//2 )
        animate += Animation( size_hint_x = 0, duration=time_trial//2 )
        return animate
    
    def pausa(self, animate):
        time_pause= self.config['time_pause']
        #time_pause+=1
        animate += Animation(animated_color=(0,0,1), duration=time_pause)
        #animate.start(in_widget)
        #print("pausa: ", self.time_pause)
        #time beep
        #os.system('play -nq -t alsa synth {} sine {}'.format(1, 440)) #beep
        return animate
    
    def calculate_stack(self):
        time_trial = self.config['time_trial']
        run_n = self.config['run_n']
        trial_per_run = self.config['trial_per_run']
        time_pause= self.config['time_pause']
        total_stack = []
        for i in range(run_n):
            left  = [0] * (trial_per_run // 2)
            rigth = [1] * (trial_per_run // 2)
            stack = left + rigth
            random.shuffle(stack)
            total_stack.append(stack)
        return total_stack

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
