import sys
import numpy as np
#Qfiledialog es una ventana para abrir yu gfuardar archivos
#Qvbox es un organizador de widget en la ventana, este en particular los apila en vertcal
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QFileDialog, QMessageBox
from PyQt5 import QtCore, QtWidgets

from matplotlib.figure import Figure
from PyQt5.QtGui import QIntValidator

from PyQt5.uic import loadUi

from numpy import arange, sin, pi
#contenido para graficos de matplotlib
from matplotlib.backends. backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from csv import reader as reader_csv
import matplotlib.pyplot as plt

import scipy.io as sio
import numpy as np
from Modelo import Biosenal
# clase con el lienzo (canvas=lienzo) para mostrar en la interfaz los graficos matplotlib, el canvas mete la grafica dentro de la interfaz
class MyGraphCanvas(FigureCanvas):
    #constructor
    def __init__(self, parent= None,width=5, height=4, dpi=100):
        
        #se crea un objeto figura
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        #el axes en donde va a estar mi grafico debe estar en mi figura
        self.axes = self.fig.add_subplot(111)
                
        #se inicializa la clase FigureCanvas con el objeto fig
        FigureCanvas.__init__(self,self.fig)
        
   
    def graficar_gatos(self,datos):
        '''
        Permite graficar los datos de la senal
        '''
        
        self.axes.clear() #se limpia la grafica anterior
        self.axes.plot(datos) # se ingresan los datos a graficar
  
        #Se grafica en un mismo plano varias senales 
        for c in range(datos.shape[0]):
            self.axes.plot(datos[c,:]+c*10)
        self.axes.set_xlabel("Muestras")
        self.axes.set_ylabel("Amplitud")
        self.axes.figure.canvas.draw()
        
    def select_canal(self,senal,canal):
        '''
     Permite seleccionar el canal que ingrese el usuario y graficarlo
        '''
      
        if canal <= (len(senal)-1): #valida si el canal ingresado por el usuario existe
    
            self.axes.clear()
            if senal.ndim>1:
                self.axes.plot(senal[canal,:])
            else:
               self.axes.plot(senal)
            
            self.axes.set_xlabel("Tiempo")
            self.axes.set_ylabel("Amplitud")
        
            self.axes.figure.canvas.draw()
        else: #si el canal no existe, genera una ventana emergente
            msg=QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setText("Informacion")
            msg.setWindowTitle('Advertencia')
            msg.setInformativeText('Canal inexistente')
            msg.show()
            
    
#%%

