bucket = 'sistemas-distribuidos-proyecto-01'

# Bucket
import boto3
#Excepcion para cuando no tenemos credenciales en AWS
from botocore.exceptions import NoCredentialsError, ClientError, PartialCredentialsError

#Definir el servicio y la region de AWS
s3 = boto3.client("s3", region_name="us-east-2")

def crear_bucket(bucket):

    try:
        s3.create_bucket(Bucket = bucket, CreateBucketConfiguration ={'LocationConstraint': 'us-east-2'})
        print("Bucket creado correctamente")

    except NoCredentialsError:
        print("No se encontraron las credenciales de AWS.")
    except ClientError as e:
        print(f"Error al eliminar el bucket: {e}")

def crear_carpeta(bucket, carpeta):

    try:
        s3.put_object(Bucket = bucket, Key= carpeta)
        print("Carpeta creada correctamente")

    except NoCredentialsError:
        print("No se encontraron las credenciales de AWS.")
    except ClientError as e:
        print(f"Error al crear la carpeta: {e}")


#Subir objetos al bucket
def subir_objeto(archivo, bucket, carpeta, nombre_objeto=None):
    #Verificar si el objeto va a atnerner un nombre difeerente en el bcket
    if nombre_objeto is None:
        nombre_objeto = archivo
    
    nombre_objeto = carpeta + archivo

    #Subir el archivo al bucket
    try:
        s3.upload_file(archivo, bucket, nombre_objeto)
        print("El archivo se subio correctamente")
    #Verifica que el archivo exista localmente
    except FileNotFoundError:
        print("El archivo no se encuentra")
    except NoCredentialsError:
        print("Las credenciales de AWS no se encontraron")




def eliminar_primer_archivo(bucket, carpeta, archivo):

    ruta = carpeta + archivo

    try:
        # Eliminar el archivo más antiguo
        s3.delete_object(Bucket=bucket, Key=ruta)
        print(f'Archivo {archivo}  eliminado correctamente de {carpeta}')
    except NoCredentialsError:
        print("No se encontraron las credenciales de AWS.")
    except ClientError as e:
        print(f"Error al descargar los archivos: {e}")



def obtener_todos_los_archivos(bucket, carpeta):
    try:
        respuesta = s3.list_objects_v2(Bucket=bucket, Prefix=carpeta)
        if 'Contents' in respuesta:
            for objeto in respuesta['Contents']:
                nombre_objeto = objeto['Key']
                nombre_descarga = 'descargado_' + nombre_objeto.split('/')[-1]
                s3.download_file(bucket, nombre_objeto, nombre_descarga)
                print(f"Archivo {nombre_objeto} descargado como {nombre_descarga}.")
        else:
            print(f"No se encontraron archivos en la carpeta {carpeta}.")
    except NoCredentialsError:
        print("No se encontraron las credenciales de AWS.")
    except ClientError as e:
        print(f"Error al descargar los archivos: {e}")




credencial = 'credenciales/'
portada = 'portadas/'



crear_bucket(bucket)

crear_carpeta(bucket, credencial)
crear_carpeta(bucket, portada)

subir_objeto('1984.jpg', bucket, portada)
subir_objeto('arboles_cantan.jpg', bucket, portada)
subir_objeto('cien_anos_de_soledad.jpg', bucket, portada)
subir_objeto('crimen_castigo.jpg', bucket, portada)
subir_objeto('dorian_gray.jpg', bucket, portada)
subir_objeto('dracula.jpg', bucket, portada)

subir_objeto('el_gran_gatsby.jpg', bucket, portada)
subir_objeto('el_quijote.jpg', bucket, portada)
subir_objeto('la_odisea.jpg', bucket, portada)
subir_objeto('matar_a_un_ruisenor.jpg', bucket, portada)
subir_objeto('orgullo_y_prejuicio.jpg', bucket, portada)
subir_objeto('senor_anillos.jpg', bucket, portada)

subir_objeto('alejandro_martinez.png', bucket, credencial)
subir_objeto('dalila_cardona.png', bucket, credencial)
subir_objeto('inosuli_campos.png', bucket, credencial)
subir_objeto('jose_montoya.png', bucket, credencial)
subir_objeto('credencial_lector_1.png', bucket, credencial)

