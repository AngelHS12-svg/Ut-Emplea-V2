from flask import Flask, render_template,  request, redirect, url_for, flash
import psycopg2

app = Flask(__name__, template_folder="app/Views", static_folder="public")
app.secret_key = "secret_key_prueba"  # necesario para flash messages

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
def admin():
    return render_template("admi/index.html")

# ADMIN - Módulo
@app.route("/admin/inicio")
def admin_inicio():
    return render_template("admi/inicio.html")  # tu panel principal

@app.route("/admin/validar-empresa")
def admin_validar_empresa():
    return render_template("admi/validar_empresa.html")

@app.route("/admin/consultar-empresas")
def admin_consultar_empresas():
    return render_template("admi/consultar_empresas.html")

@app.route("/admin/validar-candidato")
def admin_validar_candidato():
    return render_template("admi/validar_candidato.html")

@app.route("/admin/consultar-candidatos")
def admin_consultar_candidatos():
    return render_template("admi/consultar_candidatos.html")

@app.route("/admin/vacantes")
def admin_vacantes():
    return render_template("admi/vacantes.html")

@app.route("/admin/seguimiento")
def admin_seguimiento():
    return render_template("admi/seguimiento.html")

@app.route("/admin/reportes")
def admin_reportes():
    return render_template("admi/reportes.html")

# ================= EMPRESA =================
@app.route('/empresa')
def empresa():
    return render_template('empresa/empresa-inicio.html')

@app.route("/registro-empresa")
def registro_empresa():
    return render_template("empresa/registro-empresa.html")


@app.route('/empresa/publicar')
def empresa_publicar():
    return render_template('empresa/empresa-publicar.html')


@app.route('/empresa/consultar')
def empresa_consultar():
    return render_template('empresa/empresa-consultar.html')


@app.route('/empresa/estadisticas')
def empresa_estadisticas():
    return render_template('empresa/empresa-estadisticas.html')


@app.route('/empresa/perfil')
def empresa_perfil():
    return render_template('empresa/empresa-perfil.html')

# ================= CANDIDATO =================
@app.route("/registro-candidato")
def registro_candidato():
    return render_template("vacantes/registro-vacante.html")


@app.route("/candidato-dashboard")
def candidato_dashboard():
    return render_template("vacantes/panel-candidato.html")

@app.route("/auth/login", methods=["POST"])
def auth_login():
    correo = request.form.get("correo")
    password = request.form.get("password")
    rol_seleccionado = request.form.get("rol")  # <-- nuevo

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT u.id_usuario, u.correo, u.password, r.nombre AS rol
        FROM usuarios u
        JOIN roles r ON u.id_rol = r.id_rol
        WHERE u.correo = %s AND u.password = %s
    """, (correo, password))

    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        rol_real = user[3]  # rol real en la BD

        # Comparar con rol seleccionado
        if rol_seleccionado == "admin" and rol_real == "Administrador":
            return redirect(url_for("admin"))
        elif rol_seleccionado == "empresa" and rol_real == "Empresa":
            return redirect(url_for("empresa"))
        elif rol_seleccionado == "candidato" and rol_real == "Candidato":
            return redirect(url_for("candidato_dashboard"))
        else:
            flash("El rol seleccionado no coincide con el usuario")
            return redirect(url_for("home"))
    else:
        flash("Correo o contraseña incorrectos")
        return redirect(url_for("home"))

# ================= MAIN =================
if __name__ == "__main__":
    app.run(debug=True)