from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.config.database import get_connection
from werkzeug.security import generate_password_hash
from datetime import datetime

empresa_bp = Blueprint('empresa', __name__)

# ================= DASHBOARD =================
@empresa_bp.route("/")
@login_required
def inicio():
    if current_user.rol != "Empresa":
        flash("Acceso denegado")
        return redirect(url_for("home"))
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Obtener ID de empresa
    cur.execute("SELECT id_empresa FROM empresas WHERE id_usuario = %s", (current_user.id,))
    empresa_data = cur.fetchone()
    
    stats = {'vacantes': 0, 'postulaciones': 0}
    if empresa_data:
        id_empresa = empresa_data[0]
        # Contador de vacantes
        cur.execute("SELECT COUNT(*) FROM vacantes WHERE id_empresa = %s", (id_empresa,))
        stats['vacantes'] = cur.fetchone()[0]
        
        # Contador de postulaciones
        cur.execute("""
            SELECT COUNT(p.id_postulacion) 
            FROM postulaciones p
            JOIN vacantes v ON p.id_vacante = v.id_vacante
            WHERE v.id_empresa = %s
        """, (id_empresa,))
        stats['postulaciones'] = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return render_template('empresa/empresa-inicio.html', stats=stats)

# ================= PUBLICAR VACANTE =================
@empresa_bp.route("/publicar", methods=["GET", "POST"])
@login_required
def publicar():
    if current_user.rol != "Empresa": return redirect(url_for("home"))
    
    if request.method == "POST":
        titulo = request.form.get("titulo")
        descripcion = request.form.get("descripcion")
        salario = request.form.get("salario")
        modalidad = request.form.get("modalidad")
        horario = request.form.get("horario")
        lugar = request.form.get("lugar")
        fecha_vencimiento = request.form.get("fecha_vencimiento")
        
        # Requisitos
        escolaridad = request.form.get("escolaridad")
        experiencia = request.form.get("experiencia")
        conocimientos = request.form.get("conocimientos")
        perfil = request.form.get("perfil")
        num_vacantes = request.form.get("num_vacantes")

        conn = get_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("SELECT id_empresa FROM empresas WHERE id_usuario = %s", (current_user.id,))
            id_empresa = cur.fetchone()[0]
            
            # Insertar vacante
            cur.execute("""
                INSERT INTO vacantes (id_empresa, titulo, descripcion, salario, modalidad, horario, lugar_trabajo, fecha_vencimiento, num_vacantes, perfil)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id_vacante
            """, (id_empresa, titulo, descripcion, float(salario) if salario and salario.replace('.', '', 1).isdigit() else None, modalidad, horario, lugar, fecha_vencimiento, int(num_vacantes) if num_vacantes else 1, perfil))
            
            id_vacante = cur.fetchone()[0]
            
            # Insertar requisitos
            cur.execute("""
                INSERT INTO requisitos_vacante (id_vacante, escolaridad, experiencia, descripcion)
                VALUES (%s, %s, %s, %s)
            """, (id_vacante, escolaridad, experiencia, conocimientos))
            
            conn.commit()
            flash("Vacante publicada exitosamente")
            return redirect(url_for("empresa.inicio"))
        except Exception as e:
            conn.rollback()
            flash(f"Error al publicar: {str(e)}")
        finally:
            cur.close()
            conn.close()

    return render_template('empresa/empresa-publicar.html')

# ================= CONSULTAR VACANTES =================
@empresa_bp.route("/consultar")
@login_required
def consultar():
    if current_user.rol != "Empresa": return redirect(url_for("home"))
    
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id_empresa FROM empresas WHERE id_usuario = %s", (current_user.id,))
    id_empresa_row = cur.fetchone()
    
    if not id_empresa_row:
        cur.close()
        conn.close()
        return redirect(url_for("home"))
    
    id_empresa = id_empresa_row[0]
    
    cur.execute("""
        SELECT v.id_vacante, v.titulo, v.fecha_publicacion, v.estatus, 
        (SELECT COUNT(*) FROM postulaciones p WHERE p.id_vacante = v.id_vacante) as num_postulados
        FROM vacantes v
        WHERE v.id_empresa = %s
        ORDER BY v.fecha_publicacion DESC
    """, (id_empresa,))
    
    vacantes = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template('empresa/empresa-consultar.html', vacantes=vacantes)

# ================= PERFIL =================
@empresa_bp.route("/perfil")
@login_required
def perfil():
    if current_user.rol != "Empresa": return redirect(url_for("home"))
    
    conn = get_connection()
    # Usamos un cursor normal pero podemos mapear a dict si fuera necesario. 
    # Para mantener consistencia con el resto del archivo, usaremos el cursor por defecto.
    cur = conn.cursor()
    
    cur.execute("""
        SELECT e.nombre, e.giro, e.tipo_empresa, e.telefono, d.calle, 
               rh.nombre as rh_nombre, rh.telefono as rh_telefono, rh.correo as rh_correo
        FROM empresas e
        LEFT JOIN direcciones_empresa d ON e.id_empresa = d.id_empresa
        LEFT JOIN recursos_humanos rh ON e.id_empresa = rh.id_empresa
        WHERE e.id_usuario = %s
    """, (current_user.id,))
    
    empresa = cur.fetchone()
    cur.close()
    conn.close()
    
    return render_template('empresa/empresa-perfil.html', empresa=empresa)