class InterfazGrafico(QMainWindow):
# se define esta clase para crear la interfaz grafica
    def graficar_canal (self):
        '''
        Permite graficar el canal seleccionado por el usuario
        '''
        canal = int(self.campo_canal.text())
        self.__sc.select_canal(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max),canal)
        
        # se activan botones relacionados con filtrar
        self.tipo_umbral.setEnabled(True)
        self.umbral.setEnabled(True)
        self.ponderacion.setEnabled(True) 
        self.boton_graficarf.setEnabled(True)
        
    def filtro(self):
        '''
        Permite devolver el vector de la senal filtrada
        '''
        canal= int(self.campo_canal.text())
        x=self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max)[canal,:] #se definen los datos del canal seleccionado
        tipo_umbral = self.tipo_umbral.currentIndex()
        umbral=self.umbral.currentIndex()
        ponderacion=self.ponderacion.currentIndex()
        filtrada=self.__coordinador.filtrar(x, tipo_umbral, umbral, ponderacion)
        return filtrada    
        
        
    def graficar_filtrada(self):
        '''
        Grafica la senal filtrada
        '''
            
        self.__sc1.select_canal((self.filtro()),0) 
        
        # se habilitan los botones de escalado temporal y guardar senal
        self.lim_inf.setEnabled(True)
        self.lim_sup.setEnabled(True)
        self.escalar.setEnabled(True)
        self.boton_guardar.setEnabled(True)

    def habilitar(self):
        ''' 
        Habilita el boton para seleccionar el canal
        '''
        self.boton_canal.setEnabled(True)
            
    def habilitar_s1(self):
        ''' 
        Habilita el boton para graficar y el campo para elegir el canal
        '''
        self.boton_graficar.setEnabled(True)
        self.campo_canal.setEnabled(True)
            
    def habilitar_desplazamiento(self):
        ''' 
        Habilita los botones de escalado 
        '''
        self.atras.setEnabled(True)
        self.adelante.setEnabled(True)
    
    def escalado_temporal(self):
        ''' 
        Muestra la grafica de las senales en el rango de muestras seleccionado por el usuario
        '''
        
        lim_inf = int(self.lim_inf.text())
        lim_sup = int(self.lim_sup.text())
        
        self.__x_max = lim_sup
        self.__x_min = lim_inf
        
        if (lim_inf >= lim_sup): # si el limite inferior es mayor al superior sale una ventana emergente de advertencia
            
            msg=QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setText("Informacion")
            msg.setWindowTitle('Advertencia')
            msg.setInformativeText('Rango invalido')
            msg.show()
        else:
            
            self.graficar_canal()
            self.graficar_filtrada()
            
    def desplazar_atras(self):
        ''' 
        Permite realizar el desplazamiento de las senales hacia atras
        '''
        # se re-definen los limite superior e inferior
        nuevo_lim_inf = self.__x_min - 25
        nuevo_lim_sup =self.__x_max - 25
        
        self.__x_max = nuevo_lim_sup
        self.__x_min = nuevo_lim_inf
        
        self.graficar_canal()
        self.graficar_filtrada()
        
    def desplazar_adelante(self):
        ''' 
        Permite realizar el desplazamiento de las senales hacia adelante
        '''
        # se re-definen los limite superior e inferior
        nuevo_lim_inf = self.__x_min + 25
        nuevo_lim_sup = self.__x_max + 25
        
        self.__x_max = nuevo_lim_sup
        self.__x_min = nuevo_lim_inf
        
        self.graficar_canal()
        self.graficar_filtrada()

    
    def __init__(self):
        #inicializa la clase interfaz grafico
        super(InterfazGrafico,self).__init__()
        #se carga el diseno creadi
        loadUi ('anadir_grafico.ui',self)
        #se llama la rutina donde se configura la interfaz
        self.setup()
        #se muestra la interfaz
        self.show()
    def setup(self):
        #los layout permiten organizar widgets en un contenedor
        # se crea el primer espacio
        layout = QVBoxLayout()
        #se añade el organizador al campo grafico
        self.campo_grafico.setLayout(layout)
        #se crea un objeto para manejo de graficos
        self.__sc = MyGraphCanvas(self.campo_grafico, width=5, height=4, dpi=100)
        #se añade el campo de graficos
        layout.addWidget(self.__sc)
        
        # se crea el segundo espacio
        layout1= QVBoxLayout()
        self.campo_grafico1.setLayout(layout1)
        #se crea un objeto para manejo de graficos
        self.__sc1 = MyGraphCanvas(self.campo_grafico1, width=5, height=4, dpi=100)
        #se añade el campo de graficos
        layout1.addWidget(self.__sc1)
        
        # se definen los botones y los campos
        self.boton_canal.setEnabled(False)
        self.lim_inf.setEnabled(False)
        self.lim_sup.setEnabled(False)
        self.escalar.setEnabled(False)
        self.atras.setEnabled(False)
        self.adelante.setEnabled(False)
        self.tipo_umbral.setEnabled(False)
        self.umbral.setEnabled(False)
        self.ponderacion.setEnabled(False) 
        self.boton_guardar.setEnabled(False)
        self.boton_cargar.clicked.connect(self.cargar_senal)
        self.boton_cargar.clicked.connect(self.habilitar)
        self.campo_canal.setEnabled(False)
        self.boton_graficar.setEnabled(False)
        self.boton_graficarf.setEnabled(False)
        self.boton_canal.clicked.connect(self.habilitar_s1)
        self.boton_graficar.clicked.connect(self.graficar_canal)
        self.boton_graficarf.clicked.connect(self.graficar_filtrada)
        self.campo_canal.setValidator(QIntValidator(0,50))
        self.escalar.clicked.connect(self.escalado_temporal)
        self.escalar.clicked.connect(self.habilitar_desplazamiento)
        self.atras.clicked.connect(self.desplazar_atras)
        self.adelante.clicked.connect(self.desplazar_adelante)
        self.boton_guardar.clicked.connect(self.guardar_senal)
    
    def asignar_Controlador(self,controlador):
        '''
        Se asigna como coordinador a la ventana controlador
        '''
        self.__coordinador=controlador
        
    def cargar_senal(self):
        '''
        Permite cargar la senal desde una ventana emergente de explorador de archivos
        '''
        archivo_cargado, _ = QFileDialog.getOpenFileName(self, "Abrir señal","","Todos los archivos (*);;Archivos mat (*.mat)*")
        if archivo_cargado != "":
            data = sio.loadmat(archivo_cargado) #carga el archivo
            data = data["data"] # se le entrega su key para acceder
            sensores,puntos,ensayos=data.shape #vuelve continuos los datos
            senal_continua=np.reshape(data,(sensores,puntos*ensayos),order="F")
            self.__coordinador.recibirDatosSenal(senal_continua) # el coordinador recibe los datos de la senal
            self.__x_min=0
            self.__x_max=5000
            #grafica utilizando el controlador
            self.__sc.graficar_gatos(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max))

    def guardar_senal(self):
        '''
        Guarda la senal filrada 
        '''
        
        file,_=QFileDialog.getSaveFileName(self,"guardar senal"," ","Archivos mat (*.mat)")
        data_final=self.filtro()
        dic={'data':data_final}
        sio.savemat(file, dic )
