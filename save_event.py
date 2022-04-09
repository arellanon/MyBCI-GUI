#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  9 12:33:48 2022

@author: nahuel
"""
#librerias
import numpy as np
import time
from datetime import datetime
#from loaddata import *

#sklearn
from sklearn.model_selection import ShuffleSplit, cross_val_score, cross_val_predict
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn import metrics as met
import joblib

#mne
import mne
from mne.decoding import CSP
from mne.channels import read_layout
from mne.channels import make_standard_montage
from mne.preprocessing import (create_eog_epochs, create_ecg_epochs,
                               compute_proj_ecg, compute_proj_eog)
from libb import *

def main():   
    low_freq, high_freq = 7., 30.
    
    path = 'DATA/T4/'
    
    #Se carga set de datos crudos
    #data = np.load(path + '/data.npy')
    #Data Señal
    data = np.load(path + '/data.npy')
    #data = data.transpose()
    print("data: ", data.shape)
    
    #Se carga la matriz de eventos
    events= np.load(path +'/events.npy')
    print(events)
    
    raw = loadDatos(data, 'ch_names.txt')
    
    
    #Seleccionamos los canales a utilizar
    raw.pick_channels(['P3', 'P4', 'C3', 'C4','P7', 'P8', 'O1', 'O2'])
    #print('raw select: ', raw.shape)
    
    #Seteamos la ubicacion de los canales segun el 
    montage = make_standard_montage('standard_1020')
    raw.set_montage(montage)
    
    #raw.plot(scalings='auto', n_channels=8, duration=20)
    #raw.plot(scalings='auto', n_channels=1, events=events)
    raw.plot(scalings='auto', n_channels=1)
    # Se aplica filtros band-pass
    #raw.filter(low_freq, high_freq, fir_design='firwin', skip_by_annotation='edge')
    raw.save("eeg.fif", overwrite=True)
    mne.write_events("event.fif", events)
    
if __name__ == "__main__":
    main()