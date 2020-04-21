import sys
import numpy as np
# Qfiledialog es una ventana para abrir yu gfuardar archivos
# Qvbox es un organizador de widget en la ventana, este en particular los apila en vertcal
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QFileDialog, QMessageBox
from PyQt5 import QtCore, QtWidgets

from matplotlib.figure import Figure
from PyQt5.QtGui import QIntValidator

from PyQt5.uic import loadUi

import scipy.signal as signal
from chronux.mtspectrumc import mtspectrumc
from IPython import get_ipython
# import pwyt

# contenido para graficos de matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from csv import reader as reader_csv
import matplotlib.pyplot as plt

import scipy.io as sio
from modelo import Biosenal


# clase con el lienzo (canvas=lienzo) para mostrar en la interfaz los graficos matplotlib, el canvas mete la grafica dentro de la interfaz
class MyGraphCanvas(FigureCanvas):
    # constructor
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # se crea un objeto figura
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        # el axes en donde va a estar mi grafico debe estar en mi figura
        self.axes = self.fig.add_subplot(111)

        # se inicializa la clase FigureCanvas con el objeto fig
        FigureCanvas.__init__(self, self.fig)

    def graficar_datos(self, datos, start, stop, fmuestreo):
        '''
        Permite graficar los datos de la senal
        '''

        self.axes.clear()  # se limpia la grafica anterior
        self.fig.clf()
        self.axes = self.fig.add_subplot(111)

        # Se grafica en un mismo plano varias senales

        step = 1 / fmuestreo

        time = np.arange(start, stop, step)

        for c in range(datos.shape[0]):
            self.axes.plot(time, datos[c, :] + c * 10)

        self.axes.axes.set_title("Señal cargada", fontsize=15)
        self.axes.set_xlabel("Tiempo [s]")
        self.axes.set_ylabel("Amplitud")
        self.axes.figure.canvas.draw()

    def graficar_frecuencia(self, f, Pxx, fmin, fmax, title):
        self.axes.clear()
        self.fig.clf()
        self.axes = self.fig.add_subplot(111)

        # self.axes.plot(f,Pxx)
        self.axes.plot(f[(f >= fmin) & (f <= fmax)], Pxx[(f >= fmin) & (f <= fmax)])
        # (f[(f >= 4) & (f <= 40)],Pxx[(f >=4) & (f <= 40)])
        self.axes.set_xlabel("Frecuencia [Hz]")
        self.axes.set_ylabel("Amplitud")
        self.axes.axes.set_title(title, fontsize=15)
        self.axes.figure.canvas.draw()

    def graficar_espectro(self, time, freqs, power, fmin, fmax):
        # primero se necesita limpiar la grafica anterior

        self.axes.clear()
        self.fig.clf()
        self.axes = self.fig.add_subplot(111)

        # ingresamos los datos a graficar
        scalogram = self.axes.contourf(time,
                                       freqs,
                                       power,
                                       100,  # Especificar 20 divisiones en las escalas de color
                                       extend='both')

        # ordenamos que dibuje
        self.axes.set_ylabel('frequency [Hz]')
        self.axes.set_xlabel('Time [s]')
        self.axes.axes.set_title("Análisis por Wavelet continuo", fontsize=15)
        self.cb = plt.colorbar(scalogram, ax=self.axes)
        self.axes.figure.canvas.draw()

    # def select_canal(self,senal,canal):
    #     '''
    #  Permite seleccionar el canal que ingrese el usuario y graficarlo
    #     '''

    #     if canal <= (len(senal)-1): #valida si el canal ingresado por el usuario existe

    #         self.axes.clear()
    #         if senal.ndim>1:
    #             self.axes.plot(senal[canal,:])
    #         else:
    #            self.axes.plot(senal)

    #         self.axes.set_xlabel("Tiempo")
    #         self.axes.set_ylabel("Amplitud")

    #         self.axes.figure.canvas.draw()
    #     else: #si el canal no existe, genera una ventana emergente
    #         msg=QMessageBox(self)
    #         msg.setIcon(QMessageBox.Information)
    #         msg.setText("Informacion")
    #         msg.setWindowTitle('Advertencia')
    #         msg.setInformativeText('Canal inexistente')
    #         msg.show()