subir_objeto('maria_garcia.png', bucket, credencial)
subir_objeto('refugio_salinas.png', bucket, credencial)
subir_objeto('rodrigo_olmos.png', bucket, credencial)
subir_objeto('yave_vargas.png', bucket, credencial)
subir_objeto('credencial_lector_2.png', bucket, credencial)
























#Crear Apis y manejar exepciones
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
#importar paquete para crear la estructura de los datos
from pydantic import BaseModel
#Conexion con mongo db
from motor import motor_asyncio
from bson import ObjectId
from datetime import datetime, timedelta
from typing import List, Optional
import os
#Confgurar la conexion con mongo db
#ubicacion de la conexion de mongo db
MONGO_URI = "mongodb://localhost:27017/"
#ejecutarel clinte de bases de datos que es motor
cliente = motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = cliente["proyecto_l"]
autores = db["autor"]
bibliotecarios = db["bibliotecario"]
lectores = db["lector"]
libros = db["libro"]
prestamos = db["prestamo"]
contadores = db["contadores"]
#Crear objeto para interactuar con la API
app = FastAPI()

class Autor(BaseModel):
    id: Optional[int] = None
    nombre: str
    apellido: str
    biografia: str

class Bibliotecario(BaseModel):
    id: Optional[int] = None
    nombre: str
    apellido: str
    correo: str

class Lector(BaseModel):
    id: Optional[int] = None
    nombre: str
    apellido: str
    correo: str

class Libro(BaseModel):
    id: Optional[int] = None
    titulo: str
    autor_id: int
    descripcion: str
    imagen_portada: str
    inventario: bool

class Prestamo(BaseModel):
    id: Optional[int] = None
    lector_id: int
    libro_id: int
    fecha_prestamo: datetime
    fecha_devolucion: Optional[datetime] = None
    bibliotecario_id: int
    foto_credencial: str



async def init_db():
    """Inicializa los contadores si no existen"""
    colecciones = ["autores", "bibliotecario", "lector", "libro", "prestamo"]
    for coleccion in colecciones:
        await contadores.update_one(
            {"_id": coleccion},
            {"$setOnInsert": {"sequence_value": 0}},
            upsert=True
        )

@app.on_event("startup")
async def startup_event():
    """Se ejecuta cuando inicia la aplicación"""
    await init_db()
    print("Base de datos inicializada")

async def obtener_siguiente_id(coleccion: str) -> int:
    """
    Obtiene el siguiente ID disponible para una colección específica
    usando un sistema de contadores en MongoDB
    """
    resultado = await contadores.find_one_and_update(
        {"_id": coleccion},
        {"$inc": {"sequence_value": 1}},
        upsert=True,
        return_document=True
    )
    return resultado["sequence_value"]


def subir_imagen(archivo: UploadFile, bucket: str, carpeta: str, nombre_objeto: str=None):
    if archivo is None:
        return{"error": "No se recibio un archivo"}


    if nombre_objeto is None:
        nombre_objeto = archivo.filename

    nombre_objeto = os.path.join(carpeta, nombre_objeto)

    # Crear un archivo temporal en el sistema
    temp_file_path = f"/tmp/{archivo.filename}"

    try:
        # Usar el método de FastAPI para obtener el archivo en su forma de bytes
        with open(archivo.file.name, "wb") as buffer:
            buffer.write(archivo.file.read())
        
        s3.upload_file(archivo.file.name, bucket, nombre_objeto)
        return {"mensaje": "El archivo se subió correctamente"}
    except FileNotFoundError:
        return {"error": "El archivo no se encuentra"}
    except NoCredentialsError:
        return {"error": "Las credenciales de AWS no se encontraron"}
    except Exception as e:
        return {"error": str(e)}
    finally: 
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


# Endpoint para subir imagen de libro
@app.post("/imagen/libro/")
async def subir_imagen_libro(file: UploadFile = File(...)):
    response = subir_imagen(file, bucket, portada) 
    return JSONResponse(content=response)

# Endpoint para subir la credencial del lector
@app.post("/imagen/credencial/")
async def subir_credencial_lector(file: UploadFile = File(...)):
    response = subir_imagen(file, bucket, credencial)  
    return JSONResponse(content=response)


