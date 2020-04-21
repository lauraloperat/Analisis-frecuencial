# -*- coding: utf-8 -*-
"""
Juan Pablo Vasco y Laura Lopera
"""
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt
import pywt #1.1.1


class Biosenal(object):
    def __init__(self,data=None):
        if not data == None:
            self.asignarDatos(data)
        else:
            self.__data=np.asarray([])
            self.__canales=0
            self.__puntos=0
    def asignarDatos(self,data):
        self.__data=data
        self.__canales=data.shape[0]
        self.__puntos=data.shape[1]
    #necesitamos hacer operacioes basicas sobre las senal, ampliarla, disminuirla, trasladarla temporalmente etc
    def devolver_segmento(self,x_min,x_max):
        '''
        Parameters
        ----------
        x_min : valor minimo del rango.
        x_max : valor maximo del rango.

        Returns
        -------
        Devuelve los valores de la señal que esten dentro del rango descrito.

        '''
        if x_min>=x_max:
            return None #si el valor minimo del rango es mayor o igual al maximo, no retorna nada
        #cojo los valores que necesito en la biosenal

        return self.__data[:,x_min:x_max]
    def calcularWavelet(self,senal,fmin,fmax,fs):

        #analisis usando wavelet continuo

        sampling_period =  1/fs
        Frequency_Band = [fmin, fmax] # Banda de frecuencia a analizar

        # Métodos de obtener las escalas para el Complex Morlet Wavelet
        # Método 1:
        # Determinar las frecuencias respectivas para una escalas definidas
        scales = np.arange(1, 250)
        frequencies = pywt.scale2frequency('cmor', scales)/sampling_period
        # Extraer las escalas correspondientes a la banda de frecuencia a analizar
        scales = scales[(frequencies >= Frequency_Band[0]) & (frequencies <= Frequency_Band[1])]

        N = senal.shape[0]

        # Obtener el tiempo correspondiente a una epoca de la señal (en segundos)
        time_epoch = sampling_period*N

        # Analizar una epoca de un montaje (con las escalas del método 1)
        # Obtener el vector de tiempo adecuado para una epoca de un montaje de la señal
        time = np.arange(0, time_epoch, sampling_period)
        # Para la primera epoca del segundo montaje calcular la transformada continua de Wavelet, usando Complex Morlet Wavelet

        [coef, freqs] = pywt.cwt(senal, scales, 'cmor', sampling_period)
        # Calcular la potencia
        power = (np.abs(coef)) ** 2

        return time, freqs, power
