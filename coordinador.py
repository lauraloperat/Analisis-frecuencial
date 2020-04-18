"""
Juan Pablo Vasco y Laura Lopera 
"""
from Modelo import Biosenal
from interfaz import InterfazGrafico
import sys
from PyQt5.QtWidgets import QApplication

class Principal(object):
    def __init__(self):        
        self.__app=QApplication(sys.argv)
        self.__mi_vista=InterfazGrafico()
        self.__mi_biosenal=Biosenal()
        self.__mi_controlador=Coordinador(self.__mi_vista,self.__mi_biosenal)
        self.__mi_vista.asignar_Controlador(self.__mi_controlador)
    def main(self):
        self.__mi_vista.show()
        sys.exit(self.__app.exec_())
    
class Coordinador(object):
    def __init__(self,vista,biosenal):
        self.__mi_vista=vista
        self.__mi_biosenal=biosenal
    def recibirDatosSenal(self,data):
        self.__mi_biosenal.asignarDatos(data)
#        print(data.shape)
    def devolverDatosSenal(self,x_min,x_max):
        return self.__mi_biosenal.devolver_segmento(x_min,x_max)
    def escalarSenal(self,x_min,x_max,escala):
        return self.__mi_biosenal.escalar_senal(x_min,x_max,escala)
    def graficar_canal(self,canal):
        return self.graficar_canal(canal)
    def filtrar(self, senal, tipo_umbral, umbral, ponderado):
        return self.__mi_biosenal.filtrar(senal, tipo_umbral, umbral, ponderado)
p=Principal()
p.main()
