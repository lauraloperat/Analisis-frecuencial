"" "
Juan Pablo Vasco y Laura Lopera 
"" "
de  Modelo  import  Biosenal
desde  interfaz  import  InterfazGrafico
 sys de importación
de  PyQt5 . QtWidgets  importa  QApplication

Clase  Principal ( objeto ):
    def  __init__ ( self ):        
        auto . __app = QApplication ( sys . argv )
        auto . __mi_vista = InterfazGrafico ()
        auto . __mi_biosenal = Biosenal ()
        auto . __mi_controlador = Coordinador ( self . __mi_vista , self . __mi_biosenal )
        auto . __mi_vista . asignar_Controlador ( self . __mi_controlador )
    def  main ( self ):
        auto . __mi_vista . show ()
        sys . salir ( self . __app . exec_ ())
    
 Coordinador de clase ( objeto ):
    def  __init__ ( self , vista , biosenal ):
        auto . __mi_vista = vista
        auto . __mi_biosenal = biosenal
    def  recibirDatosSenal ( self , data ):
        auto . __mi_biosenal . asignarDatos ( datos )
# print (data.shape)
    def  devolverDatosSenal ( self , x_min , x_max ):
        volver a  sí mismo . __mi_biosenal . devolver_segmento ( x_min , x_max )
    def  escalarSenal ( self , x_min , x_max , escala ):
        volver a  sí mismo . __mi_biosenal . escalar_senal ( x_min , x_max , escala )
    def  graficar_canal ( auto , canal ):
        volver a  sí mismo . graficar_canal ( canal )
     filtro de def ( self , senal , tipo_umbral , umbral , ponderado ):
        volver a  sí mismo . __mi_biosenal . filtrar ( senal , tipo_umbral , umbral , ponderado )
p = Principal ()
p . main ()
