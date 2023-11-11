

# -*- coding: utf-8 -*-
""" -------------------------------------------------------------------------------------------------------------------------------------
    ------------------------------------------------ Grupo de investigación GEPAR -------------------------------------------------------
    -------------------------------------------------- Universidad de Antioquia ---------------------------------------------------------
    -------------- Autores: Luis Fernando Torres (Interfaz gráfica y documentación) -------
    -------------------------------------------------------------------------------------------------------------------------------------
    --------------- Project Name: Clasificación de esquejes mediante técnicas de visión artificial --------------------------------------
    -------------------------------------------------------------------------------------------------------------------------------------
    ----------Description: En este proyecto se pretende implementar un algoritmo que permita clasificar los esquejes que son ------------
                           ingresados a la máquina clasificadora, de modo que a cada uno de ellos se les asigne una clasificación -------
                           para ser separados a través del sistema neumático. -----------------------------------------------------------
    ------------------------------------------------------------------------------------------------------------------------------------- """
                       
                                                                                                                
""" -----------------------------------------------------------------------------------------------------------------------------------------
    -------------------------------- 1. Importación de las librerí­as necesarias para el programa --------------------------------------------
    ----------------------------------------------------------------------------------------------------------------------------------------- """
                                                                                                                                            
from tkinter import ttk                                                        # Librerí­a para poder usar el combobox
import cv2                                                          # Librerí­a para el manejo de imagenes en general
import glob                                                         # Librerí­a para hallar las rutas de las imagenes al elegir lectura desde directorio
import numpy as np                                                  # Librerí­a de funciones matemáticas
#import tkFileDialog                                                 # Librerí­a para abrir el explorador y buscar la ruta deseada
import tkinter as tk                                                # Librerí­a para generar los elementos de la interfaz gráfica
#import serial.tools.list_ports                                      # Librerí­a para utilizar información asociada a los puertos seriales 
from math import factorial                                          # Librerí­a utilizada en el filtro de savitzky_golay
from collections import deque                                       # Librerí­a para utilizar el tipo de dato estructurado que controla el sistema neumático
from PIL import Image, ImageTk                                      # Librerí­a para mostrar imagenes en la interfaz gráfica
#from tkMessageBox import showerror,askquestion,showinfo             # Librerí­a para generar ventanas emergentes 
from tkinter import filedialog                                      # Libreria para corregir tkfiledialog
from tkinter import messagebox
import time                                                         # Libreria para inicializar timers para espera
import os           
import tkinter.simpledialog as sd                                   #Librería para mostrar dialogos 
import json                                                         # Librería para crear el archivo donde se va a guardar los tipos de estquejes                           

import socket                                                       # Librería para comunicación con PLC
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

""" ----------------------------------------------------------------------------------------------------------------------------------------
    -------------------------------------------------- 2. Implementación de funciones ------------------------------------------------------
    ---------------------------------------------------------------------------------------------------------------------------------------- """

"""---------------------------------------------- a. Elección del directorio para lectura ---------------------------------------------------"""
def ask_path_directorio():
    """ Esta función es una función sin parámetros de entrada la cual muestra en pantalla una interfaz de explorador de archivos para 
        seleccionar el directorio que contiene las imágenes que serán procesadas, obtiene la ruta de la carpeta y valida que en dicha 
        carpeta existan imágenes con formato TIFF. Esta función, adicionalmente, genera un label que muestra la ruta elegida en la interfaz.
        No se retorna ninguna variable."""
    
    """------------------------------------------------- a.1. Definición de variables --------------------------------------------------------"""
    global ruta_lectura                                                # Variable donde se almacena la ruta del directorio donde estan las imagenes a procesar
    global img_count                                                   # Variable que cuenta la cantidad de imagenes procesadas
    global Text_ruta                                                   # Widget de texto donde se muestra la ruta del directorio elegido
    global num_esqueje_analizado                                       # Variable que almacena la posición de la ultima imagen que se analizó en caso de una suspensión de la ejecución
    global rutas_esquejes                                              # Variable tipo lista que almacena todas las rutas de las imagenes .TIFF del directorio seleccionado           
    global Cantidad_imagenes                                           # Variable que almacena la cantidad de imagenes .TIFF que hay en el directorio seleccionado
    
    """----------------------------------------- a.2. Obtención de las rutas de las imágenes ------------------------------------------------"""
    ruta_lectura = filedialog.askdirectory()                         # Se abre el explorador de archivos para buscar el directorio en el ordenador y se captura dicha ruta
    rutas_esquejes = glob.glob(ruta_lectura + "/*.TIFF")               # Se genera la lista con todas las rutas de las imagenes .TIFF del directorio seleccionado
    Cantidad_imagenes = len(rutas_esquejes)                            # Se encuentra la longitud de la lista para saber cuántas imágenes hay en el directorio elegido
    num_esqueje_analizado = 0                                          # Se inicializa en 0 la posición de la última imagen analizada 
    img_count=0                                                        # Se inicializa en 0 el contador de las imagenes procesadas 
    
    """----------------------------------------------- a.3. Validación de la imágenes -------------------------------------------------------"""
    # Validación de la presencia de imágenes con formato TIFF en el directorio elegido
    if (Cantidad_imagenes == 0):
        messagebox.showerror("Mensaje de error","No se han encontrado imágenes con formato TIFF en el directorio seleccionado, por favor elija otro directorio.")
    else:
        # Widget de texto para mostrar la ruta de lectura de los esquejes
        Text_ruta = tk.Text(font = ("Calibri",10, "bold"), width = 59, height = 1, fg = '#000000', bg = "#9A9EAD")
        Text_ruta.place(x=460,y = 20)                                  # Se posiciona el Widget en las coordenadas dadas                 
        Text_ruta.insert("insert", ruta_lectura)                       # Se inserta el texto asociado a la ruta del directorio seleccionado
        Text_ruta.tag_configure("center", justify = 'center')          # Se configura el Widget para justificar el texto centrado
        Text_ruta.tag_add("center",1.0,"end")                          # Se agrega dicha justificación al Widget de texto 
        Text_ruta.config(state='disable')                              # Se inhabilita la edición del texto 

