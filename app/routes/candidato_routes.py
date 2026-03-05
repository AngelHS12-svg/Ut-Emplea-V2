from flask import Blueprint, request, redirect
from app.config.database import get_connection

candidato_bp = Blueprint('candidato', __name__)

@candidato_bp.route("/registro-candidato", methods=["POST"])
def registrar_candidato():

    sexo = request.form["sexo"]
    nombre = request.form["nombre"]
    carrera = request.form["carrera"]
    egreso = request.form["egreso"]
    telefono = request.form["telefono"]
    correo = request.form["correo"]
    password = request.form["password"]

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO candidatos
    (sexo,nombre,carrera,egreso,telefono,correo,password)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(query,(sexo,nombre,carrera,egreso,telefono,correo,password))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/")