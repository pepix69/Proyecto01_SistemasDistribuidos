# Proyecto01_SistemasDistribuidos

Paso 1:
Base de datos:

Es necesario tener instalado MongoDB Database tools: https://www.mongodb.com/docs/database-tools/installation/installation/
1. Entrar a la consola de comandos
2. Ejecutar el comando: mongorestore --db proyecto_l ruta_de_la_carpeta_de_la_base,
Es necesario sustituir ruta_de_la_carpeta_de_la_base por la ruta donde se encuentra
la carpeta proyecto_l que fue proporcionada, esta ruta entre comillas dobles.
3. Verificar en el MongoDB Compass si se encuentra la base de datos. (Hay registros previos para verificar que fue cargado correctamente)
![image](https://github.com/user-attachments/assets/d3aae2b1-281b-4935-a1c7-05d0c592a52a)




Paso 2:
Main:

Es necesario tener inataladas las dependencias fastapi, pydantic, motor, bson, datetime, typing,

Ejecución en Visual Studio Code:
1. Abrir la carpeta donde se encuentre el archivo main.py, con Visual Studio Code. Nota importante: Se puede modificar el nombre del bucket en la primera linea si así se desea.
2. Abrir una nueva terminal
3. Ejecutar el comando: fastapi dev main.py
4. Acceder a http://127.0.0.1:8000/docs para verificar el funcionamiento

Para probar el funcionamiento, se ejecutó el archivo main con el siguiente nombre de bucket: sistemas-distribuidos-proyecto-01 (Asegurarse de que sea un nombre único)
![image](https://github.com/user-attachments/assets/e652e6a0-0568-410f-8d45-c9875f06d6b0)

Creación del bucket en S3
![image](https://github.com/user-attachments/assets/caad1d4f-3924-4744-af74-cb0a67331280)


A continuación se muestra algunas pruebas de la API

1. GetAutor
   
![image](https://github.com/user-attachments/assets/54a9d7e6-29b0-41ba-bc49-704a37310f7e)


3. Eliminar lector (David Alba)
   
![image](https://github.com/user-attachments/assets/a07950d5-c677-4e52-9a52-ab867a0e4ce1)

![image](https://github.com/user-attachments/assets/744ba27b-b2ff-4747-ba82-2d301d37de53)

![image](https://github.com/user-attachments/assets/ae62a623-c2d2-498e-a9b3-6ad9b549ca7b)


3. Crear bibliotecaria (Estefania Corrales)
   
![image](https://github.com/user-attachments/assets/f83c305f-9bac-466c-90b3-0ef07098aeb4)

![image](https://github.com/user-attachments/assets/7c97a107-df2e-4c16-8f77-671e639517f7)

