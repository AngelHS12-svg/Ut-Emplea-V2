from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__, template_folder="app/Views", static_folder="public")
app.secret_key = "secret_key_prueba"  # necesario para flash messages

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "home"

class User(UserMixin):
    def __init__(self, id_usuario, correo, id_rol, nombre_rol):
        self.id = id_usuario
        self.correo = correo
        self.id_rol = id_rol
        self.rol = nombre_rol

@login_manager.user_loader
def load_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.id_usuario, u.correo, u.id_rol, r.nombre 
        FROM usuarios u 
        JOIN roles r ON u.id_rol = r.id_rol 
        WHERE u.id_usuario = %s
    """, (user_id,))
    user_data = cur.fetchone()
    cur.close()
    conn.close()
    if user_data:
        return User(user_data[0], user_data[1], user_data[2], user_data[3])
    return None

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="bolsa_trabajo_uto",
        user="postgres",
        password="angel123",
        port="5432"
    )

# ================= HOME =================
@app.route("/")
def home():
    return render_template("home/index.html")


# ================= LOGIN =================
@app.route("/login")
def login():
    return render_template("home/index.html")


# ================= ADMIN =================
@app.route("/admin")
@login_required
def admin():
    if current_user.rol != "Administrador":
        flash("Acceso denegado: Se requiere rol de Administrador")
        return redirect(url_for("home"))
    return render_template("admi/index.html")

# ADMIN - Módulo
@app.route("/admin/inicio")
@login_required
def admin_inicio():
    if current_user.rol != "Administrador":
        flash("Acceso denegado")
        return redirect(url_for("home"))
    return render_template("admi/inicio.html")  # tu panel principal

@app.route("/admin/validar-empresa")
@login_required
def admin_validar_empresa():
    if current_user.rol != "Administrador":
        flash("Acceso denegado")
        return redirect(url_for("home"))
    return render_template("admi/validar_empresa.html")

@app.route("/admin/consultar-empresas")
@login_required
def admin_consultar_empresas():
    if current_user.rol != "Administrador": return redirect(url_for("home"))
    return render_template("admi/consultar_empresas.html")

@app.route("/admin/validar-candidato")
@login_required
def admin_validar_candidato():
    if current_user.rol != "Administrador": return redirect(url_for("home"))
    return render_template("admi/validar_candidato.html")

@app.route("/admin/consultar-candidatos")
@login_required
def admin_consultar_candidatos():
    if current_user.rol != "Administrador": return redirect(url_for("home"))
    return render_template("admi/consultar_candidatos.html")

@app.route("/admin/vacantes")
@login_required
def admin_vacantes():
    if current_user.rol != "Administrador": return redirect(url_for("home"))
    return render_template("admi/vacantes.html")

@app.route("/admin/seguimiento")
@login_required
def admin_seguimiento():
    if current_user.rol != "Administrador": return redirect(url_for("home"))
    return render_template("admi/seguimiento.html")

@app.route("/admin/reportes")
@login_required
def admin_reportes():
    if current_user.rol != "Administrador": return redirect(url_for("home"))
    return render_template("admi/reportes.html")

# ================= EMPRESA =================
@app.route('/empresa')
@login_required
def empresa():
    if current_user.rol != "Empresa":
        flash("Acceso denegado: Se requiere rol de Empresa")
        return redirect(url_for("home"))
    return render_template('empresa/empresa-inicio.html')

@app.route("/registro-empresa", methods=["GET", "POST"])
def registro_empresa():
    if request.method == "POST":
        nombre_empresa = request.form.get("empresa")
        giro = request.form.get("giro")
        tipo_empresa = request.form.get("tipo_empresa")
        telefono = request.form.get("telefono")
        direccion = request.form.get("direccion")
        correo = request.form.get("correo")
        password = request.form.get("password")
        responsable_rrhh = request.form.get("responsable_rrhh")
        telefono_rrhh = request.form.get("telefono_rrhh")
        correo_rrhh = request.form.get("correo_rrhh")

        hashed_password = generate_password_hash(password)

        conn = get_connection()
        cur = conn.cursor()

        try:
            # 1. Insertar en usuarios
            cur.execute("""
                INSERT INTO usuarios (id_rol, correo, password) 
                VALUES (2, %s, %s) RETURNING id_usuario
            """, (correo, hashed_password))
            id_usuario = cur.fetchone()[0]

            # 2. Insertar en empresas
            cur.execute("""
                INSERT INTO empresas (id_usuario, nombre, giro, tipo_empresa, telefono) 
                VALUES (%s, %s, %s, %s, %s) RETURNING id_empresa
            """, (id_usuario, nombre_empresa, giro, tipo_empresa, telefono))
            id_empresa = cur.fetchone()[0]

            # 3. Insertar en direcciones_empresa
            cur.execute("""
                INSERT INTO direcciones_empresa (id_empresa, calle) 
                VALUES (%s, %s)
            """, (id_empresa, direccion))

            # 4. Insertar en recursos_humanos
            cur.execute("""
                INSERT INTO recursos_humanos (id_empresa, nombre, telefono, correo) 
                VALUES (%s, %s, %s, %s)
            """, (id_empresa, responsable_rrhh, telefono_rrhh, correo_rrhh))

            conn.commit()
            flash("Empresa registrada exitosamente. Ahora puede iniciar sesión.")
            return redirect(url_for("home"))
        except Exception as e:
            conn.rollback()
            flash(f"Error al registrar: {str(e)}")
            return redirect(url_for("registro_empresa"))
        finally:
            cur.close()
            conn.close()

    return render_template("empresa/registro-empresa.html")


@app.route('/empresa/publicar')
@login_required
def empresa_publicar():
    if current_user.rol != "Empresa":
        return redirect(url_for("home"))
    return render_template('empresa/empresa-publicar.html')


@app.route('/empresa/consultar')
@login_required
def empresa_consultar():
    if current_user.rol != "Empresa":
        return redirect(url_for("home"))
    return render_template('empresa/empresa-consultar.html')


@app.route('/empresa/estadisticas')
@login_required
def empresa_estadisticas():
    if current_user.rol != "Empresa": return redirect(url_for("home"))
    return render_template('empresa/empresa-estadisticas.html')


@app.route('/empresa/perfil')
@login_required
def empresa_perfil():
    if current_user.rol != "Empresa": return redirect(url_for("home"))
    return render_template('empresa/empresa-perfil.html')

# ================= CANDIDATO =================
@app.route("/registro-candidato", methods=["GET", "POST"])
def registro_candidato():
    if request.method == "POST":
        sexo = request.form.get("sexo")
        nombre = request.form.get("nombre")
        carrera_nombre = request.form.get("carrera")
        anio_egreso = request.form.get("egreso")
        telefono = request.form.get("telefono")
        correo = request.form.get("correo")
        password = request.form.get("password")

        hashed_password = generate_password_hash(password)

        conn = get_connection()
        cur = conn.cursor()

        try:
            # Primero obtener el id_carrera si existe, o usar null
            cur.execute("SELECT id_carrera FROM carreras WHERE nombre = %s", (carrera_nombre,))
            carrera_data = cur.fetchone()
            id_carrera = carrera_data[0] if carrera_data else None

            # 1. Insertar en usuarios
            cur.execute("""
                INSERT INTO usuarios (id_rol, correo, password) 
                VALUES (3, %s, %s) RETURNING id_usuario
            """, (correo, hashed_password))
            id_usuario = cur.fetchone()[0]

            # 2. Insertar en candidatos
            cur.execute("""
                INSERT INTO candidatos (id_usuario, nombre, sexo, telefono, id_carrera, anio_egreso) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_usuario, nombre, sexo, telefono, id_carrera, anio_egreso))

            conn.commit()
            flash("Registro exitoso. Bienvenido a UT Oriental Emplea.")
            return redirect(url_for("home"))
        except Exception as e:
            conn.rollback()
            flash(f"Error al registrar: {str(e)}")
            return redirect(url_for("registro_candidato"))
        finally:
            cur.close()
            conn.close()

    return render_template("vacantes/registro-vacante.html")