"""----------------------------------------------b. Inicio de la ejecución -------------------------------------------------------------------"""
def iniciar():
    """Esta función no tiene parámetros de entrada y es la encargada de dar inicio al procesamiento de las imágenes. Allí se identifica el método 
       de lectura que se eligió y el tipo de esquejes que se van a procesar y con base en esta información se da inicio al análisis de las imágenes. 
       Esta función se ejecuta como respuesta al botón “Iniciar”, y cada vez que se invoque cambia el estado del botón a “Detener” y asocia dicho botón 
       a la función detener(). No se retorna ninguna variable."""
       
    """---------------------------------------- b.1. Definición de variables -----------------------------------------------------------------"""
    global factor                                                   # Factor de conversión para pasar de cm a pixeles y viceversa
    global corto_cm                                                 # Longitud de un esqueje corto dada en cm, acorde a la clase elegida 
    global largo_cm                                                 # Longitud de un esqueje largo dada en cm, acorde a la clase elegida
    global Hoja_base_cm                                             # Longitud de un esqueje con hoja en base dada en cm, acorde a la clase elegida
    global flag_break                                               # Bandera que cuando vale 1 indica que se debe detener el procesamiento de las imágenes  
    global corto_pixeles                                            # Longitud de un esqueje corto convertida a pixeles
    global largo_pixeles                                            # Longitud de un esqueje largo convertida a pixeles
    global hojabase_pixeles                                         # Longitud de un esqueje con hoja en base convertida a pixeles
    
    proceso = combox.get()                                          # Se obtiene el tipo de esquejes elegido desde el combox
    largo, corto, hoja_base = get_params_by_name(proceso)  
    
    corto_cm = float(corto)
    largo_cm = float(largo)
    Hoja_base_cm = round(float(hoja_base),2)

    """-------------------------------------- b.2. Tipo de esquejes a clasificar --------------------------------------------------------------"""
    # Proceso para clasificar los esquejes de la clase Atlantis
   # if proceso == 'Atlantis':

        #corto_cm = 7.56                                             # Se asigna la longitud de un esqueje corto dada en cm, acorde a la clase Atlantis     
        #largo_cm = 8.99                                             # Se asigna la longitud de un esqueje largo dada en cm, acorde a la clase Atlantis
        #Hoja_base_cm = 1                                            # Se asigna la longitud de un esqueje con hoja en base dada en cm, acorde a la clase Atlantis
        
    # Proceso para clasificar los esquejes de la clase Baltica
    #elif proceso == 'Baltica':
        
        #corto_cm = 6.5                                              # Se asigna la longitud de un esqueje corto dada en cm, acorde a la clase Baltica     
        #largo_cm = 8.5                                              # Se asigna la longitud de un esqueje largo dada en cm, acorde a la clase Baltica
        #Hoja_base_cm = 1                                            # Se asigna la longitud de un esqueje con hoja en base dada en cm, acorde a la clase Baltica
    
    """ Si se desea agregar otro tipo de esquejes utilice otra sentencia elif indicando el nombre del tipo de esquejes 
        y la longitud de cada una de las clasificaciones.
        
        elif proceso == 'tipo de esqueje':
        
            corto_cm = umbral de longitud para esquejes cortos     
            largo_cm = umbral de longitud para esquejes largos                                              
            Hoja_base_cm = umbral de longitud para hoja en base"""

    """--------------------------------------- b.3. Asignación de variables ---------------------------------------------------------------------"""
    factor = 11.5 / 960                                             # Se inicializa el factor de conversión
    flag_break = 0                                                  # Se inicializa la bandera en 0               

    # Se realiza la tansformación a pixeles de los valores ingresados en centí­metros, usando el factor de conversión
    corto_pixeles = int(corto_cm / factor)
    largo_pixeles = int(largo_cm / factor)
    hojabase_pixeles = int(Hoja_base_cm / factor) 
    
    """---------------------------------- b.4. Cambio de estado botón iniciar --------------------------------------------------------------------"""
    label_imagenDefecto1.destroy()                                  # Se elimina la imagen en blanco que inicialmente estaba en la interfaz (a la izquierda)
    label_imagenDefecto2.config(bg = 'black')                       # Se cambia a negro el color de la imagen de fondo del lado derecho ya que la imagen procesada no es tan grande
    button_iniciar_detener.config(text='Detener',command=detener)   # Se reconfigura el botón para que se pueda detener la ejecución con él  

    """---------------------------------- b.5. Validación al modo de lectura ----------------------------------------------------------------------"""
    # Acorde al estado del radiobutton se  ejecuta la función asociado a lectura desde directorio o desde la cámara
   
    
   
    if (state_radiobutton.get() == 1):
        ejecucion_directorio()                                      # Se ejecuta la función asociada a la lectura de las imágenes desde un directorio            
        
    elif (state_radiobutton.get() == 2):                            # Se ejecuta la función asociada a la lectura de las imágenes desde la cámara
        conectar_PLC()
        ejecucion_camera()  
    else:                                                           # Si no se detecta el modo de lectura aparece este error
        messagebox.showerror("Mensaje de error","No se ha detectado el modo de lectura, por favor elí­jalo.")                                            
        detener()

"""-------------------------------------------- c. Detención de la ejecución ---------------------------------------------------------------------"""
def detener():
    """Esta función no posee parámetros de entrada y se ejecuta al dar clic sobre el botón “Detener”. Allí se cambia el valor de una variable tipo bandera 
       de la cual depende la detención del proceso de ejecución así que se detendrá el ciclo, independientemente del tipo de lectura. Adicionalmente, cada 
       vez que se invoque esta función cambia el estado del botón a “Iniciar” y asocia dicho botón a la función iniciar(). No se retorna ninguna variable."""
       
    global flag_break                                               # Bandera que cuando vale 1 indica que se debe detener el procesamiento de las imágenes  
    flag_break = 1                                                  # Se asigna el valor de 1 para detener el procesamiento de las imágenes
    button_iniciar_detener.config(text='Iniciar',command=iniciar)   # Se reconfigura el botón para que se pueda iniciar/reanudar la ejecución con él  

"""-------------------------------------- d. Actualización de la interfaz gráfica ------------------------------------------------------------------"""
def actualizar_interfaz(original_image,processed_image):
    """Esta función tiene como parámetros de entrada la imagen original del esqueje y la imagen procesada de éste. Cada vez que se ejecuta esta función se 
       actualizan las imágenes del esqueje que se muestra en la interfaz. Adicionalmente en los text edit se actualiza la información obtenida de la 
       clasificación y longitud del esqueje analizado y el número de esquejes analizados hasta el momento. No se retorna ninguna variable."""

    """---------------------- d.1. Actualización de la infomación de los Widgets de texto  ---------------------------------------------------------"""
    Text_longitud.delete('1.0', tk.END)                            # Se elimina el texto que habí­a anteriormente en el Widget
    Text_longitud.insert("insert", str(round(longitud_cm,2)))      # Se inserta en el Widget el texto asociado a la longitud del esqueje redondeado a 2 cifras decimales
    Text_longitud.tag_configure("center", justify = 'center')      # Se configura el Widget para justificar el texto centrado 
    Text_longitud.tag_add("center",1.0,"end")                      # Se agrega dicha justificación al Widget 
    
    Text_cantidad.delete('1.0', tk.END)                            # Se elimina el texto que habí­a anteriormente en el Label 
    Text_cantidad.insert("insert",str(num_esqueje_analizado+1))    # Se inserta en el Widget el texto asociado a la cantidad de imágenes procesadas
    Text_cantidad.tag_configure("center", justify = 'center')      # Se configura el Widget para justificar el texto centrado
    Text_cantidad.tag_add("center",1.0,"end")                      # Se agrega dicha justificación al Widget 
    
    Text_clasificacion.delete('1.0', tk.END)                       # Se elimina el texto que habí­a anteriormente en el Label  
    Text_clasificacion.insert("insert",clase)                      # Se inserta en el Widget el texto asociado a la clasificación que se encontró del esqueje
    Text_clasificacion.tag_configure("center",justify='center')    # Se configura el Widget para justificar el texto centrado
    Text_clasificacion.tag_add("center",1.0,"end")                 # Se agrega dicha justificación al Widget 
    
    """--------------------------------- d.2. Se muestran las imagenes en la interfaz -------------------------------------------------------------"""
    # Se coloca la imagen original en una label y se modifica la posición y el tamaíño.
    imagen_original = original_image 
    imagen_original = cv2.resize(imagen_original, (560,490))                            
    imagenCV2 = cv2.cvtColor(imagen_original, cv2.COLOR_BGR2RGBA)
    imagen_original = imagenCV2
    imagen_original = Image.fromarray(imagen_original)                                  
    imgtk = ImageTk.PhotoImage(image=imagen_original)                                  
     
    label_imag_ORIGINAL = tk.Label(MainWindow, image=imgtk,width = 550, height = 480 )
    label_imag_ORIGINAL.place(x=45,y=42)
    label_imag_ORIGINAL.imgtk = imgtk
    label_imag_ORIGINAL.configure(image=imgtk)
    
    # Se coloca la imagen procesada en una label y se modifica la posición y el tamaño.
    imagen_procesada = processed_image 
    imagen_procesada = cv2.resize(imagen_procesada, (500,220))                          
    imagenCV2_2 = cv2.cvtColor(imagen_procesada, cv2.COLOR_BGR2RGBA)
    imagen_procesada = imagenCV2_2
    imagen_procesada = Image.fromarray(imagen_procesada)                                
    imgtk = ImageTk.PhotoImage(image=imagen_procesada)                                  
    
    label_imag_PROCESADA = tk.Label(MainWindow, image=imgtk,width = 480, height = 200 )
    label_imag_PROCESADA.place(x=690,y=167)
    label_imag_PROCESADA.imgtk = imgtk
    label_imag_PROCESADA.configure(image=imgtk)
    MainWindow.update()