#CRUD Autores
@app.get("/autores/")
async def get_autor():
    #obtener de manera asincrona todos los usuarios
    resultados = dict()#todos los usuarios
    autor_ = await autores.find().to_list(None)
    #iterar todos los elemneyos de la lista users 
    for i, autor in enumerate(autor_):
        #diccionario por cada usuario
        resultados[i] = dict()
        resultados[i]["id"] = autor["id"]
        resultados[i]["nombre"] = autor["nombre"]
        resultados[i]["apellido"] = autor["apellido"]
        resultados[i]["biografia"] = autor["biografia"]
    return resultados

@app.get("/autores/{autor_id}")
async def get_autor(autor_id: int):
    # Aquí se busca el usuario y se retorna un diccionario o un objeto User
    producto = await autores.find_one({"id": autor_id})
    if producto is None:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    
    # El modelo User se usa para la respuesta
    return {
        "id" : producto["id"],
        "nombre" : producto["nombre"],
        "apellido" : producto["apellido"],
        "biografia" : producto["biografia"]
    }

@app.post("/autores/")
async def create_autor(autor: Autor):
    """
    Crea un nuevo autor con ID autogenerado
    """
    # Obtener el siguiente ID disponible
    nuevo_id = await obtener_siguiente_id("autores")
    
    # Crear el documento del autor con el ID autogenerado
    autor_dict = autor.dict(exclude_unset=True)
    autor_dict["id"] = nuevo_id
    
    # Insertar en la base de datos
    await autores.insert_one(autor_dict)
    
    # Devolver el autor creado con su ID
    return {
        "id": nuevo_id,
        "nombre": autor_dict["nombre"],
        "apellido": autor_dict["apellido"],
        "biografia": autor_dict["biografia"]
    }

@app.put("/autores/{autor_id}")
async def update_autor(autor_id: int, autor: Autor):

     # Convertir el ID a ObjectId
    #producto_id = ObjectId(producto_id)
    
    # Buscar el usuario para verificar si existe
    existing_user = await autores.find_one({"id": autor_id})
    if existing_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    update_data = {
        "nombre": autor.nombre,
        "apellido": autor.apellido,
        "biografia": autor.biografia
    }

    # Realizar la actualización
    update_result = await autores.update_one(
        {"id": autor_id},
        {"$set": update_data}  # Usa $set para actualizar los campos específicos
    )
    
     # Obtener el usuario actualizado
    updated_user = await autores.find_one({"id": autor_id})

    return {
        "id" : updated_user["id"],
        "nombre" : updated_user["nombre"],
        "apellido" : updated_user["apellido"],
        "biografia" : updated_user["biografia"]
    }

@app.delete("/autores/{producto_id}")
async def delete_autor(autor_id: int):
    # Verificar si el id proporcionado es válido
    #if not ObjectId.is_valid(producto_id):
    #    raise HTTPException(status_code=400, detail="ID no válido")

    # Convertir el id a ObjectId y buscar el usuario
    delete_result = await autores.delete_one({"id":autor_id})

    # Verificar si se eliminó algún usuario
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {"message": "Usuario eliminado correctamente"}

#CRUD bibliotecario
@app.get("/bibliotecarios/")
async def get_bibliotecario():
    resultados = dict()
    bibliotecario_ = await bibliotecarios.find().to_list(None)
    for i, bibliotecario in enumerate(bibliotecario_):
        resultados[i] = dict()
        resultados[i]["id"] = bibliotecario["id"]
        resultados[i]["nombre"] = bibliotecario["nombre"]
        resultados[i]["apellido"] = bibliotecario["apellido"]
        resultados[i]["correo"] = bibliotecario["correo"]
    return resultados

@app.get("/bibliotecarios/{bibliotecario_id}")
async def get_bibliotecario(bibliotecario_id: int):
    # Aquí se busca el bibliotecario y se retorna un diccionario
    bibli = await bibliotecarios.find_one({"id": bibliotecario_id})
    if bibli is None:
        raise HTTPException(status_code=404, detail="Bibliotecario no encontrado")
    
    # Retornar los datos del bibliotecario
    return {
        "id": bibli["id"],
        "nombre": bibli["nombre"],
        "apellido": bibli["apellido"],
        "correo": bibli["correo"]
    }
    