# ================= ESTADÍSTICAS =================
@empresa_bp.route("/estadisticas")
@login_required
def estadisticas():
    if current_user.rol != "Empresa": return redirect(url_for("home"))
    
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id_empresa FROM empresas WHERE id_usuario = %s", (current_user.id,))
    empresa_data = cur.fetchone()
    
    stats = {
        'vacantes_activas': 0, 'vacantes_inactivas': 0,
        'total_postulaciones': 0, 'en_revision': 0,
        'aceptadas': 0, 'rechazadas': 0
    }
    vacantes_detalle = []
    
    if empresa_data:
        id_empresa = empresa_data[0]
        cur.execute("SELECT COUNT(*) FROM vacantes WHERE id_empresa = %s AND estatus = 'activa'", (id_empresa,))
        stats['vacantes_activas'] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM vacantes WHERE id_empresa = %s AND estatus != 'activa'", (id_empresa,))
        stats['vacantes_inactivas'] = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(p.id_postulacion)
            FROM postulaciones p JOIN vacantes v ON p.id_vacante = v.id_vacante
            WHERE v.id_empresa = %s
        """, (id_empresa,))
        stats['total_postulaciones'] = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(p.id_postulacion)
            FROM postulaciones p JOIN vacantes v ON p.id_vacante = v.id_vacante
            WHERE v.id_empresa = %s AND p.estado = 'en revision'
        """, (id_empresa,))
        stats['en_revision'] = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(p.id_postulacion)
            FROM postulaciones p JOIN vacantes v ON p.id_vacante = v.id_vacante
            WHERE v.id_empresa = %s AND p.estado = 'aceptado'
        """, (id_empresa,))
        stats['aceptadas'] = cur.fetchone()[0]
        cur.execute("""
            SELECT COUNT(p.id_postulacion)
            FROM postulaciones p JOIN vacantes v ON p.id_vacante = v.id_vacante
            WHERE v.id_empresa = %s AND p.estado = 'rechazado'
        """, (id_empresa,))
        stats['rechazadas'] = cur.fetchone()[0]
        
        # Detalle por vacante
        cur.execute("""
            SELECT v.titulo,
                   (SELECT COUNT(*) FROM postulaciones p WHERE p.id_vacante = v.id_vacante) as total,
                   (SELECT COUNT(*) FROM postulaciones p WHERE p.id_vacante = v.id_vacante AND p.estado = 'en revision') as revision,
                   (SELECT COUNT(*) FROM postulaciones p WHERE p.id_vacante = v.id_vacante AND p.estado = 'aceptado') as aceptadas
            FROM vacantes v WHERE v.id_empresa = %s
            ORDER BY v.fecha_publicacion DESC
        """, (id_empresa,))
        vacantes_detalle = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('empresa/empresa-estadisticas.html', stats=stats, vacantes_detalle=vacantes_detalle)

# ================= REGISTRO (Mantenido por compatibilidad) =================
@empresa_bp.route("/registro-empresa", methods=["POST"])
def registrar_empresa():
    data = request.form
    hashed_password = generate_password_hash(data.get("password"))
    
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO usuarios (id_rol, correo, password) VALUES (2, %s, %s) RETURNING id_usuario", 
                   (data.get("correo"), hashed_password))
        id_usuario = cur.fetchone()[0]
        
        cur.execute("INSERT INTO empresas (id_usuario, nombre, giro, tipo_empresa, telefono) VALUES (%s, %s, %s, %s, %s) RETURNING id_empresa",
                   (id_usuario, data.get("empresa"), data.get("giro"), data.get("tipo_empresa"), data.get("telefono")))
        id_empresa = cur.fetchone()[0]
        
        cur.execute("INSERT INTO direcciones_empresa (id_empresa, calle) VALUES (%s, %s)", (id_empresa, data.get("direccion")))
        cur.execute("INSERT INTO recursos_humanos (id_empresa, nombre, telefono, correo) VALUES (%s, %s, %s, %s)",
                   (id_empresa, data.get("responsable_rrhh"), data.get("telefono_rrhh"), data.get("correo_rrhh")))
        
        conn.commit()
        flash("Registro exitoso")
        return redirect(url_for("home"))
    except Exception as e:
        conn.rollback()
        flash(f"Error: {str(e)}")
        return redirect(url_for("registro_empresa"))
    finally:
        cur.close()
        conn.close()