"""----------------------------------- e. Elección del directorio para el guardado --------------------------------------------------------------------"""
def ask_path_camera():
    """Esta función es una función sin parámetros de entrada la cual muestra en pantalla una interfaz de diálogo, donde si el usuario desea guardar 
       la imagenes capturadas se abre un explorador de archivos para seleccionar la ruta donde se desea guardar las imágenes que serán procesadas, 
       adicionalmente, genera un label que muestra la ruta elegida en la interfaz. No se retorna ninguna variable."""
    
    """-------------------------------------- e.1. Definición de variables  ---------------------------------------------------------------------------"""
    global ruta_almacenamiento                                         # Variable donde se almacena la ruta del directorio donde estan las imagenes a procesar                               
    global almacenamiento                                              # Variable que indica si desea guardar las imágenes capturadas  
    
    # Ventana emergente donde se pregunta al usuario si se desea guardar las imágens capturadas
    almacenamiento = messagebox.askquestion("Petición de almacenamiento", "¿Desea almacenar las imágenes capturadas?")
    
    """-------------------------- e.2. Validación para guardar la imágenes capturadas ----------------------------------------------------------------------"""    
    if (almacenamiento == 'yes'):
        ruta_almacenamiento  = filedialog.askdirectory(initialdir="C:/User/Imagenes")               # Se abre el explorador de archivos para buscar el directorio en el ordenador y se captura dicha ruta
        # Widget de texto para mostrar la ruta de lectura de los esquejes
        Text_ruta = tk.Text(font = ("Calibri",10, "bold"), width = 59, height = 1, fg = '#000000', bg = "#9A9EAD")
        Text_ruta.place(x=460,y = 20)                                  # Se posiciona el Widget en las coordenadas dadas                 
        Text_ruta.insert("insert", ruta_almacenamiento)                # Se inserta el texto asociado a la ruta del directorio seleccionado
        Text_ruta.tag_configure("center", justify = 'center')          # Se configura el Widget para justificar el texto centrado
        Text_ruta.tag_add("center",1.0,"end")                          # Se agrega dicha justificación al Widget de texto 
        Text_ruta.config(state='disable')                              # Se inhabilita la edición del texto
        