@app.route("/candidato-dashboard")
@login_required
def candidato_dashboard():
    if current_user.rol != "Candidato":
        flash("Acceso denegado")
        return redirect(url_for("home"))
    return render_template("vacantes/panel-candidato.html")

@app.route("/candidato/buscar")
@login_required
def candidato_buscar():
    if current_user.rol != "Candidato": return redirect(url_for("home"))
    return render_template("vacantes/buscar-vacantes.html")

@app.route("/candidato/ver")
@login_required
def candidato_ver():
    if current_user.rol != "Candidato": return redirect(url_for("home"))
    return render_template("vacantes/ver-vacantes.html")

@app.route("/candidato/postulaciones")
@login_required
def candidato_postulaciones():
    if current_user.rol != "Candidato": return redirect(url_for("home"))
    return render_template("vacantes/mis-postulaciones.html")

@app.route("/candidato/estado-postulaciones")
@login_required
def candidato_estado_postulaciones():
    if current_user.rol != "Candidato": return redirect(url_for("home"))
    return render_template("vacantes/estado-postulaciones.html")

@app.route("/candidato/perfil")
@login_required
def candidato_perfil():
    if current_user.rol != "Candidato": return redirect(url_for("home"))
    return render_template("vacantes/perfil-candidato.html")

@app.route("/candidato/detalle-vacante")
@login_required
def candidato_detalle_vacante():
    if current_user.rol != "Candidato": return redirect(url_for("home"))
    return render_template("vacantes/detalle-vacante.html")

@app.route("/auth/login", methods=["POST"])
def auth_login():
    correo = request.form.get("correo")
    password = request.form.get("password")
    rol_seleccionado = request.form.get("rol")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT u.id_usuario, u.correo, u.password, r.nombre AS rol, u.id_rol
        FROM usuarios u
        JOIN roles r ON u.id_rol = r.id_rol
        WHERE u.correo = %s
    """, (correo,))

    user_data = cur.fetchone()
    cur.close()
    conn.close()

    if user_data:
        id_usuario, user_correo, hashed_password, rol_real, id_rol = user_data
        
        if check_password_hash(hashed_password, password):
            # Verificar rol coincide con selección del modal
            if (rol_seleccionado == "admin" and rol_real == "Administrador") or \
               (rol_seleccionado == "empresa" and rol_real == "Empresa") or \
               (rol_seleccionado == "candidato" and rol_real == "Candidato"):
                
                user_obj = User(id_usuario, user_correo, id_rol, rol_real)
                login_user(user_obj)
                
                if rol_real == "Administrador":
                    return redirect(url_for("admin"))
                elif rol_real == "Empresa":
                    return redirect(url_for("empresa"))
                else:
                    return redirect(url_for("candidato_dashboard"))
            else:
                flash("El rol seleccionado no coincide con su cuenta.")
                return redirect(url_for("home"))
        else:
            flash("Contraseña incorrecta.")
            return redirect(url_for("home"))
    else:
        flash("El correo no está registrado.")
        return redirect(url_for("home"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.")
    return redirect(url_for("home"))

# ================= MAIN =================
if __name__ == "__main__":
    app.run(debug=True)