# %%

class InterfazGrafico(QMainWindow):
    # se define esta clase para crear la interfaz grafica
    # def graficar_canal (self):
    #     '''
    #     Permite graficar el canal seleccionado por el usuario
    #     '''
    #     canal = int(self.campo_canal.text())
    #     self.__sc.select_canal(self.__coordinador.devolverDatosSenal(self.__x_min,self.__x_max),canal)

    #     # se activan botones relacionados con filtrar
    #     self.tipo_umbral.setEnabled(True)
    #     self.umbral.setEnabled(True)
    #     self.ponderacion.setEnabled(True)
    #     self.boton_graficarf.setEnabled(True)

    def deshabilitar_metodos(self):

        metodo = self.metodo.currentIndex()
        if metodo == 0:
            self.campo_duracion.setEnabled(False)
            self.campo_ancho.setEnabled(False)
            self.campo_p.setEnabled(False)
            self.segmentos.setEnabled(False)
            self.adelante_esp.setEnabled(False)
            self.atras_esp.setEnabled(False)
            self.campo_tamano.setEnabled(True)
            self.campo_solapamiento.setEnabled(True)
        if metodo == 1:
            self.campo_tamano.setEnabled(False)
            self.campo_solapamiento.setEnabled(False)
            self.adelante_esp.setEnabled(False)
            self.atras_esp.setEnabled(False)
            self.campo_duracion.setEnabled(True)
            self.campo_ancho.setEnabled(True)
            self.campo_p.setEnabled(True)
            self.segmentos.setEnabled(True)
        if metodo == 2:
            self.campo_duracion.setEnabled(False)
            self.campo_ancho.setEnabled(False)
            self.campo_p.setEnabled(False)
            self.segmentos.setEnabled(False)
            self.campo_tamano.setEnabled(False)
            self.campo_solapamiento.setEnabled(False)
            self.adelante_esp.setEnabled(False)
            self.atras_esp.setEnabled(False)

    def escalado(self):
        '''
        Muestra la grafica de las senales en el rango de muestras seleccionado por el usuario
        '''
        if self.lim_inf.text() == "" or self.lim_sup.text() == "":

            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setText("Informacion")
            msg.setWindowTitle('Advertencia')
            msg.setInformativeText('Faltan campos por llenar')
            msg.show()
        else:

            self.__lim_inf = int(self.lim_inf.text())
            self.__lim_sup = int(self.lim_sup.text())

            self.__x_max = self.__lim_sup * self.__fmuestreo
            self.__x_min = self.__lim_inf * self.__fmuestreo

            if (
                    self.__lim_inf >= self.__lim_sup):  # si el limite inferior es mayor al superior sale una ventana emergente de advertencia

                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setText("Informacion")
                msg.setWindowTitle('Advertencia')
                msg.setInformativeText('Rango invalido')
                msg.show()
            else:

                self.__sc.graficar_datos(self.__coordinador.devolverDatosSenal(self.__x_min, self.__x_max),
                                         self.__lim_inf, self.__lim_sup, self.__fmuestreo)

                # Se habilitan campos y botones
                self.atras_2.setEnabled(True)
                self.adelante.setEnabled(True)

    def desplazar_atras(self):
        '''
        Permite realizar el desplazamiento de las senales hacia atras
        '''
        # se re-definen los limite superior e inferior
        desplazamiento = int((self.__x_max - self.__x_min) * 0.05)

        self.__x_max = self.__x_max - desplazamiento
        self.__x_min = self.__x_min - desplazamiento
        self.__lim_inf = (self.__x_min) / self.__fmuestreo
        self.__lim_sup = (self.__x_max) / self.__fmuestreo

        self.__sc.graficar_datos(self.__coordinador.devolverDatosSenal(self.__x_min, self.__x_max), self.__lim_inf,
                                 self.__lim_sup, self.__fmuestreo)

    def desplazar_adelante(self):
        '''
        Permite realizar el desplazamiento de las senales hacia adelante
        '''
        # se re-definen los limite superior e inferior
        desplazamiento = int((self.__x_max - self.__x_min) * 0.05)
        self.__x_max = self.__x_max + desplazamiento
        self.__x_min = self.__x_min + desplazamiento
        self.__lim_inf = (self.__x_min) / self.__fmuestreo
        self.__lim_sup = (self.__x_max) / self.__fmuestreo

        self.__sc.graficar_datos(self.__coordinador.devolverDatosSenal(self.__x_min, self.__x_max), self.__lim_inf,
                                 self.__lim_sup, self.__fmuestreo)

    def desplazar_atras_frecuencia(self):
        '''
        Permite realizar el desplazamiento de las senales hacia atras
        '''
        # se re-definen los limite superior e inferior
        desplazamiento = int((self.__f_max - self.__f_min) * 0.05)
        self.__f_max = self.__f_max - desplazamiento
        self.__f_min = self.__f_min - desplazamiento

        return self.analisis_f(self.__f_min, self.__f_max)

    def desplazar_adelante_frecuencia(self):
        '''
        Permite realizar el desplazamiento de las senales hacia adelante
        '''
        # se re-definen los limite superior e inferior
        desplazamiento = int((self.__f_max - self.__f_min) * 0.05)
        self.__f_max = self.__f_max + desplazamiento
        self.__f_min = self.__f_min + desplazamiento

        return self.analisis_f(self.__f_min, self.__f_max)

    def inicializar_frec_interes(self):

        if self.f_min.text() == "" or self.f_max.text() == "":
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setText("Informacion")
            msg.setWindowTitle('Advertencia')
            msg.setInformativeText('Faltan campos por llenar')
            msg.show()
        else:
            self.__f_min = int(self.f_min.text())
            self.__f_max = int(self.f_max.text())

            if (
                    self.__f_min >= self.__f_max):  # si el limite inferior es mayor al superior sale una ventana emergente de advertencia

                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setText("Informacion")
                msg.setWindowTitle('Advertencia')
                msg.setInformativeText('Rango invalido')
                msg.show()
            else:

                return self.analisis_f(self.__f_min, self.__f_max)

    def analisis_f(self, fmin, fmax):

        key = self.lineEdit.text()
        data = self.data[key]
        self.__coordinador.recibirDatosSenal(data)
        x = self.__coordinador.devolverDatosSenal(self.__x_min, self.__x_max)[0]

        if self.nivel_DC.isChecked() == True:
            x = x - np.mean(x)

        tipo = self.metodo.currentIndex()
        fs = int(self.campo_frecuencia.text())

        if tipo == 0:
            if self.campo_tamano.text() == "" or self.campo_solapamiento.text() == "":
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setText("Informacion")
                msg.setWindowTitle('Advertencia')
                msg.setInformativeText('Faltan campos por llenar')
                msg.show()
            else:
                tamano = int(self.campo_tamano.text())
                solapamiento = int(self.campo_solapamiento.text())
                f, Pxx = signal.welch(x, fs, 'hamming', tamano, solapamiento, scaling='density');

                title = "Análisis por método de Welch"

                self.__sc1.graficar_frecuencia(f, Pxx, fmin, fmax, title)

        elif tipo == 1:

            self.graficar_key()

            self.__coordinador.recibirDatosSenal(data)
            x = self.__coordinador.devolverDatosSenal(self.__x_min, self.__x_max)[0]
            print("shape orig: ", x.shape)
            if self.nivel_DC.isChecked() == True:
                x = x - np.mean(x)

            if self.campo_duracion.text() == "" or self.campo_ancho.text() == "" or self.campo_p.text() == "" or self.segmentos.text() == "":
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setText("Informacion")
                msg.setWindowTitle('Advertencia')
                msg.setInformativeText('Faltan campos por llenar')
                msg.show()
            else:
                W = int(self.campo_duracion.text())
                T = int(self.campo_ancho.text())
                p = int(self.campo_p.text())
                N = int(self.segmentos.text())

                params = dict(fs=fs, fpass=[fmin, fmax], tapers=[W, T, p], trialave=1)

                primer_termino = x.shape[0] / N
                print("primero", primer_termino)
                primer_termino = int(np.ceil(primer_termino))
                print("primero int", primer_termino)
                shape_final = primer_termino * N
                print("Shape nuevo", shape_final)
                nuevo_x = np.zeros([shape_final])
                nuevo_x[0:x.shape[0]] = x
                print("shape final", nuevo_x.shape)
                data = np.reshape(nuevo_x, (primer_termino, N), order='F')

                # Calculate the spectral power of the data
                Pxx, f = mtspectrumc(data, params)

                title = "Análisis por método Multitaper"

                self.__sc1.graficar_frecuencia(f, Pxx, fmin, fmax, title)
        else:
            # en realidad solo necesito limites cuando tengo que extraerlos, pero si los
            # extraigo por fuera mi funcion de grafico puede leer los valores
            tiempo, freq, power = self.__coordinador.calcularWavelet(x, fmin, fmax, fs)

            self.__sc1.graficar_espectro(tiempo, freq, power, fmin, fmax)

        # Se habilitan campos y botones
        self.campo_tamano.setEnabled(False)
        self.campo_solapamiento.setEnabled(False)
        self.adelante_esp.setEnabled(True)
        self.atras_esp.setEnabled(True)

    def __init__(self):
        # inicializa la clase interfaz grafico
        super(InterfazGrafico, self).__init__()
        # se carga el diseno creadi
        loadUi('anadir_grafico2.ui', self)
        # se llama la rutina donde se configura la interfaz
        self.setup()
        # se muestra la interfaz
        self.show()

    def setup(self):
        # los layout permiten organizar widgets en un contenedor
        # se crea el primer espacio
        layout = QVBoxLayout()
        # se añade el organizador al campo grafico
        self.campo_grafico.setLayout(layout)
        # se crea un objeto para manejo de graficos
        self.__sc = MyGraphCanvas(self.campo_grafico, width=5, height=1, dpi=75)
        # se añade el campo de graficos
        layout.addWidget(self.__sc)

        # se crea el segundo espacio
        layout1 = QVBoxLayout()
        self.campo_grafico_2.setLayout(layout1)
        # se crea un objeto para manejo de graficos
        self.__sc1 = MyGraphCanvas(self.campo_grafico_2, width=5, height=4, dpi=75)
        # se añade el campo de grafico
        layout1.addWidget(self.__sc1)

        # se definen los botones y los campos
        self.lineEdit.setEnabled(False)
        self.campo_frecuencia.setEnabled(False)
        self.boton_graficar.setEnabled(False)
        self.lim_inf.setEnabled(False)
        self.lim_sup.setEnabled(False)
        self.escalar.setEnabled(False)
        self.atras_2.setEnabled(False)
        self.adelante.setEnabled(False)
        self.metodo.setEnabled(False)
        self.f_min.setEnabled(False)
        self.f_max.setEnabled(False)
        self.campo_tamano.setEnabled(False)
        self.campo_solapamiento.setEnabled(False)
        self.campo_duracion.setEnabled(False)
        self.campo_ancho.setEnabled(False)
        self.campo_p.setEnabled(False)
        self.segmentos.setEnabled(False)
        self.nivel_DC.setEnabled(False)
        self.analizar.setEnabled(False)
        self.adelante_esp.setEnabled(False)
        self.atras_esp.setEnabled(False)
        self.boton_cargar.clicked.connect(self.cargar_datos)
        self.disponibles.setReadOnly(True)
        self.boton_graficar.clicked.connect(self.graficar_key)
        self.metodo.activated.connect(self.deshabilitar_metodos)
        self.escalar.clicked.connect(self.escalado)
        #        self.escalar.clicked.connect(self.habilitar_desplazamiento)
        self.atras_2.clicked.connect(self.desplazar_atras)
        self.adelante.clicked.connect(self.desplazar_adelante)
        self.analizar.clicked.connect(self.inicializar_frec_interes)
        self.atras_esp.clicked.connect(self.desplazar_atras_frecuencia)
        self.adelante_esp.clicked.connect(self.desplazar_adelante_frecuencia)
        self.f_min.setValidator(QIntValidator(0, 100000000))
        self.f_max.setValidator(QIntValidator(0, 100000000))
        self.campo_tamano.setValidator(QIntValidator(0, 100000000))
        self.campo_solapamiento.setValidator(QIntValidator(0, 100000000))

    def asignar_Controlador(self, controlador):
        '''
        Se asigna como coordinador a la ventana controlador
        '''
        self.__coordinador = controlador

    def cargar_datos(self):
        '''
        Permite cargar la senal desde una ventana emergente de explorador de archivos
        '''
        archivo_cargado, _ = QFileDialog.getOpenFileName(self, "Abrir señal", "",
                                                         "Todos los archivos (*);;Archivos mat (*.mat)*")
        if archivo_cargado != "":
            self.data = sio.loadmat(archivo_cargado)  # carga el archivo

            keys = []

            for key, value in self.data.items():
                keys.append(key)
            keys = keys[3:]

            keys_str = ""
            keys_str = "\n".join(keys)
            self.disponibles.setPlainText(keys_str)

            # Se habilitan campos y botones
            self.lineEdit.setEnabled(True)
            self.campo_frecuencia.setEnabled(True)
            self.boton_graficar.setEnabled(True)

    def graficar_key(self):

        if self.lineEdit.text() == "" or self.campo_frecuencia.text() == "":
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setText("Informacion")
            msg.setWindowTitle('Advertencia')
            msg.setInformativeText('Faltan campos por llenar')
            msg.show()
        else:
            key = self.lineEdit.text()
            fmuestreo = int(self.campo_frecuencia.text())
            data = self.data[key]  # se le entrega su key para acceder
            self.__x_min = 0
            self.__x_max = data.shape[1]
            self.__fmuestreo = fmuestreo
            start = 0
            stop = data.shape[1] / fmuestreo

            if len(data.shape) == 3:

                sensores, puntos, ensayos = data.shape  # vuelve continuos los datos
                senal_continua = np.reshape(data, (sensores, puntos * ensayos), order="F")
                self.__coordinador.recibirDatosSenal(senal_continua)  # el coordinador recibe los datos de la senal
                # grafica utilizando el controlador
                self.__sc.graficar_datos(self.__coordinador.devolverDatosSenal(self.__x_min, self.__x_max), start, stop,
                                         fmuestreo)
            else:

                senal_continua = data
                self.__coordinador.recibirDatosSenal(senal_continua)  # el coordinador recibe los datos de la senal
                # grafica utilizando el controlador
                self.__sc.graficar_datos(self.__coordinador.devolverDatosSenal(self.__x_min, self.__x_max), start, stop,
                                         fmuestreo)

            # Se habilitan campos y botones
            self.lim_inf.setEnabled(True)
            self.lim_sup.setEnabled(True)
            self.escalar.setEnabled(True)
            self.metodo.setEnabled(True)
            self.f_min.setEnabled(True)
            self.f_max.setEnabled(True)
            self.nivel_DC.setEnabled(True)
            self.campo_tamano.setEnabled(True)
            self.campo_solapamiento.setEnabled(True)
            self.analizar.setEnabled(True)

#
#    def guardar_senal(self):
#        '''
#        Guarda la senal filrada
#        '''
#
#        file,_=QFileDialog.getSaveFileName(self,"guardar senal"," ","Archivos mat (*.mat)")
#        data_final=self.filtro()
#        dic={'data':data_final}
#        sio.savemat(file, dic )
