#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 23:59:47 2020

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


class TrainML:

    def run(self):
        config_train_ml = loadConfig("config.ini", "TRAIN_ML")
        path = config_train_ml['path']
        tmin = config_train_ml['tmin']
        tmax = config_train_ml['tmax']
        
        low_freq, high_freq = 7., 30.
        print("tmin: ",tmin," - tmax: ", tmax )
    #    tmin, tmax = 0.5, 1.5
    #    tmin, tmax = 2, 4
        
        # event_id
        event_id = {'right': 1, 'left': 0}
        acurracy = []
        """        
        path_raiz = 'DATA/'
        name = 'T21'
        path = path_raiz + name        
        #Se carga set de datos crudos
        data = np.load(path + '/data.npy')
        #data = data.transpose()
        print("data: ", data.shape)
        
        #Se carga la matriz de eventos
        events= np.load(path +'/events.npy')
    
        #Data Señal
        raw = loadDatos(data, 'ch_names.txt')
        
        #Seleccionamos los canales a utilizar
        raw.pick_channels(['P3', 'P4', 'C3', 'C4','P7', 'P8', 'O1', 'O2'])
        
        #Seteamos la ubicacion de los canales segun el 
        montage = make_standard_montage('standard_1020')
        raw.set_montage(montage)
        
        # Se aplica filtros band-pass
        raw.filter(low_freq, high_freq, fir_design='firwin', skip_by_annotation='edge')
        
        print(type(raw))
        print(type(events))
        """
        raw = mne.io.read_raw_fif(path + "/raw_eeg.fif", preload=True)
        raw.filter(low_freq, high_freq, fir_design='firwin', skip_by_annotation='edge')
    
        #sample_data_events_file = os.path.join(sample_data_folder, 'MEG', 'sample','sample_audvis_raw-eve.fif')
        events = mne.read_events(path + "/raw_eeg-eve.fif")
        
        print(type(raw))
        print(type(events))
        #Se genera las epocas con los datos crudos y los eventos
        epochs = mne.Epochs(raw, events=events, event_id=event_id, tmin=tmin, tmax=tmax, baseline=None, preload=True, verbose=False)
        
        #Se carga target (convierte 1 -> -1 y 2 -> 0 )
        #target = epochs.events[:, -1] - 2
        target = epochs.events[:, -1]
        #print(epochs.events[:, -1])
        print(target)
        
        #Lo convierte a matriz numpy
        epochs_data = epochs.get_data()
        
        #Se crea set de de pruebas y test
        X_train, X_test, y_train, y_test = train_test_split(epochs_data, target, test_size=0.2, random_state=0)
            
        #Guardamos los set de datos
        np.save(path + '/X_train.npy', X_train)
        np.save(path + '/y_train.npy', y_train)
        np.save(path + '/X_test.npy', X_test)
        np.save(path + '/y_test.npy', y_test)
        
        """
        print(X_train.shape)
        print(y_train.shape)
        print(X_test.shape)
        print(y_test.shape)
        
        print(type(X_train))
        print((y_train))
        print(type(X_test))
        print((y_test))
        """
        
        #Clasificadores del modelo
        csp = CSP(n_components=2, reg=None, log=True, norm_trace=False)
        lda = LinearDiscriminantAnalysis()
        
        #Modelo utiliza CSP y LDA
        model = Pipeline([('CSP', csp), ('LDA', lda)])    
        print(epochs_data.shape )
        #Entrenamiento del modelo
        model.fit(X_train, y_train)
        
        score = model.score(X_train, y_train)
        print("Score entrenamiento: ", score)
        # plot CSP patterns estimated on full data for visualization
        #csp.fit_transform(epochs_data, target)
        #csp.plot_patterns(epochs.info, ch_type='eeg', size=1.5)
        
        #Resultados
        result=model.predict(X_test)
        
        #Guardamos el modelo
        joblib.dump(model, path + '/model.pkl')
        
        #Variables report
        ts = time.time()
        matriz=met.confusion_matrix(y_test, result)
        report=met.classification_report(y_test, result)
        
        #Mostrar report
        print(ts, ' - ', datetime.fromtimestamp(ts))
        print(matriz)
        print(report)
            
        #Archivo de salida
        fout=open(path + "/output.txt","a")
        fout.write(str(datetime.fromtimestamp(ts)) + "\n")
        fout.write(str(matriz) + "\n")
        fout.write(str( report))
        fout.write("\n")
        fout.close()