@app.post("/bibliotecarios/")
async def create_bibliotecario(bibliotecario: Bibliotecario):
    """
    Crea un nuevo bibliotecario con ID autogenerado
    """
    # Obtener el siguiente ID disponible
    nuevo_id = await obtener_siguiente_id("bibliotecarios")
    
    # Crear el documento del bibliotecario con el ID autogenerado
    bibliotecario_dict = bibliotecario.dict(exclude_unset=True)
    bibliotecario_dict["id"] = nuevo_id
    
    # Insertar en la base de datos
    await bibliotecarios.insert_one(bibliotecario_dict)
    
    # Devolver el bibliotecario creado con su ID
    return {
        "id": nuevo_id,
        "nombre": bibliotecario_dict["nombre"],
        "apellido": bibliotecario_dict["apellido"],
        "correo": bibliotecario_dict["correo"]
    }
    
@app.put("/bibliotecarios/{bibliotecario_id}")
async def update_bibliotecario(bibliotecario_id: int, bibliotecario: Bibliotecario):
    # Buscar el bibliotecario para verificar si existe
    existing_bibliotecario = await bibliotecarios.find_one({"id": bibliotecario_id})
    if existing_bibliotecario is None:
        raise HTTPException(status_code=404, detail="Bibliotecario no encontrado")
    
    update_data = {
        "nombre": bibliotecario.nombre,
        "apellido": bibliotecario.apellido,
        "correo": bibliotecario.correo
    }

    # Realizar la actualización
    await bibliotecarios.update_one(
        {"id": bibliotecario_id},
        {"$set": update_data}  # Usa $set para actualizar los campos específicos
    )
    
    # Obtener el bibliotecario actualizado
    updated_bibliotecario = await bibliotecarios.find_one({"id": bibliotecario_id})

    return {
        "id": updated_bibliotecario["id"],
        "nombre": updated_bibliotecario["nombre"],
        "apellido": updated_bibliotecario["apellido"],
        "correo": updated_bibliotecario["correo"]
    }    
    
@app.delete("/bibliotecarios/{bibliotecario_id}")
async def delete_bibliotecario(bibliotecario_id: int):
    # Buscar el bibliotecario y eliminarlo
    delete_result = await bibliotecarios.delete_one({"id": bibliotecario_id})

    # Verificar si se eliminó algún bibliotecario
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Bibliotecario no encontrado")

    return {"message": "Bibliotecario eliminado correctamente"}

#CRUD Lector
@app.get("/lectores/")
async def get_lector():
    resultados = dict()
    lector_ = await lectores.find().to_list(None)
    for i, lector in enumerate(lector_):
        resultados[i] = dict()
        resultados[i]["id"] = lector["id"]
        resultados[i]["nombre"] = lector["nombre"]
        resultados[i]["apellido"] = lector["apellido"]
        resultados[i]["correo"] = lector["correo"]
    return resultados

@app.get("/lectores/{lector_id}")
async def get_lector(lector_id: int):
    lector = await lectores.find_one({"id": lector_id})
    if lector is None:
        raise HTTPException(status_code=404, detail="Lector no encontrado")
    
    return {
        "id": lector["id"],
        "nombre": lector["nombre"],
        "apellido": lector["apellido"],
        "correo": lector["correo"]
    }

@app.post("/lectores/")
async def create_lectores(lector: Lector):
    # Obtener el siguiente ID disponible
    nuevo_id = await obtener_siguiente_id("lectores")
    
    # Crear el documento del autor con el ID autogenerado
    lector_dict = lector.dict(exclude_unset=True)
    lector_dict["id"] = nuevo_id
    
    # Insertar en la base de datos
    await lectores.insert_one(lector_dict)
    
    # Devolver el autor creado con su ID
    return {
        "id": nuevo_id,
        "nombre": lector_dict["nombre"],
        "apellido": lector_dict["apellido"],
        "correo": lector_dict["correo"]
    }

