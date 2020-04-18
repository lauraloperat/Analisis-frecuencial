"""
Juan Pablo Vasco y Laura Lopera
"""
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt


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
    
    def filtrar(self, vector, tipo_umbral, umbral, ponderado):
        '''
        Parameters
        ----------
        vector : corresponde a todos los valores de la señal del canal seleccionado.
        tipo_umbral : forma de filtrado seleccionada por el usuario (hard, soft).
        umbral :tipo de umbral seleccionada por el usuario(universal, minimax, sure).
        ponderado : forma de aplicacion del peso seleccionada por el usuario (one, SLN, MLN).
        Returns
        -------
        filtrada_reconstruida : señal final filtrada.
        '''
        
        nivel_final=np.floor(np.log2(vector.shape[0]/2) -1) #se establece cuantas veces se hace la descomposicion
        
        t_haar = self.decompose(vector, 1, nivel_final, []) #se llama a la funcion descomponer 
        
        thr = self.umbral(umbral, t_haar) #se llama a la funcion umbral
        
        pesos = self.ponderado(ponderado, t_haar) #se llama a la funcion ponderado
                     
        filtrada = self.tipo_umbral(tipo_umbral, t_haar, pesos, thr) #se llama la funcion tipo umbral
        
        filtrada_reconstruida = self.rebuild(filtrada, 1, nivel_final, []) #se llama a la funcion que recompone la señal
        
        return filtrada_reconstruida
    
    
    def decompose(self, x, nivel_actual, nivel_final, t_haar):
        '''
        Parameters
        ----------
        x : corresponde al vector que corresponde a la señal en el canal especificado.
        nivel_actual : funciona como un contador.
        nivel_final : corresponde a cuantas veces se debe hacer la descomposicion.
        t_haar : es un vector que al llamar la funcion almacena los valores de la transformada Haar.
        Returns
        -------
        Devuelve el vector que contiene los valores de la transformada Haar.
        '''
    
        s = np.array([(1/np.sqrt(2)), (1/np.sqrt(2))]) #definicion del valor de scale
        w = np.array([(-1/np.sqrt(2)), (1/np.sqrt(2))])   #definicion del valor de wavelet          
        
        if (nivel_actual <= nivel_final):
            if (x.shape[0] %2) != 0:
                x = np.append(x, 0) 
        #mientras nivel actual sea menor o igual a nivel final, se hace la transformada Haar
        scale_x = np.convolve(x, s, 'full')
        aprox_x = scale_x[1::2] #se submuestrea

        wavelet_x = np.convolve(x, w, 'full')
        detail_x = wavelet_x[1::2] #se submuestrea

        t_haar.append(detail_x)

        if (nivel_actual < nivel_final):
            return self.decompose(aprox_x, nivel_actual+1, nivel_final, t_haar)
        #mientras nivel actual sea menor a nivel final, la funcion se llama a si misma
        t_haar.append(aprox_x)
        
        return t_haar
        
    def umbral(self, umbral, vector):
        '''
        Devuelve el valor del umbral, segun lo seleccionado por el usuario (universal, minimax, sure)
        '''
        Num_samples=0 #actua como un contador
        for i in range(len(vector)):
            Num_samples = Num_samples + len(vector[i]) #se saca el numero de muestras dependiendo del detalle a analizar
        
        if umbral == 0: #umbral universal
            thr = np.sqrt(2*(np.log(Num_samples)))
                    
        if umbral == 1: #umbral minimax
            thr = 0.3936 + 0.1829*((np.log(Num_samples))/np.log(2))
                    
        if umbral == 2: #umbral sure
            
            sx2=[]
            risk=[]
            for i in range(len(vector)):
                sx2 = np.append(sx2, vector[i])
                
            sx2 = np.power(np.sort(np.abs(sx2)),2)
            #se implementa la ecuacion de sure
            risk = (Num_samples-(2*np.arange(1,Num_samples + 1)) + (np.cumsum(sx2[0:Num_samples])) + np.multiply(np.arange(Num_samples,0,-1), sx2[0:Num_samples]))/Num_samples
            #Se selecciona el mejor valor como el mínimo valor del vector anterior
            best = np.min(risk)
            #Se redondea a un entero
            redondeo = int(np.round(best))
            #Se toma la raiz cuadrada del valor en la posición "best" 
            thr = np.sqrt(sx2[redondeo])
        return thr
    
    def ponderado(self, ponderado, vector):
        '''
        Devuelve los pesos de los detalles segun el tipo de ponderacion elegido (one,SLN, MLN)
        '''
        
        pesos = np.zeros(len(vector))
        detail1 = vector[0]
        
        if ponderado == 0: #ponderado one
            pesos[:] = 1
            
        if ponderado == 1: #ponderado SLN
            peso_detail1 = (np.median(np.absolute(detail1)))/0.6745
            pesos[:] = peso_detail1 #todos los detalles se multiplican por el peso del detalle 1 
        
        if ponderado == 2: #ponderado MLN
            for i in range(len(vector)):
                peso_detail_x = (np.median(np.absolute(vector[i])))/0.6745
                pesos[i] = peso_detail_x #se multiplica cada detalle por su peso correspondiente
        return pesos
    
    def tipo_umbral(self, tipo_umbral, vector, pesos, thr):
        '''
      Devuelve el vector de los detalles y la aproximacion dependiendo del tipo de filtrado seleccionado (hard, soft)
        '''
        
        umbrales_definitivos = pesos*thr
        
        if tipo_umbral == 0: #filtrado hard
            
            for i in range(len(vector)-1): #para recorrer el vector de transformada Haar
                for j in range(len(vector[i])): #para recorrer cada posicion de cada detalle
                    if np.abs(vector[i][j]) < umbrales_definitivos[i]:
                        vector[i][j] = 0 #si el valor del detalle en esa posicion es menor que el umbral, se hace cero
                    else:
                        pass #si el valor del detalle en esta posicion es mayor al umbral, permanece igual
            
        if tipo_umbral == 1: #filtrado soft
            
            for i in range(len(vector)-1):#para recorrer el vector de transformada Haar
                for j in range(len(vector[i])): #para recorrer cada posicion de cada detalle
                    if np.abs(vector[i][j]) < umbrales_definitivos[i]:
                        vector[i][j] = 0 #si el valor del detalle en esa posicion es menor que el umbral, se hace cero
                    else: #si el valor del detalle en esta posicion es mayor al umbral, se ejecuta la ecuacion
                        sgn = np.sign(vector[i][j])
                        resta = np.abs(vector[i][j]) - umbrales_definitivos[i]
                        vector[i][j] = sgn*resta
        return vector
        
    def rebuild(self, t_haar, nivel_actual, nivel_final, x):
        '''
        Parameters
        ----------
        t_haar : vector de transformada Haar, entregado por decompose.
        x : corresponde al vector que corresponde a la señal en el canal especificado.
        nivel_actual : funciona como un contador.
        nivel_final : corresponde a cuantas veces se debe hacer la reconstruccion.
        Returns
        -------
        Devuelve el vector de la señal reconstruida.
        '''
    
        s_inv = np.array([(1/np.sqrt(2)), (1/np.sqrt(2))]) #definicion del valor de scale
        w_inv = np.array([(1/np.sqrt(2)), (-1/np.sqrt(2))])#definicion del valor de wavelet
             
        size = len(t_haar) 
        detalle = t_haar[size - 1 - nivel_actual] #para recorrer todas las posiciones correspondientes a los detalles
        
        if (nivel_actual <= nivel_final):
            if (nivel_actual==1):
                npoints_aprox = len(t_haar[len(t_haar)-1])
                aprox_inv = np.zeros(2*npoints_aprox)
                aprox_inv[0::2] = t_haar[size-1]# se sobremuestrea          
        
            else:
                if (len(x) > len(detalle)):
                    x = x[0:len(detalle)]
                npoints_aprox = len(x)
                aprox_inv = np.zeros(2*npoints_aprox)
                aprox_inv[0::2] = x #se sobremuestrea
            
            aprox_x = np.convolve(aprox_inv, s_inv, 'full') #se realiza la convolucion con scale inverso
            
            detail_inv = np.zeros(2*npoints_aprox)
            detail_inv[0::2] = detalle
            
            detail_x = np.convolve(detail_inv, w_inv, 'full') #se realiza la convolucion con wavelet inverso 
            
            x = aprox_x + detail_x

            return self.rebuild(t_haar, nivel_actual+1, nivel_final, x) #la funcion se llama a si misma y se aumenta el nivel actual (contador)
        
        return x
