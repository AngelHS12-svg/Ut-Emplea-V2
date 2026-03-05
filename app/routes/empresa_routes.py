from flask import Blueprint, request, redirect
from app.config.database import get_connection

empresa_bp = Blueprint('empresa', __name__)

@empresa_bp.route("/registro-empresa", methods=["POST"])
def registrar_empresa():

    empresa = request.form["empresa"]
    giro = request.form["giro"]
    tipo_empresa = request.form["tipo_empresa"]
    telefono = request.form["telefono"]
    direccion = request.form["direccion"]
    correo = request.form["correo"]
    password = request.form["password"]
    responsable = request.form["responsable_rrhh"]
    telefono_rrhh = request.form["telefono_rrhh"]
    correo_rrhh = request.form["correo_rrhh"]

    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO empresas
    (empresa,giro,tipo_empresa,telefono,direccion,correo,password,responsable_rrhh,telefono_rrhh,correo_rrhh)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(query,(
        empresa,
        giro,
        tipo_empresa,
        telefono,
        direccion,
        correo,
        password,
        responsable,
        telefono_rrhh,
        correo_rrhh
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return redirect("/")