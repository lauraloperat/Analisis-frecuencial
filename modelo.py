"" "
Juan Pablo Vasco y Laura Lopera
"" "
importar  numpy  como  np
importación  scipy . io  como  sio
importar  matplotlib . pyplot  como  plt


clase  Biosenal ( objeto ):
    def  __init__ ( self , data = None ):
        si  no  datos  ==  Ninguno :
            auto . asignarDatos ( datos )
        más :
            auto . __data = np . una matriz ([])
            auto . __canales = 0
            auto . __puntos = 0
    def  asignarDatos ( auto , datos ):
        auto . __data = datos
        auto . __canales = datos . forma [ 0 ]
        auto . __puntos = datos . forma [ 1 ]
    #necesitamos hacer operaciones básicas sobre las senal, ampliarla, disminuirla, trasladarla variable etc.
    def  devolver_segmento ( self , x_min , x_max ):
        '' '
        Parámetros
        ----------
        x_min: valor minimo del rango.
        x_max: valor maximo del rango.
        Devoluciones
        -------
        Devuelve los valores de la señal que esten dentro del rango descrito.
        '' '
        si  x_min > = x_max :
            return  None  #si el valor minimo del rango es mayor o igual al maximo, no retorna nada
        #cojo los valores que necesito en la biosenal
        volver a  sí mismo . __data [:, x_min : x_max ]
    
     filtro de def ( self , vector , tipo_umbral , umbral , ponderado ):
        '' '
        Parámetros
        ----------
        vector: corresponde a todos los valores de la señal del canal seleccionado.
        tipo_umbral: forma de filtrado seleccionado por el usuario (duro, blando).
        umbral: tipo de umbral seleccionado por el usuario (universal, minimax, seguro).
        ponderado: forma de aplicación del peso seleccionado por el usuario (uno, SLN, MLN).
        Devoluciones
        -------
        filtrada_reconstruida: señal final filtrada.
        '' '
        
        nivel_final = np . floor ( np . log2 ( vector . forma [ 0 ] / 2 ) - 1 ) #se establece cuantas veces se hace la descomposicion
        
        t_haar  =  self . descomponer ( vector , 1 , nivel_final , []) #se llama a la función descomponer
        
        thr  =  auto . umbral ( umbral , t_haar ) #se llama a la funcion umbral
        
        pesos  =  auto . ponderado ( ponderado , t_haar ) #se llama a la funcion ponderado
                     
        filtrada  =  auto . tipo_umbral ( tipo_umbral , t_haar , pesos , thr ) #se llama la funcion tipo umbral
        
        filtrada_reconstruida  =  self . rebuild ( filtrada , 1 , nivel_final , []) #se llama a la función que recompone la señal
        
        volver  filtrada_reconstruida
    
    
    def  descompose ( self , x , nivel_actual , nivel_final , t_haar ):
        '' '
        Parámetros
        ----------
        x: correspondencia al vector que corresponde a la señal en el canal especificado.
        nivel_actual: funciona como un contador.
        nivel_final: corresponde a cuantas veces se debe hacer la descomposicion.
        t_haar: es un vector que al llamar a la función almacena los valores de la transformación Haar.
        Devoluciones
        -------
        Devuelve el vector que contiene los valores de la transformación Haar.
        '' '
    
        s  =  np . array ([( 1 / np . sqrt ( 2 )), ( 1 / np . sqrt ( 2 ))]) # definición del valor de escala
        w  =  np . array ([( - 1 / np . sqrt ( 2 )), ( 1 / np . sqrt ( 2 ))])    # definición del valor de wavelet          
        
        if ( nivel_actual  <=  nivel_final ):
            if ( x . forma [ 0 ] % 2 ) ! =  0 :
                x  =  np . agregar ( x , 0 )
        #mientras nivel actual sea menor o igual a nivel final, se hace la transformación Haar
        scale_x  =  np . convolucionar ( x , s , 'completo' )
        aprox_x  =  scale_x [ 1 :: 2 ] #se submuestrea

        wavelet_x  =  np . convolucionar ( x , w , 'completo' )
        detail_x  =  wavelet_x [ 1 :: 2 ] #se submuestrea

        t_haar . agregar ( detalle_x )

        if ( nivel_actual  <  nivel_final ):
            volver a  sí mismo . descomponer ( aprox_x , nivel_actual + 1 , nivel_final , t_haar )
        #mientras nivel actual sea menor a nivel final, la función se llama a si misma
        t_haar . agregar ( aprox_x )
        
        volver  t_haar
        
    def  umbral ( self , umbral , vector ):
        '' '
        Devuelve el valor del umbral, segun lo seleccionado por el usuario (universal, minimax, sure)
        '' '
        Num_samples = 0  #actua como un contador
        para  i  en  rango ( len ( vector )):
            Num_samples  =  Num_samples  +  len ( vector [ i ]) #se saca el número de muestras identificadas del detalle a analizar
        
        si  umbral  ==  0 : #umbral universal
            thr  =  np . sqrt ( 2 * ( np . log ( Num_samples )))
                    
        if  umbral  ==  1 : #umbral minimax
            thr  =  0.3936  +  0.1829 * (( np . log ( Num_samples )) / np . log ( 2 ))
                    
        if  umbral  ==  2 : #umbral seguro
            
            sx2 = []
            riesgo = []
            para  i  en  rango ( len ( vector )):
                sx2  =  np . agregar ( sx2 , vector [ i ])
                
            sx2  =  np . potencia ( np . sort ( np . abs ( sx2 )), 2 )
            #se implementa la ecuacion de sure
            de riesgo  = ( Num_samples - ( 2 * np . arange ( 1 , Num_samples  +  1 )) + ( np . cumSum ( sx2 [ 0 : Num_samples ])) +  np . multiplican ( np . arange ( Num_samples , 0 , - 1 ), sx2 [ 0 : Num_samples ])) / Num_samples
            #Se selecciona el mejor valor como el mínimo valor del vector anterior
            mejor  =  np . min ( riesgo )
            #Se redondea a un entero
            redondeo  =  int ( np . round ( mejor ))
            #Se toma la raíz cuadrada del valor en la posición "mejor" 
            thr  =  np . sqrt ( sx2 [ redondeo ])
        volver  thr
    
    def  ponderado ( self , ponderado , vector ):
        '' '
        Devuelve los pesos de los detalles según el tipo de ponderación elegido (uno, SLN, MLN)
        '' '
        
        pesos  =  np . ceros ( len ( vector ))
        detalle1  =  vector [ 0 ]
        
        si  ponderado  ==  0 : #ponderado uno
            pesos [:] =  1
            
        si  ponderado  ==  1 : #ponderado SLN
            peso_detalle1  = ( np . mediana ( np . absoluto ( detalle1 ))) / 0.6745
            pesos [:] =  peso_detail1  #todos los detalles se multiplican por el peso del detalle 1
        
        si  ponderado  ==  2 : #ponderado MLN
            para  i  en  rango ( len ( vector )):
                peso_detail_x  = ( np . mediana ( np . absoluto ( vector [ i ]))) / 0.6745
                pesos [ i ] =  peso_detail_x  #se multiplica cada detalle por su peso correspondiente
        devolución de  pesos
    
    def  tipo_umbral ( self , tipo_umbral , vector , pesos , thr ):
        '' '
      Devuelve el vector de los detalles y la aproximación seleccionada del tipo de filtrado seleccionado (duro, suave)
        '' '
        
        umbrales_definitivos  =  pesos * thr
        
        si  tipo_umbral  ==  0 : #filtrado duro
            
            para  i  in  range ( len ( vector ) - 1 ): #para recorrer el vector de transformada Haar
                para  j  en  rango ( len ( vector [ i ])): #para recorrer cada posición de cada detalle
                    si  np . abs ( vector [ i ] [ j ]) <  umbrales_definitivos [ i ]:
                        vector [ i ] [ j ] =  0  #si el valor del detalle en esa posición es menor que el umbral, se hace cero
                    más :
                        pase  #si el valor del detalle en esta posición es mayor al umbral, permanece igual
            
        si  tipo_umbral  ==  1 : #filtrado suave
            
            para  i  in  range ( len ( vector ) - 1 ): #para recorrer el vector de transformada Haar
                para  j  en  rango ( len ( vector [ i ])): #para recorrer cada posición de cada detalle
                    si  np . abs ( vector [ i ] [ j ]) <  umbrales_definitivos [ i ]:
                        vector [ i ] [ j ] =  0  #si el valor del detalle en esa posición es menor que el umbral, se hace cero
                    más : #si el valor del detalle en esta posición es mayor al umbral, se ejecuta la ecuación
                        sgn  =  np . signo ( vector [ i ] [ j ])
                        resta  =  np . abs ( vector [ i ] [ j ]) -  umbrales_definitivos [ i ]
                        vector [ i ] [ j ] =  sgn * resta
         vector de retorno
        
    def  rebuild ( self , t_haar , nivel_actual , nivel_final , x ):
        '' '
        Parámetros
        ----------
        t_haar: vector de transformación Haar, entregado por descomponer.
        x: correspondencia al vector que corresponde a la señal en el canal especificado.
        nivel_actual: funciona como un contador.
        nivel_final: corresponde a cuantas veces se debe hacer la reconstrucción.
        Devoluciones
        -------
        Devuelve el vector de la señal reconstruida.
        '' '
    
        s_inv  =  np . array ([( 1 / np . sqrt ( 2 )), ( 1 / np . sqrt ( 2 ))]) # definición del valor de escala
        w_inv  =  np . array ([( 1 / np . sqrt ( 2 )), ( - 1 / np . sqrt ( 2 ))]) # definición del valor de wavelet
             
        tamaño  =  len ( t_haar )
        detalle  =  t_haar [ tamaño  -  1  -  nivel_actual ] #para recorrer todas las posiciones correspondientes a los detalles
        
        if ( nivel_actual  <=  nivel_final ):
            if ( nivel_actual == 1 ):
                npoints_aprox  =  len ( t_haar [ len ( t_haar ) - 1 ])
                aprox_inv  =  np . ceros ( 2 * npoints_aprox )
                aprox_inv [ 0 :: 2 ] =  t_haar [ tamaño - 1 ] # se sobremuestrea          
        
            más :
                if ( len ( x ) >  len ( detalle )):
                    x  =  x [ 0 : len ( detalle )]
                npoints_aprox  =  len ( x )
                aprox_inv  =  np . ceros ( 2 * npoints_aprox )
                aprox_inv [ 0 :: 2 ] =  x  #se sobremuestrea
            
            aprox_x  =  np . convolve ( aprox_inv , s_inv , 'full' ) #se realiza la convolucion con scale inverso
            
            detail_inv  =  np . ceros ( 2 * npoints_aprox )
            detail_inv [ 0 :: 2 ] =  detalle
            
            detail_x  =  np . convolve ( detail_inv , w_inv , 'full' ) #se realiza la convolucion con wavelet inverso
            
            x  =  aprox_x  +  detalle_x

            volver a  sí mismo . rebuild ( t_haar , nivel_actual + 1 , nivel_final , x ) #la función se llama a si misma y se aumenta el nivel actual (contador)
        
        volver  x