@app.put("/lectores/{lector_id}")
async def update_lector(lector_id: int, lector: Lector):
    existing_lector = await lectores.find_one({"id": lector_id})
    if existing_lector is None:
        raise HTTPException(status_code=404, detail="Lector no encontrado")
    
    update_data = {
        "nombre": lector.nombre,
        "apellido": lector.apellido,
        "correo": lector.correo,
    }

    await lectores.update_one(
        {"id": lector_id},
        {"$set": update_data}
    )
    
    updated_lector = await lectores.find_one({"id": lector_id})

    return {
        "id": updated_lector["id"],
        "nombre": updated_lector["nombre"],
        "apellido": updated_lector["apellido"],
        "correo": updated_lector["correo"],
    }

@app.delete("/lectores/{lector_id}")
async def delete_lector(lector_id: int):
    delete_result = await lectores.delete_one({"id": lector_id})

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Lector no encontrado")

    return {"message": "Lector eliminado correctamente"}


#CRUD Libro
@app.get("/libros/")
async def get_libro():
    resultados = dict()
    libro_ = await libros.find().to_list(None)
    for i, libro in enumerate(libro_):
        resultados[i] = dict()
        resultados[i]["id"] = libro["id"]
        resultados[i]["titulo"] = libro["titulo"]
        resultados[i]["autor_id"] = libro["autor_id"]
        resultados[i]["descripcion"] = libro["descripcion"]
        resultados[i]["imagen_portada"] = libro["imagen_portada"]
        resultados[i]["inventario"] = libro["inventario"]
    return resultados

@app.get("/libros/{libro_id}")
async def get_libro(libro_id: int):
    libro = await libros.find_one({"id": libro_id})
    if libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    return {
        "id": libro["id"],
        "titulo": libro["titulo"],
        "autor_id": libro["autor_id"],
        "descripcion": libro["descripcion"],
        "imagen_portada": libro["imagen_portada"],
        "inventario": libro["inventario"]
    }

@app.post("/libros/")
async def create_libro(libro: Libro):
    nuevo_id = await obtener_siguiente_id("libros")
    
    libro_dict = libro.dict(exclude_unset=True)
    libro_dict["id"] = nuevo_id
    
    await libros.insert_one(libro_dict)
    
    return {
        "id": nuevo_id,
        "titulo": libro_dict["titulo"],
        "autor_id": libro_dict["autor_id"],
        "descripcion": libro_dict["descripcion"],
        "imagen_portada": libro_dict["imagen_portada"],
        "inventario": libro_dict["inventario"]
    }

@app.put("/libros/{libro_id}")
async def update_libro(libro_id: int, libro: Libro):
    existing_libro = await libros.find_one({"id": libro_id})
    if existing_libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    update_data = {
        "titulo": libro.titulo,
        "autor_id": libro.autor_id,
        "descripcion": libro.descripcion,
        "imagen_portada": libro.imagen_portada,
        "inventario": libro.inventario
    }

    await libros.update_one(
        {"id": libro_id},
        {"$set": update_data}
    )
    
    updated_libro = await libros.find_one({"id": libro_id})

    return {
        "id": updated_libro["id"],
        "titulo": updated_libro["titulo"],
        "autor_id": updated_libro["autor_id"],
        "descripcion": updated_libro["descripcion"],
        "imagen_portada": updated_libro["imagen_portada"],
        "inventario": updated_libro["inventario"]
    }

@app.delete("/libros/{libro_id}")
async def delete_libro(libro_id: int):
    delete_result = await libros.delete_one({"id": libro_id})

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    return {"message": "Libro eliminado correctamente"}

#CRUD Prestamo
@app.get("/prestamos/")
async def get_prestamo():
    resultados = dict()
    prestamo_ = await prestamos.find().to_list(None)
    for i, prestamo in enumerate(prestamo_):
        resultados[i] = dict()
        resultados[i]["id"] = prestamo["id"]
        resultados[i]["lector_id"] = prestamo["lector_id"]
        resultados[i]["libro_id"] = prestamo["libro_id"]
        resultados[i]["fecha_prestamo"] = prestamo["fecha_prestamo"]
        resultados[i]["fecha_devolucion"] = prestamo["fecha_devolucion"]
        resultados[i]["bibliotecario_id"] = prestamo["bibliotecario_id"]
        resultados[i]["foto_credencial"] = prestamo["foto_credencial"]
    return resultados

