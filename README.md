# ALSOFT

Este repositorio alberga la totalidad de los documentos requeridos para la ejecución del Software ALIES (ALSOFT). Dicho software ha sido concebido con el propósito de llevar a cabo la selección de esquejes mediante la implementación de la comunicación MODBUS entre el ordenador y el PLC, estableciendo una dinámica de cliente-servidor.

Inicialmente, se requiere clonar el repositorio con el propósito de obtener todos los archivos esenciales para la posterior ejecución. Este procedimiento puede ser llevado a cabo mediante el siguiente comando:

`git clone https://github.com/luistorrest/ALSOFT.git`

# ALSOFT: SOFTWARE PARA ALIES ALIMENTADORA DE SELECCIONADORA DE ESQUEJES

ALSOFT es un sistema de clasificación automatizada de esquejes basado en técnicas de visión artificial. Este software está diseñado para procesar imágenes de esquejes, extraer características clave, y clasificarlos. El sistema está integrado con un PLC para controlar el proceso de clasificación en tiempo real.

## Requisitos del Sistema

- **Python 3.8 o superior**
- **Librerías Requeridas**:
  - `opencv-python` (para procesamiento de imágenes)
  - `numpy` (para operaciones matemáticas)
  - `tkinter` (para la interfaz gráfica)
  - `matplotlib` (para visualización de datos)
  - `pandas` (para manejo de datos en CSV)
  - `Pillow` (para manejo de imágenes en la interfaz gráfica)
# Instalación

1. Clona este repositorio:
```
git clone https://github.com/tu_usuario/ALSOFT.git
cd ALSOFT
```
2. Crear un entorno virtual (Recomendado):
```
python -m venv venv
source venv/bin/activate  # En Linux/Mac
venv\Scripts\activate     # En Windows
```
3. Instalar dependencias
```
pip install -r requirements.txt
```
4. Ejecutar programa
 ```
python ALSOFT.py
 ```   

# Estructura:
```  
ALSOFT/
│
├── main.py                # Script principal del programa
├── modules/               # Módulos adicionales
│   └── imageProcess.py    # Funciones de procesamiento de imágenes
├── Assets/                # Recursos como imágenes y logos
│   └── Images/
│       ├── gepar.png
│       ├── udea.png
│       └── GDM_logo.jpg
├── TipoEsquejes.json      # Archivo JSON con parámetros de esquejes
├── requirements.txt       # Lista de dependencias
└── README.md              # Este archivo
```  

## Registro de Software
Este Software está registrado en la Dirección Nacional de Derecho de Autor / Ministerio de Interior de Colombia con el número de registro 13-101-238 el 06 de diciembre del 2024
# Authores

- [@luistorrset](https://www.linkedin.com/in/luisftorrest/)
- [@David Fernandez ]()


