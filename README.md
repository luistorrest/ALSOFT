# ALSOFT

Este repositorio alberga la totalidad de los documentos requeridos para la ejecución del Software ALIES (ALSOFT). Dicho software ha sido concebido con el propósito de llevar a cabo la selección de esquejes mediante la implementación de la comunicación MODBUS entre el ordenador y el PLC, estableciendo una dinámica de cliente-servidor.

Inicialmente, se requiere clonar el repositorio con el propósito de obtener todos los archivos esenciales para la posterior ejecución. Este procedimiento puede ser llevado a cabo mediante el siguiente comando:

`git clone https://github.com/luistorrest/ALSOFT.git`

Con el objetivo de proceder a la instalación integral de las bibliotecas indispensables y así permitir la ejecución sin contratiempos del programa en cuestión, resulta imperativo generar un entorno virtual de Python. A tal efecto, se sugiere atender las etapas que se detallan a continuación en la terminal:

- Dirigirse al directorio de elección para la creación del entorno virtual.

- Ejecutar el comando:

`python -m venv plc_img`.

- Acceder a la carpeta correspondiente mediante la ruta:

 `plc_img\Scripts`.

- Activar el entorno virtual por medio del comando

`activate`.


Una vez el entorno virtual de Python esté activado, se procede a la instalación de las bibliotecas y dependencias indispensables para la ejecución del programa, mediante el empleo del siguiente comando:

`pip install -r requirements.txt`

Prosiguiendo con el proceso, se ejecuta el archivo de Python denominado "pruebaPLC_IMG_SOCAES_.py" a través del siguiente comando:


`python .\pruebaPLC_IMG_SOCAES_.py
`

Es de suma importancia destacar que para garantizar el correcto funcionamiento del programa, es imperativo mantener una conexión activa entre el PLC y el equipo informático. Esto se debe a que la ejecución de las acciones planificadas se fundamenta en el establecimiento de una conexión efectiva entre ambos dispositivos. Por lo tanto, se recomienda asegurarse de que el PLC esté debidamente conectado al computador antes de proceder con la ejecución del programa.