@app.get("/prestamos/{prestamo_id}")
async def get_bibliotecario(prestamo_id: int):
    # Aquí se busca el bibliotecario y se retorna un diccionario
    prestamo = await prestamos.find_one({"id": prestamo_id})
    if prestamo is None:
        raise HTTPException(status_code=404, detail="Prestamo no encontrado")
    
    # Retornar los datos del bibliotecario
    return {
        "id": prestamo["id"],
        "lector_id": prestamo["lector_id"],
        "libro_id": prestamo["libro_id"],
        "fecha_prestamo": prestamo["fecha_prestamo"],
        "fecha_devolucion": prestamo["fecha_devolucion"],
        "bibliotecario_id": prestamo["bibliotecario_id"],
        "foto_credencial": prestamo["foto_credencial"]
    }
    
@app.post("/prestamos/")
async def create_prestamo(prestamo: Prestamo):
    """
    Crea un nuevo prestamo con ID autogenerado
    """
    # Obtener el siguiente ID disponible
    nuevo_id = await obtener_siguiente_id("prestamos")
    
    # Crear el documento del prestamo con el ID autogenerado
    prestamo_dict = prestamo.dict(exclude_unset=True)

    # Asignar fecha actual si no se proporcionó
    if "fecha_prestamo" not in prestamo_dict or prestamo_dict["fecha_prestamo"] is None:
        prestamo_dict["fecha_prestamo"] = datetime.utcnow()
    
    # Calcular fecha de devolución (3 días después del préstamo)
    prestamo_dict["fecha_devolucion"] = prestamo_dict["fecha_prestamo"] + timedelta(days=3)
    

    prestamo_dict["id"] = nuevo_id
    
    # Insertar en la base de datos
    await prestamos.insert_one(prestamo_dict)
    
    # Devolver el bibliotecario creado con su ID
    return {
        "id": nuevo_id,
        "lector_id": prestamo_dict["lector_id"],
        "libro_id": prestamo_dict["libro_id"],
        "fecha_prestamo": prestamo_dict["fecha_prestamo"],
        "fecha_devolucion": prestamo_dict["fecha_devolucion"],
        "bibliotecario_id": prestamo_dict["bibliotecario_id"],
        "foto_credencial": prestamo_dict["foto_credencial"]
    }
    
@app.put("/prestamos/{prestamo_id}")
async def update_prestamo(prestamo_id: int, prestamo: Prestamo):
    # Buscar el prestamo para verificar si existe
    existing_prestamo = await prestamos.find_one({"id": prestamo_id})
    if existing_prestamo is None:
        raise HTTPException(status_code=404, detail="Prestamo no encontrado")
    
    update_data = {
        "lector_id": prestamo.lector_id,
        "libro_id": prestamo.libro_id,
        "fecha_prestamo": prestamo.fecha_prestamo,
        "fecha_devolucion": prestamo.fecha_devolucion,
        "bibliotecario_id": prestamo.bibliotecario_id,
        "foto_credencial": prestamo.foto_credencial
    }

    # Realizar la actualización
    await prestamos.update_one(
        {"id": prestamo_id},
        {"$set": update_data}  # Usa $set para actualizar los campos específicos
    )
    
    # Obtener el prestamo actualizado
    updated_prestamo = await prestamos.find_one({"id": prestamo_id})

    return {
        "id": updated_prestamo["id"],
        "lector_id": updated_prestamo["lector_id"],
        "libro_id": updated_prestamo["libro_id"],
        "fecha_prestamo": updated_prestamo["fecha_prestamo"],
        "fecha_devolucion": updated_prestamo["fecha_devolucion"],
        "bibliotecario_id": updated_prestamo["bibliotecario_id"],
        "foto_credencial": updated_prestamo["foto_credencial"]
    }    
    
@app.delete("/prestamos/{prestamo_id}")
async def delete_prestamo(prestamo_id: int):
    # Buscar el bibliotecario y eliminarlo
    delete_result = await prestamos.delete_one({"id": prestamo_id})

    # Verificar si se eliminó algún bibliotecario
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Prestamo no encontrado")

    return {"message": "Prestamo eliminado correctamente"}