"""----------------------------------- f. Extracción de información del esqueje ----------------------------------------------------------------------------"""
def encontrar_medidas(imagen):
    """
    Función para encontrar el area foliar y tallo promedio de un esqueje
    """
    gray = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    w=gray.shape[1] #Ancho de la imagen
    h=gray.shape[0] # Alto de la imagen
    imgen = gray[0:h,0:w//3] # Particiono el tallo de la imagen
    imgen_Area = gray[0:h,w//3:] # Particiono el tallo de la imagen

    ai=0 # aera foliar
    sup=0 # Parte superior de la imagen
    inf=0 # parte inferior de la imagen
    a1_img = imgen_Area[h//2:,:]
    a2_img = imgen_Area[0:h//2,:]

    Vei=[] # Vector para encontrar estadisticas 

    for i in range(w//3):

        u=np.count_nonzero(gray[0:h,i])
        #ei += u # Recorro cada columna y encuentro lo que no son zeros
        #print(u)
        Vei.append(u)
        #print(ei)

    for i in range(2*w//3):

        u1=np.count_nonzero(a1_img[0:h//2,i])
        u2=np.count_nonzero(a2_img[0:h//2,i])
        sup += u1 
        inf += u2
        

    factor = 11.5 / 960 
    if sup>inf:
        ai= sup*factor**2
    else:
        ai=inf*factor**2

    return  np.mean(Vei)*factor,ai

def segmentacion(original_image):
    """Esta función es una función que tiene como parámetro de entrada la imagen original, es el core de SOCAES, pues aquí es donde se realiza la extracción de toda la información acerca del esqueje 
       que está siendo analizado. Allí se realiza un preprocesado de la imagen, operaciones de morfología y se utiliza un filtro en la detección de la hoja en base. Esta función retorna la imagen 
       procesada e información asociada al esqueje como longitud en centímetros y clasificación.""" 
    
    """---------------------------- f.1. Definición e inicialización de variable ----------------------------------------------------------------------------"""
    global clase                                                                                           # Variable que almacena la clase
    #global tallo_promedio
    #global area_foliar                                                                                        
    
    clasificacion='0'                                                                                      # Variable donde se almacena la clasificación del esqueje
    clase='nada'                                                                                           # Variable donde se almacena la clase del esqueje
   
    """---------------------- f.2. Preprocesado y extracción de contornos de la imagen -----------------------------------------------------------------------"""
    ret,imagen_binarizada = cv2.threshold(original_image[:,:,0],50,255,cv2.THRESH_BINARY_INV)              # Se pasa la imagen a escala de grises y se realiza una binarización invertida con un umbral de 50
    contours, hierarchy = cv2.findContours(imagen_binarizada,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)     # Se encuetra los contornos de la imagen binarizada
    contours = sorted(contours, key=cv2.contourArea,reverse=True)                                          # Se ordenan los contornos de mayor area a menor area  
    
    contorno_esqueje = contours[0]                                                                         # Se toma el primer contorno que corresponde al de mayor area (contorno del esqueje)    
    imagen_binarizada[...] = 0                                                                             # Se lleva todos los valores de la imgaen a   
    cv2.drawContours(imagen_binarizada, [contorno_esqueje], 0, 255, cv2.FILLED)                            # Se dibuja el contorno del esquejes en la imagens creada en la línea anterior, para que solo exista el contorno del esqueje
    mascara = cv2.bitwise_and(original_image,original_image,mask = imagen_binarizada)                      # Se aplica la mascara del contorno de la imagen original con una operacion and 
    centerContour,sizeContour,theta = cv2.fitEllipse(contorno_esqueje)                                     # Se encierra el esqueje en la elipse de menor area para obtener el ángulo que forma con la horizontal
    esqueje_rotado=rotateAndScale(mascara,1,theta)                                                         # Se el llamdo a la función para rotar el contorno del esqueje en la imagen 
    ret,imagen_binarizada_2 = cv2.threshold(esqueje_rotado[:,:,1],5,255,cv2.THRESH_BINARY)                 # Se realiza una binarización invertida con un umbral de 5
    contours2, hierarchy2 = cv2.findContours(imagen_binarizada_2,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE) # Se encuetra los contornos de la imagen binarizada 2
    contours2 = sorted(contours2, key=cv2.contourArea,reverse=True)                                        # Se ordenan los contornos de mayor area a menor area  
    contorno_esqueje2 = contours2[0]                                                                       # Se toma el primer contorno que corresponde al de mayor area  
    imagen_binarizada_2[...] = 0                                                                           # Se lleva todos los valores de la imgaen a 0
    cv2.drawContours(imagen_binarizada_2, [contorno_esqueje2], 0, 255, cv2.FILLED)                         # Se dibuja el contorno del esquejes en la imagens creada en la línea anterior, para que solo exista el contorno del esqueje
    
    x,y,w,h = cv2.boundingRect(contorno_esqueje2)                                                          # Se encuentra el rectángulo de menor área que encierra el contorno del esqueje
    dst_roi = esqueje_rotado[y:y+h,x:x+w]                                                                  # Se toma la sección de la imagen usando la máscara dada por las dimensiones del rectángulo encontrado en la linea anterior
    
    imagen_binarizada_3 = imagen_binarizada_2[y:y+h,x:x+w] 
    cols,rows=dst_roi.shape[:2] 
    #print("col: ", cols, "Rows",rows)
                                                                           # Se obtienen las dimensiones de la imagen (Número de filas y columnas)
    """----------------------------------- f.3. Validación para rotar la imagen 90° -----------------------------------------------------------------------"""
    if rows<cols:                                                                                          # Si el número de filas es menor que de columnas se hace una rotación de 90° 
        esqueje_rotado = rotateAndScale(dst_roi,1,90)
        imagen_binarizada_3 = rotateAndScale(imagen_binarizada_3,1,90)            
    
    """------------------------------------------- f.4. Aplicación morfoligía -----------------------------------------------------------------------------"""
    kernel = np.ones((5,11),np.uint8)                                                                      # Definición del elemento estructurante
    imagen_binarizada_3 = cv2.morphologyEx(imagen_binarizada_3, cv2.MORPH_OPEN, kernel)                    # Se realiza una apertura 
    cols,rows=dst_roi.shape[:2]                                                                            # Se obtienen las dimensiones de la imagen (Número de filas y columnas)
          
    longitud_cm = cols*factor                                                                              # Se convierte la longitud a centímetros multiplicando por el factor de conversión  
    
    """-------------------------- f.5. Asignación de la clasificación y clase del esqueje -------------------------------------------------------------------"""
    if cols<corto_pixeles and cols>200:                                                                    # El esqueje es corto si el número de columnnas es menor a la longitud de un esqueje corto en pixeles 
        clasificacion='1'
        clase='Corto'
    elif cols>largo_pixeles:                                                                               # El esqueje es largo si el número de columnnas es mayor a la longitud de un esqueje largo en pixeles
        clasificacion='2'
        clase='Largo'
    elif cols<200 or rows<20:                                                                              # La imagen no tiene clasificacion si el número de columnnas es menor que 200 pixeles o el número de filas es menor que 20
        clasificacion='0'
        clase='nada'
    elif cols>corto_pixeles and cols<largo_pixeles:                                                        # El esqueje es ideal si el número de columnnas es mayor a la longitud de un esqueje corto en pixeles y menor a la longitud de un esqueje largo en pixeles
        clasificacion='4'
        clase='Ideal'
    
    """----------------------------------- f.6. Proceso para hallar hoja en base ----------------------------------------------------------------------------"""
    if clase != 'corto':
        a=0  
        b=0
        d=0
        
        row,col=imagen_binarizada_3.shape
        
        # Realización de lntegral de proyeccion sobre la imagen binaria
        for c in range(col):
            a=np.append(a,(imagen_binarizada_3[:,c] > 100).sum())
        
        promedio=np.average(a[np.uint(a.size*0.01):np.uint(a.size*0.5)])
        
        if promedio<100:
            b = a
        else:
            b = np.flipud(a)
            
        if promedio<100:pow
        if np.uint(b.size)>200:
            b=savitzky_golay(b,11,1)
            b=savitzky_golay(b,11,1)
            d=np.diff(b)
            d=savitzky_golay(d,11,1)
   
            # Se hace una selección usando la media
            promedio=np.average(b[np.uint(hojabase_pixeles*0.4):np.uintp(hojabase_pixeles*0.5)])
            valor_hojabase_pixeles=b[hojabase_pixeles]
            
            if np.abs(valor_hojabase_pixeles-promedio)> np.uintp(promedio*0.22):      
                clasificacion='3'
                clase='Hoja en base'


    tallo_promedio,area_foliar = encontrar_medidas(esqueje_rotado)                                      # Se llama la función para encontrar area foliar y tallo promedio del esqueje
   
    ret_esqueje_rotado = esqueje_rotado                                                                 # Imagen que se retorna
    b,g,r = cv2.split(esqueje_rotado)                                                                   # Se obtienen las capas b,g,r
    esqueje_rotado = cv2.merge([r,g,b])                                                                 # Se cambia la imagen a r,g,b

    return tallo_promedio,area_foliar,ret_esqueje_rotado, longitud_cm, clasificacion, clase, dst_roi.copy(), contorno_esqueje2
    
"""------------------------------------------- g. Rotación de la imagen ----------------------------------------------------------------------------"""
def rotateAndScale(img_binarizada, scaleFactor = 0.5, theta = 30):
    """Esta Función tiene como parámetros de entreda la imagen binarizada, un factor de escala para cambiar el tamaño de la imagen y el ángulo que se desea
       rotar la imagen. Esta función tiene como retorno la imagen rotada."""
       
    (old_filas,old_columnas) = img_binarizada.shape[:2]                                                                                       # Se obtiene el número de  filas y columnas de la imagen 
    Matriz_rotada = cv2.getRotationMatrix2D(center=(old_columnas/2,old_filas/2), angle=theta, scale=scaleFactor)                              # Rota la imagen theta grados alrededor se su centro
    
    new_columnas,new_filas = old_columnas*scaleFactor,old_filas*scaleFactor                                                                   # Se escala la imagen
    r = np.deg2rad(theta)                                                                                                                     # Se convierte el ángulo de grados a radianes
    new_columnas,new_filas = (abs(np.sin(r)*new_filas) + abs(np.cos(r)*new_columnas),abs(np.sin(r)*new_columnas) + abs(np.cos(r)*new_filas))  # Encontrar las nuevas dimensiones de la imagen escalada
    
    (tx,ty) = ((new_columnas-old_columnas)/2,(new_filas-old_filas)/2)                                                                         # Encuetra un promedio entre la imagen original y la imagen escalada
    Matriz_rotada[0,2] += tx 
    Matriz_rotada[1,2] += ty
    
    rotated_and_scaled_img = cv2.warpAffine(img_binarizada, Matriz_rotada, dsize=(int(new_columnas),int(new_filas)))
    # La función warpAffine, trabaja de la siguiente forma:
    # 1. aplica a la matriz rotada una transformacion a cada uno de los pixeles de la imagen original
    # 2. guarda todo lo que cae en la parte superior izquierda de la imagen resultante
    
    return rotated_and_scaled_img

"""------------------------------------------- h. Filtro savitzky_golay ----------------------------------------------------------------------------"""
def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    """ Smooth (and optionally differentiate) data with a Savitzky-Golay filter.The 
        Savitzky-Golay filter removes high frequency noise from data. It has the
        advantage of preserving the original shape and features of the signal better
        than other types of filtering approaches, such as moving averages techniques."""

    try:
        window_size = abs(int(window_size))
        order = abs(int(order))
    
    except ValueError:
        raise ValueError("window_size and order have to be of type int")
    
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')


"""------------------------------------ i. Modo de lectura desde un directorio -----------------------------------------------------------------------------"""
def ejecucion_directorio():
    """Esta función no tiene parámetros de entrada y es la encargada de administrar el procesamiento de los esquejes al haber seleccionado el modo de 
       lectura desde un directorio."""
       
    """---------------------------------------- i.1. Definición de variables -----------------------------------------------------------------"""
    global ruta_lectura                                                             # Variable donde se almacena la ruta del directorio donde estan las imagenes a procesar
    global clase                                                                    # Variable que almacena la clase
    global Cantidad_imagenes                                                        # Variable que almacena la cantidad de imagenes .TIFF que hay en el directorio seleccionado
    global num_esqueje_analizado                                                    # Variable que almacena la posición de la ultima imagen que se analizó en caso de una suspensión de la ejecución
    global longitud_cm                                                              # Variable que almacena la longitud obtenida del esqueje dada en centímetros
    global rutas_esquejes                                                           # Variable tipo lista que almacena todas las rutas de las imagenes .TIFF del directorio seleccionado           
    global img_count                                                                # Variable que cuenta la cantidad de imagenes procesadas
    #global tallo_promedio
    #global area_foliar
    

    
    """--------------------------------- i.2. Validación para guardar resultados -----------------------------------------------------------------"""
    if (num_esqueje_analizado == 0):                                                # Si es el primer esqueje analizado se abre el archivo donde se almacenan los resultados
        file_results = open(ruta_lectura + "/Resultados.csv", 'w')               
        file_results.write("Ruta Esqueje;Longitud (cm);Clasificacion;Area Foliar;Tallo promedio\n")            # Se asigna el título de las columnas
                       
    """------------------- i.3. Ciclo principal donde se analizan las imágenes del directorio ----------------------------------------------------"""
    for img_count in range(num_esqueje_analizado, Cantidad_imagenes+1):

        if flag_break == 1:                                                         # Si la bandera es 1 se rompe el ciclo, lo que indica que se presionó el botón detener
            break
        
        try :
            image = cv2.imread(rutas_esquejes[num_esqueje_analizado])
                    
            tallo_promedio,area_foliar, esqueje_rotado, longitud_cm, classification, clase, imagenSegmentada, contorno_esqueje= segmentacion(image[100:1000,100:1200])   
            actualizar_interfaz(image,esqueje_rotado)        
            file_results.write(rutas_esquejes[num_esqueje_analizado]+";"+str(round(longitud_cm,2))+";"+clase+";"+str(round(area_foliar,2))+";"+str(round(tallo_promedio,2))+"\n")
            num_esqueje_analizado = img_count

        except :
            pass 
        
    if (num_esqueje_analizado == Cantidad_imagenes):
        detener()
        messagebox.showinfo("Ejecución finalizada", "Las imágenes del directorio elegido fueron procesadas con éxito. Puede consultar la hoja de resultados en el mismo directorio donde se encuentran las imágenes.")
        file_results.close()
               
#"""--------------------------------------- j. Modo de lectura desde cámara -----------------------------------------------------------------------------"""
def ejecucion_camera():
    """Esta función no tiene parámetros de entrada y es la encargada de administrar el procesamiento de los esquejes al haber seleccionado el modo de lectura desde la cámara. Allí se realiza la configuración 
       del puerto serial y de la cámara, asegurándose de que efectivamente están disponibles estos dispositivos. Luego se inicia el ciclo infinito donde se captura la imagen y se procesa haciendo uso de la 
       función segmentacion().No se retorna ninguna variable."""
       
    """---------------------------- j.1. Definición e inicialización de variables -----------------------------------------------------------------------"""
    global my_deque                                     # Se define una variable tipo deque con base en el vector banda
    global num_esqueje_analizado                        # Contador de la cantidad de imagenes analizadas (Generación de base de datos )
    global Text_ruta
    global vector_banda                                 # Arreglo que permitirá administrar las posiciones de los esquejes en la banda  
    global corto_pixeles                                # Medidad de esquejes cortos en pixeles
    global largo_pixeles                                # Medidad de esquejes largos en pixeles
    global label_longitud 
    global label_cantidad
    global classification                               # Clasificación asignada al esqueje analizado
    global hojabase_pixeles                             # Medidad de hoja en base en pixeles
    global cantidad_esquejes
    global longitud_cm
    global ruta_almacenamiento                                       
    global almacenamiento
    global procesar_imagen
    global cont
    global plc
    global clase_codificada 
    global Cantidad_imagenes 
                                                         
    classification='0'                                  # Se inicializa la calsificación en '0'
    vector_banda=list('000000000000')                   # Se inicializa todas las posiciones en 0 (Sin calsificación)                   
    my_deque = deque(vector_banda)   
        
    try:
        Text_ruta.destroy()
    except:
        pass
    
    """------------------------------------- j.2. Inicialización de la cámara ----------------------------------------------------------------------------""" 
    # capture = cv2.VideoCapture(0)
    # index = capture.set(cv2.CAP_PROP_FPS,30)
    # capture.set(3,1280)
    # capture.set(4,1024)
    # count = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    # capture.set(cv2.CAP_PROP_POS_FRAMES,count-1)
    # capture.set(cv2.CAP_PROP_SETTINGS, 0); 
#    cv2.waitKey(10000)

 
#    ret, frame = capture.read()          # Se realiza la captura de un frame usando la variable tipo video 
    ret=False
    if(ret == True):
         messagebox.showerror("Mensaje de error","No se detecta la cámara de la máquina, por favor conéctela.")
         return 0
        
    

    """------------------- j.4. Ciclo para realizar la captura frame por frame de las imagenes de los esquejes------------------------------------""" 
#    while(flag_break == 0):        
            # Se intenta procesar un frame utilizando una excepción para evitar problemas con los frames errados   
    if(flag_break == 0):
        try:               
            """-------------------------- j.4.1. Lectura del frame y valor serial-----------------------------------------------------------------""" 

            if (procesar_imagen==True):  # Esta linea es la que reemplaza el infrarojo, si se cumple la condicion de entrada por teclado procede a proceaar el frame obtenido.                       
                """----------------------------------------- a.2. Obtención de las rutas de las imágenes ------------------------------------------------"""
                ruta_lectura = "C:/Users/Administrator/Documents/GEPAR/Base_de_datos/Grande"                       # Se abre el explorador de archivos para buscar el directorio en el ordenador y se captura dicha ruta
                rutas_esquejes = glob.glob(ruta_lectura + "/*.TIFF")      # Se genera la lista con todas las rutas de las imagenes .TIFF del directorio seleccionado
                  
                #print("Si esta leyendo")
                frame = cv2.imread(rutas_esquejes[cantidad_esquejes])#En ves de leer la camara, se lee un archivo donde estab las imagenes guardadas
                image = frame.copy()           
                procesar_imagen=False
                                     
                #Se invoca la funcion 'segmentación' con la imagen capturada pero seleccionando una región para evitar bordes del frame original
                esqueje_rotado, longitud_cm, classification, clase, imagenSegmentada, contorno_esqueje= segmentacion(image[100:1000,100:1200]) 
                #prin("Segmento")
                """-----------   j.4.2.1. Validación para guardado de la imagen capturada -----------------------------------------------------------""" 
                if (almacenamiento == 'yes'):
                    cv2.imwrite(ruta_almacenamiento +'_'+ clase +'_'+ str(cantidad_esquejes+1) + '.TIFF',image)#Se guarda la imagen con la ruta predeterminada        

                """-----------   j.4.2.2. Envió de señales para encender LED ------------------------------------------------------""" 
                
                if(clase=="Vacio"): 
                    clase_codificada = 0
 
                        
                elif(clase=="Largo"):                   # Si el esqueje es largo, se envia la señal para disparar el segundo actuador    
                    clase_codificada = 1

            
                elif(clase=="Hoja en base"):            # Si el esqueje tiene hoja en base, se envia la señal para disparar el tercer actuador
                    clase_codificada = 2

                    
                elif(clase=="Corto"):                   # Si el esqueje es largo, se envia la señal para disparar el segundo actuador    
                    clase_codificada = 3

                    
                elif(clase=="Ideal"):                   # Si el esqueje es ideal.
                    clase_codificada = 4

                
                else:                                   # Si retorna más de un esqueje
                    clase_codificada = 5
                              
                
                cantidad_esquejes = cantidad_esquejes + 1     # Se aumenta en uno el contador de las imagenes procesadas                
                num_esqueje_analizado = cont    
                actualizar_interfaz(image,esqueje_rotado)     # Se invoca la función para actualziar la interfaz
        
        except :  
            # La excepción se da cuando se leyó correctamente un frame. Se deja pasar para capturar otro frame y así­ no generar errores
            pass  
""" ----------------------------------------------------------------------------------------------------------------------------------------
    ------------------------------------------------- 3.Funciones asociadas al PLC ------------------------------------------------
    ---------------------------------------------------------------------------------------------------------------------------------------- """
                  
        
def conectar_PLC():
    """
    Funcion para verificar conexion con el plc para establecer comunicación utilizando la IP del PLC y el puerto de comunicación
    """
    global plc                                #Variable global para comunicar el PLC 
    global procesar_imagen                    #Variable para saber si la imagen ya esta disponible para procesar la imagen
    global flag_break                         # Bandera que cuando vale 1 indica que se debe detener el procesamiento de las imágenes  
    
    host= "192.168.1.5"                       # IP del PLC
    port = 502                                # Puerto de conexion del PLC 
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as plc:
            plc.settimeout(5)                   # Establecer un tiempo de espera para la conexión
            plc.connect((host, port))           #Conectar el PLC a la IP y puerto asignado
            messagebox.showinfo("Conexión establecida","Se ha establecido la conexion con el PLC, puede continuar con la ejecución del programa")
            repeat_event()
            #ejecucion_camera()
            
    except ConnectionRefusedError:  
        messagebox.showerror("ERROR","No se pudo conectar al PLC. Verifica la dirección y el puerto.")
        
    except socket.timeout:
        messagebox.showerror("ERROR","Tiempo de espera agotado. No se pudo conectar al PLC.")
        
    except Exception as e:
        messagebox.showerror("ERROR",f"Error al conectar al PLC: {e}")
        
def repeat_event():
    """
    Con esta función se realiza una lectura periodica del PLC cada 20 mili-segundos para verificar
    el estado de la máquina y las peticiones que se tienen según los eventos transcurridos en el tiempo
    """
    leer_PLC()
    MainWindow.after(100, repeat_event)  # La funcion que se repite cada 20ms

def escribir_PLC(contador,clase_codificada,velocidad,boton_start_stop):
    """
    Función para escribir los datos en el PLC y llevar control de la máquina en sincronia con los datot 
    obtenidos por el software los datos que se envían son:
    
        1 clasificación del esqueje
        2 Velocidad del variador
        3. Estado del boton de mover la banda
        4. Verificación de conexion 
    """
    global plc
    global Cantidad_imagenes 

    boton_start_stop= not (boton_start_stop)
    
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as plc:
        plc.connect(("192.168.1.5",502))

        # trama = "\x00\x00\x00\x00\x00\x06\x01\x03\x10\x00\x00\x01"
        #for contador in range (0,5):
        frame = bytearray()
        frame.append(0x01) #identificador de mensaje
        frame.append(0x00)
        frame.append(0x00)
        frame.append(0x00)
        frame.append(0x00)
        frame.append(0x11)
        frame.append(0x01) # Byte para identificar que es esclavo
        frame.append(0x10) # codigo Modbus para escritura al PLC, es decir escribir a los registros.
        frame.append(0x10) # Dirección alta (para escritura)
        frame.append(0x0A) # Dirección baja (para escritura)
        frame.append(0x00) # Numero de palabras parte alta
        frame.append(0x05) # Numero de palabras parte baja
        frame.append(0x0A) # Bytes a enviar
        frame.append(0x00) # contador a enviar parte alta
        frame.append(contador) # contador a enviar parte baja que es el contador D10 (Aqui va el dato recibido en el contador del otro codigo) -> pasar derecho el contador de lectiura
        frame.append(0x00) # Clasificacion alta
        frame.append(clase_codificada) # Clasificacion baja (Clasificacion codificada , despues del procesamiento de imagenes)   -> Claisifacion variable global
        frame.append(0x00) # velocidad alta del variador 
        frame.append(0x00) # Velocidad baja del variador   -< VEl variador
        frame.append(0x00) # Botón Start parte alta
        frame.append(boton_start_stop) # Botón Start parte baja  ->flag_break negado
        frame.append(0x00) # Palabra verificacion de conexion parte alta siempre en 0
        frame.append(0x01) # Palabra verificacion de conexion parte baja siempre en 1

            
        plc.sendall(frame)       
        data = plc.recv(1024)
        print("Clase:",clase_codificada)
        print("Escrito", repr(frame))
        
        plc.close()

def leer_PLC():

    """
    Esta es la función que permite ralizar la lectura del estado de la máquina por medio del PLC utilzando protocolo MODBUS
    En esta funcion se obtiene información:
        1 Leer imagen: una bandera que indica si ha pasado un eslabon para capturar una imagen a procesar
        2 contador: que permite llevar sincronización entre el software y hardware
        3 corriente del variador: Permite controlar la velocidad y evitar daños de la banda transportadora
        4 Estado del variador: si se enciende o se apaga el movimiento de la banda, pulsando un botón físico
    
    """
     
    global procesar_imagen     
    global cont
    global plc
    global flag_break                                               # Bandera que cuando vale 1 indica que se debe detener el procesamiento de las imágenes     
    global clase_codificada
       
    # trama = "\x00\x00\x00\x00\x00\x06\x01\x03\x10\x00\x00\x01"
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as plc:
        plc.connect(("192.168.1.5",502))
        
        #Protocolo MODBUS para lectura 
        frame = bytearray()
        frame.append(0x01) #identificador de mensaje
        frame.append(0x00) 
        frame.append(0x00)
        frame.append(0x00)
        frame.append(0x00)
        frame.append(0x06) # Numero de bytes que siguen
        frame.append(0x01) # Byte para identificar que es esclavo
        frame.append(0x03) # codigo Modbus para escritura
        frame.append(0x10) # Dirección alta (para escritura)
        frame.append(0x00) # Dirección baja (para escritura)
        frame.append(0x00) # numero de memoria parte alta
        frame.append(0x04) # numero de memoria parte baja
        
        
        plc.sendall(frame) #Solicutd al PLC      
        data = plc.recv(1024) # Guardar datos devueltos por el PLC en el arreglo data
        #print("Recibido", repr(data))
        
    if(data[10]==1): 
        #si paso un eslavon la cámara ya tomo foto  y se procede a procesar la siguiente imagen
        procesar_imagen=True                
        ejecucion_camera()
        escribir_PLC(data[12],clase_codificada,1,flag_break) 
        cont+=1 
        plc.close() 

        #if (num_esqueje_analizado == Cantidad_imagenes):
            #detener()
            #messagebox.showinfo("Ejecución finalizada", "Las imágenes del directorio elegido fueron procesadas con éxito. Puede consultar la hoja de resultados en el mismo directorio donde se encuentran las imágenes.")
            #file_results.close()
            
        
    else:
        # coloco contador y clasificacion en cero para enviar al plc 
        escribir_PLC(data[12],0,1,flag_break) 
        plc.close() 
    
        #if (num_esqueje_analizado == Cantidad_imagenes):
            #detener()
            #messagebox.showinfo("Ejecución finalizada", "Las imágenes del directorio elegido fueron procesadas con éxito. Puede consultar la hoja de resultados en el mismo directorio donde se encuentran las imágenes.")
            #file_results.close()

""" ----------------------------------------------------------------------------------------------------------------------------------------
    ------------------------------------------------- 4. Definición de funciones asociadas a botones ------------------------------------------------
    ---------------------------------------------------------------------------------------------------------------------------------------- """
  
def agregar_esqueje():
    """
    Función que permite agregar una nueva variedad de esqueje desde un boton
    Se introduce el nombre de la variedad, el tamaño en cm del esqueje corto, largo,  y hoja en base 
    y se almacena los datos en un archivo formato json
    """
    
    input_window = tk.Toplevel(MainWindow)
    input_window.title('Agregar nueva variedad de un esqueje')
    input_window.configure(bg="#314354", highlightbackground='#343A40')
    input_window.geometry("500x400")

    # Make the input window a child window of the main window and disable it
    input_window.transient(MainWindow)
    input_window.grab_set()

    # Create and pack the Label and Entry widgets for the name, Largo, corto, and hoja_base parameters
    name_label = tk.Label(input_window, text='Variedad de Esqueje:', bg="#4B4F65", fg='#AAAABA', font=("calibri", 12, "bold"))
    name_label.pack(pady=5)

    name_entry = tk.Entry(input_window, bg="#343A40", fg='#AAAABA', font=("calibri", 12, "bold"))
    name_entry.pack(pady=5)

    largo_label = tk.Label(input_window, text='Largo en cm:', bg="#4B4F65", fg='#AAAABA', font=("calibri", 12, "bold"))
    largo_label.pack(pady=5)

    largo_entry = tk.Entry(input_window, bg="#343A40", fg='#AAAABA', font=("calibri", 12, "bold"))
    largo_entry.pack(pady=5)

    corto_label = tk.Label(input_window, text='Corto en cm:', bg="#4B4F65", fg='#AAAABA', font=("calibri", 12, "bold"))
    corto_label.pack(pady=5)

    corto_entry = tk.Entry(input_window, bg="#343A40", fg='#AAAABA', font=("calibri", 12, "bold"))
    corto_entry.pack(pady=5)

    hoja_base_label = tk.Label(input_window, text='Hoja en Base en cm:', bg="#4B4F65", fg='#AAAABA',
                               font=("calibri", 12, "bold"))
    hoja_base_label.pack(pady=5)

    hoja_base_entry = tk.Entry(input_window, bg="#343A40", fg='#AAAABA', font=("calibri", 12, "bold"))
    hoja_base_entry.pack(pady=5)

    # Create the OK and Cancel buttons and pack them
    def save_and_close():
        # Get the new value and parameters from the input dialog boxes
        new_name = name_entry.get()
        new_largo = largo_entry.get()
        new_corto = corto_entry.get()
        new_hoja_base = hoja_base_entry.get()

        # Add the new value to the list as a dictionary with the new parameters
        if new_name:
            new_value = {'name': new_name, 'Largo': new_largo, 'Corto': new_corto, 'Hoja_base': new_hoja_base}
            values.append(new_value)
            # Save the updated values to the file
            with open('TipoEsquejes.json', 'w') as file:
                json.dump(values, file)
            combox.config(values=[value['name'] for value in values])

        # Close the input window
        input_window.destroy()

    ok_button = tk.Button(input_window, text='Agregar', command=save_and_close)
    ok_button.pack(pady=5)
 
    cancel_button = tk.Button(input_window, text='Cancelar', command=input_window.destroy)
    cancel_button.pack(pady=5)

    # Center the input window on the main window
    input_window.geometry("+%d+%d" % (MainWindow.winfo_rootx() + 50, MainWindow.winfo_rooty() + 50))
    
def get_selected_value():
    # Get the currently selected value from the Combobox
    name = combox.get()
    # Find the dictionary for the selected value
    selected_value = next((value for value in values if value['name'] == name), None)
    return selected_value

def get_params_by_name(name):
    for value in values:
        if value['name'] == name:
            largo = value.get('Largo', '')
            corto = value.get('Corto', '')
            hoja_base = value.get('Hoja_base', '')
            return largo, corto, hoja_base
    # If the name is not found in the values list, return empty strings for the parameters
    return '', '', ''
 

def abrir_ventana_info():
    """
    Función en la cual se muestra cual es el objetivo principal del proyecto quienes son los involucrados y los respectivos logos
    """
    # Definir las variables de imagen como globales
    global imagen1_tk, imagen2_tk, imagen3_tk, imagen4_tk
    
    # Crear una nueva ventana
    nueva_ventana = tk.Toplevel(MainWindow)
    
    nueva_ventana.configure()

    # Configurar el tamaño de la ventana
    nueva_ventana.geometry("1000x500")

    # Configurar el título de la ventana
    nueva_ventana.title("ALSOFT - Acerca del Software")

     # Agregar etiquetas con el texto
    texto1 = "Este software utiliza técnicas de visión artificial y PLC para automatizar la selección de distintos tipos de esquejes. Se trata de una herramienta tecnológica diseñada para optimizar y agilizar los procesos de selección, garantizando una mayor eficiencia y precisión en los resultados."
    etiqueta_texto1 = tk.Label(nueva_ventana, text=texto1, wraplength=500,fg = '#AAAABA',font = ("calibri", 14, "bold"), justify="center")
    etiqueta_texto1.pack()

    texto2 = "El software ha sido desarrollado con la finalidad de clasificar los esquejes de acuerdo a las medidas suministradas por la empresa ASOCOLFLORES. Gracias a la información, los esquejes pueden ser clasificados en cuatro categorías: corto, largo, hoja en base o ideal."
    etiqueta_texto2 = tk.Label(nueva_ventana, text=texto2, wraplength=500,fg = '#AAAABA',font = ("calibri", 14, "bold"), justify="center")
    etiqueta_texto2.pack()

    texto3 = "El proyecto ALIES fue desarrollado en colaboración con la Universidad de Antioquia, el Grupo GEPAR UdeA y el Grupo de Diseño Mecánico"
    etiqueta_texto3 = tk.Label(nueva_ventana, text=texto3, wraplength=600,fg = '#AAAABA',font = ("calibri", 14, "bold"), justify="center")
    etiqueta_texto3.pack()
    
    # Cargar las imágenes
    imagen1 = Image.open("gepar.png")
    imagen2 = Image.open("udea.png")
    imagen3 = Image.open("asocol.png")
    imagen4 = Image.open("GDM.jpeg")

    #Crear un objeto Canvas en la ventana
    canvas = tk.Canvas(nueva_ventana, width=800, height=600)
    canvas.pack()
    
    #Redimensionar las imágenes
    #print("Redimensionando imágenes...")
    imagen1 = imagen1.resize((100, 100))
    imagen2 = imagen2.resize((100, 100))
    imagen3 = imagen3.resize((250, 100))
    imagen4 = imagen4.resize((200, 100))

    # Convertir las imágenes a formato compatible con TKinter
    #print("Convirtiendo imágenes...")
    imagen1_tk = ImageTk.PhotoImage(imagen1)
    imagen2_tk = ImageTk.PhotoImage(imagen2)
    imagen3_tk = ImageTk.PhotoImage(imagen3)
    imagen4_tk = ImageTk.PhotoImage(imagen4)

    
    # Agregar las imágenes al Canvas
    #print("Agregando imágenes al Canvas...")
    canvas.create_image(100, 100, image=imagen1_tk)
    canvas.create_image(250, 100, image=imagen2_tk)
    canvas.create_image(450, 100, image=imagen3_tk)
    canvas.create_image(700, 100, image=imagen4_tk)

    # Mostrar el Canvas en la ventana
    canvas.pack() 

def estadisticas():
    """
    Esta función tiene como objetivo localizar un archivo CSV que almacene los datos recopilados de la máquina. Posteriormente, realiza el análisis estadístico de dichos datos y genera un diagrama de torta que facilita la visualización de la distribución de cada esqueje según su especie
    """
    try:
        # Abrir el cuadro de diálogo para seleccionar el archivo CSV
        ruta_archivo = filedialog.askopenfilename(title="Seleccionar archivo CSV", filetypes=[("Archivos CSV", "*.csv")])

        # Verificar si se seleccionó un archivo
        if ruta_archivo:
            # Cargar el archivo CSV en un DataFrame
            df = pd.read_csv(ruta_archivo, delimiter=";")

            # Calcular el conteo de clases
            conteo_clases = df['Clasificacion'].value_counts()

            # Mostrar estadísticas y plot en una nueva ventana
            ventana_estadisticas = tk.Toplevel(MainWindow)
            ventana_estadisticas.title("Estadísticas")
            ventana_estadisticas.configure(bg="#314354", highlightbackground='#343A40')

            # Crear un widget de texto para mostrar las estadísticas
            texto_estadisticas = tk.Text(ventana_estadisticas, wrap="word")
            texto_estadisticas.insert("1.0", f"Estadísticas:\n\n{df.describe()}\n\nConteo de clases:\n\n{conteo_clases}")
            texto_estadisticas.pack(expand=True, fill="both")

            # Crear un subplot más pequeño para el plot de barras
            fig, ax = plt.subplots(figsize=(4, 3))
            conteo_clases.plot(kind='pie', ax=ax)
            ax.set_title('Conteo de Clases')
            ax.set_xlabel('Clasificación')
            ax.set_ylabel('Frecuencia')

            # Agregar el plot a la ventana tkinter
            canvas = FigureCanvasTkAgg(fig, master=ventana_estadisticas)
            canvas.draw()
            canvas.get_tk_widget().pack(expand=True, fill="both", side="top", pady=(0,0),ipady=0)


        else:
            messagebox.showwarning("Advertencia", "No se seleccionó ningún archivo CSV.")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el archivo CSV. Error: {e}")



""" ----------------------------------------------------------------------------------------------------------------------------------------
    ------------------------------------------------- 4. Definición de la ventana principal ------------------------------------------------
    ---------------------------------------------------------------------------------------------------------------------------------------- """


global cantidad_esquejes
cantidad_esquejes = 0
cont=0

MainWindow = tk.Tk() # Se crea la ventana principal para la interfaz.

# Se crea la ventana principal, se asignan tí­tulo, dimensiones de la ventana y color del background.
MainWindow.title('ALSOFT')
MainWindow.configure(bg = "#314354") #E3E3F0, #3C4055 el que es 


frame = tk.Frame(MainWindow)


screen_width = MainWindow.winfo_screenwidth() #Se obtiene el ancho de la ventana 
screen_height = MainWindow.winfo_screenheight()#Se obtiene el alto de la ventana
screen_resolution = str(screen_width)+'x'+str(screen_height)#Se crea la dimensiones de la ventada
MainWindow.geometry(screen_resolution)
               
# Label para el tí­tulo de la imagen de entrada
label_imag_ORIGINAL = tk.Label(text='Imagen original', font = ("Helvetica", 18, "bold"), fg = '#AAAABA', bg = "#314354") 
label_imag_ORIGINAL.place(x=247,y=0)

# Label para el tí­tulo de la imagen de salida
label_imag_PROCESADA = tk.Label(text='Imagen procesada', font = ("Helvetica", 18, "bold"), fg = '#AAAABA', bg = "#314354")
label_imag_PROCESADA.place(x=895,y=0)

# Margenes de las imagenes
margen_1 = tk.Canvas(width=570, height=501, bg = "#343A40", highlightbackground='#343A40')
margen_1.place(x=35,y=35)

margen_2 = tk.Canvas(width=570, height=501, bg = "#343A40", highlightbackground='#343A40')
margen_2.place(x=663,y=35)


# Imagenes en blanco al iniciar el programa
label_imagenDefecto1 = tk.Label(MainWindow,width = 78, height = 32, bg = '#868E96')
label_imagenDefecto1.place(x=45,y=42)

label_imagenDefecto2 = tk.Label(MainWindow, width = 78, height = 32, bg = '#868E96')
label_imagenDefecto2.place(x=673,y=42)


# Rectangulo que encierra los elementos para elegir el modo de lectura
rectangle_1 = tk.Canvas(width=540, height=90, bg = "#4B4F65", highlightbackground='black')
rectangle_1.place(x = 703,y = 600)

# Rectangulo que encierra los labels que muestran la información obtenida 
rectangle_2 = tk.Canvas(width=610, height=90, bg = "#4B4F65", highlightbackground='black')
rectangle_2.place(x = 38,y = 600)

# Radiobutton para elegir el modo de lectura, ya sea desde la camara o desde un archivo
state_radiobutton=tk.IntVar()
label_Titulo_radiobutton = tk.Label(text='Modo de lectura', font = ("calibri", 17, "bold"), fg = '#BABACA', bg = "#4B4F65")
radiobutton_archivo = tk.Radiobutton(MainWindow, text='Directorio', command = ask_path_directorio, value = 1, variable = state_radiobutton,  font = ("calibri", 15), fg = '#AAAABA', bg = "#4B4F65",selectcolor = "#3C4055" )
radiobutton_maquina = tk.Radiobutton(MainWindow, text='Cámara', command = ask_path_camera, value = 2, variable = state_radiobutton,  font = ("calibri", 15), fg = '#AAAABA', bg = "#4B4F65",selectcolor = "#3C4055") 
label_Titulo_radiobutton.place(x=753,y = 602)
radiobutton_archivo.place(x=730,y=627) 
radiobutton_maquina.place(x=730,y=655)

# Label para el titulo del label que indica la longitud del esqueje analizado
label_Titulo_longitud = tk.Label(text='Longitud del esqueje (cm)', font = ("calibri", 17, "bold"), fg = '#AAAABA', bg = "#4B4F65")
label_Titulo_longitud.place(x=43,y = 645)

# Label para el titulo del label que indica la cantidad de esqueje analizados
label_Titulo_cantidad = tk.Label(text='Esquejes analizados', font = ("calibri", 17, "bold"), fg = '#AAAABA', bg = "#4B4F65")
label_Titulo_cantidad.place(x=43,y = 607)

# Label para el titulo del label que indica la clasificación de esqueje analizados
label_Titulo_clasificacion = tk.Label(text='Clasificación', font = ("calibri", 17, "bold"), fg = '#AAAABA', bg = "#4B4F65")
label_Titulo_clasificacion.place(x=395,y = 627)

# Widget de texto para mostrar la longitud del esqueje analizado
Text_longitud = tk.Text(font = ("calibri", 14, "bold"), width = 7, height = 1, fg = '#000000', bg = "#9A9EAD")
Text_longitud.place(x=300,y = 650)

# Widget de texto para mostrar la cantidad de esqueje analizados
Text_cantidad = tk.Text(font = ("calibri", 14, "bold"), width = 7, height = 1, fg = '#000000', bg = "#9A9EAD")
Text_cantidad.place(x=300,y = 610)

# Widget de texto para mostrar la clasificación del esqueje analizado
Text_clasificacion = tk.Text(font = ("calibri", 14, "bold"), width = 11, height = 1, fg = '#000000', bg = "#9A9EAD")
Text_clasificacion.place(x=520,y = 632)

# Se crea el botón para aplicar el proceso seleccionado
button_iniciar_detener = tk.Button(text = 'Iniciar', font = ("calibri", 14, "bold"), width = 10, height = 1, command = iniciar, fg = '#FFFFFF', bg = '#276CDE', bd=7, overrelief = "sunken")
button_iniciar_detener.place(x = 935,y = 638)


# Archivo para almacenara las variedade de esquejes 
try:
    with open('TipoEsquejes.json', 'r') as file:
        values = json.load(file)
except FileNotFoundError:
    values = []

# ComboBox para seleccionar el proceso deseado
combox = tk.ttk.Combobox(MainWindow,font = "ArialBlack 12 bold", width = 12, height = 1, values=[value['name'] for value in values])
combox.current(0)
combox.place(x = 935,y = 608)

# Se crea un boton  para añadir una nueva variedad de esqueje
add_button = tk.Button(MainWindow, text='Agregar', width = 8, height = 1, command= agregar_esqueje, fg = '#FFFFFF', bg = '#276CDE', overrelief = "sunken")
add_button.place(x=1070, y=608)

# Crear un botón en la ventana principal para acerca de 
about_boton = tk.Button(MainWindow, text="Acerca de",width = 8, height = 1,command=abrir_ventana_info,fg = '#FFFFFF', bg = '#276CDE', overrelief = "sunken")
about_boton.place(x=1070,y=638)

#Botón para estadísticas
boton_cargar = tk.Button(MainWindow, text="Estadísticas", width = 8, height = 1, command=estadisticas, fg = '#FFFFFF', bg = '#276CDE', overrelief = "sunken")
boton_cargar.place(x=1150,y=608)

#Imagen GEPAR
gepar = ImageTk.PhotoImage(file="gepar.png")
label_gepar = tk.Label(image=gepar)
label_gepar.place(x = 38,y = 700)

#Imagen UDEA
udea = ImageTk.PhotoImage(file="udea.png")
label_udea = tk.Label(image=udea)
label_udea.place(x = 138,y = 700)

#Imagen UDEA
GDM = ImageTk.PhotoImage(file="GDM_logo.jpg")
label_gdm = tk.Label(image=GDM)
label_gdm.place(x = 228,y = 700)

#icono GEPAR
#icono = MainWindow.iconbitmap("gepar.ico")

frame.pack()


MainWindow.mainloop()