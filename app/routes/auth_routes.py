from flask import Blueprint, request, jsonify
from app.config.database import get_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT id_usuario, nombre, rol
    FROM usuarios
    WHERE username = %s AND password = %s
    """

    cursor.execute(query,(username,password))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        return jsonify({
            "mensaje":"Login correcto",
            "usuario":user[1],
            "rol":user[2]
        })
    else:
        return jsonify({"mensaje":"Credenciales incorrectas"}),401