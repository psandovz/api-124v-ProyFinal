from typing import Optional

from fastapi import FastAPI, Depends, Form, HTTPException, Path, Query, Header, Response, Cookie
from pymongo import MongoClient
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId
import json

app = FastAPI()

def get_db():
    client = MongoClient("mongodb://localhost:27017/")
    try:
        db = client["fastapi"]
        yield db
    except Exception as e:
        print(str(e))
    finally:
        client.close()

class PostCreate(BaseModel):
    nombre: str = Form(..., min_length=1, max_length=20),
    apellido: str = Form(..., min_length=1, max_length=25),
    aprobado: bool = Form(...),
    nota: int = Form(..., ge=0, le=20),

@app.get("/")
def index():
    return {"message": "Bienvenidos al examen Final.....!"}


@app.get("/posts")
def buscar_estudiante(
   
    db = Depends(get_db)
):
    
    
    docs = db["estudiante"].find()

    posts = []
    for post in docs:
        posts.append({
            "id": str(post["_id"]),
            "nombre": post["nombre"],
            "apellido": post["apellido"],
            "aprobado": post["aprobado"],
            "nota": post["nota"],
            "fecha": post.get("fecha", datetime.now()).isoformat()
        })
    return {"Total": len(posts) ,"Estudiantes": posts}

@app.get("/post/{est_id}")
def obtener_Estudiante(
    est_id: str = Path(...,
                       title="ID del Estudiante",
                       description="ID del Estudiante a obtener",
                       min_length=24,
                       max_length=24,
                       regex="^[0-9a-fA-F]{24}$"),
    db = Depends(get_db)
):
    try:
        post = db["estudiante"].find_one({"_id": ObjectId(est_id)})

        if not post:
            return {"error": "Estudiante no encontrado"}

        return {
            "id": str(post["_id"]),
            "nombre": post["nombre"],
            "apellido": post["apellido"],
            "aprobado": post["aprobado"],
            "nota": post["nota"],
            "fecha": post["fecha"].isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/post/create-form-data")
def create_one_post_form_data(
    nombre: str = Form(..., min_length=1, max_length=20),
    apellido: str = Form(..., min_length=1, max_length=25),
    aprobado: bool = Form(...),
    nota: int = Form(..., ge=0, le=20),
    
    db=Depends(get_db)
):
    new_post = {
        "nombre": nombre,
        "apellido": apellido,
        "aprobado": aprobado,
        "nota": nota,
        "fecha": datetime.now()
    }
    result = db["estudiante"].insert_one(new_post)
    created_post = db["estudiante"].find_one({"_id": result.inserted_id})

    return {
        "id": str(created_post["_id"]),
        "nombre": created_post["nombre"],
        "apellido": created_post["apellido"],
        "aprobado": created_post["aprobado"],
        "nota": created_post["nota"],
        "fecha": created_post["fecha"].isoformat()
    }

@app.put("/post/edit/{est_id}")
def edit_one_post(est_id: str, post: PostCreate, db=Depends(get_db)):
    existing_post = db["estudiante"].find_one({"_id": ObjectId(est_id)})
    if not existing_post:
        return {"error": "No existing post"}
    updated_data = {
        "nombre": post.nombre,
        "apellido": post.apellido,
        "aprobado": post.aprobado,
        "nota": post.nota
    }
    filtro = {"_id": ObjectId(est_id)}
    _set = {"$set": updated_data}
    db["estudiante"].update_one(filtro, _set)

    updated_post = db["estudiante"].find_one({"_id": ObjectId(est_id)})
    return {
        "id": str(updated_post["_id"]),
        "nombre": updated_post["nombre"],
        "apellido": updated_post["apellido"],
        "aprobado": updated_post["aprobado"],
        "nota": updated_post["nota"],
        "fecha": updated_post.get("fecha", datetime.now()).isoformat()
    }

@app.delete("/post/delete/{est_id}")
def delete_one_post(est_id: str, db=Depends(get_db)):
    post = db["estudiante"].find_one({"_id": ObjectId(est_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Estudiante not found")
    
    db["estudiante"].delete_one({"_id": ObjectId(est_id)})
    return {"message": "Estudiante Eliminado Satisfactoriamente"}



