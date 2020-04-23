"""
Juan Pablo Vasco y Laura Lopera
"""
import numpy as np
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
        #se toman los valores que se necesitan en la biosenal

        return self.__data[:,x_min:x_max] 
    
    def calcularWavelet(self,senal,fmin,fmax,fs):
        """        
        Parameters
        ----------
        senal : datos a los que se le aplicaran el Wavelet continuo.
        fmin : frecuencia minima de interes.
        fmax : frecuencia maxima de interes.
        fs : frecuencia de muestreo de la senal.

        Returns
        -------
        time : rango de tiempo del espectro.
        freqs : rengo de frecuencias del espectro.
        power : rango de potencias del espectro.

        """
                        
        #analisis usando wavelet continuo

        sampling_period =  1/fs
        Frequency_Band = [fmin, fmax] # Banda de frecuencia a analizar
        
        
        # se determinan las frecuencias respectivas para una escala definida
        scales = np.arange(1, 250)
        frequencies = pywt.scale2frequency('cmor', scales)/sampling_period
        # se extraen las escalas correspondientes a la banda de frecuencia a analizar
        scales = scales[(frequencies >= Frequency_Band[0]) & (frequencies <= Frequency_Band[1])] 
        
        N = senal.shape[0]
    
        # se obtiene el tiempo correspondiente a una epoca de la senal
        time_epoch = sampling_period*N
        
        # se analiza una epoca 
        # se obtiene el vector de tiempo
        time = np.arange(0, time_epoch, sampling_period)
        
        [coef, freqs] = pywt.cwt(senal, scales, 'cmor', sampling_period)
        # se calcula la potencia 
        power = (np.abs(coef)) ** 2
        
        return time, freqs, power
