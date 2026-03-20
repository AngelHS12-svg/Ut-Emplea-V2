"""
========================================================================
 Pruebas de Carga – Ut-Emplea-V2  (Locust)
========================================================================
Ejecutar con:
    locust -f tests/locustfile.py --host=http://localhost:5000

Luego abrir http://localhost:8089 para configurar usuarios y tasa.
========================================================================
"""
from locust import HttpUser, task, between, tag


class VisitorUser(HttpUser):
    """Simula un visitante no autenticado navegando la página pública."""
    wait_time = between(1, 3)

    @tag("public")
    @task(5)
    def home_page(self):
        """Visitar la página principal."""
        self.client.get("/", name="Home Page")

    @tag("public")
    @task(2)
    def login_page(self):
        """Visitar la página de login."""
        self.client.get("/login", name="Login Page")

    @tag("public")
    @task(1)
    def registro_empresa_form(self):
        """Cargar el formulario de registro de empresa."""
        self.client.get("/registro-empresa", name="Registro Empresa (GET)")

    @tag("public")
    @task(1)
    def registro_candidato_form(self):
        """Cargar el formulario de registro de candidato."""
        self.client.get("/registro-candidato", name="Registro Candidato (GET)")


class AdminUser(HttpUser):
    """Simula un administrador navegando el panel."""
    wait_time = between(2, 5)

    def on_start(self):
        """Iniciar sesión como administrador al comenzar."""
        with self.client.post("/auth/login", data={
            "correo": "admin@utoriental.edu.mx",
            "password": "admin123",
            "rol": "admin"
        }, name="Login Admin", catch_response=True) as response:
            if response.status_code != 200 and not (300 <= response.status_code < 400):
                response.failure(f"Login Admin falló: {response.status_code}")
                print(f"DEBUG: Login Admin falló. Status: {response.status_code}, Text: {response.text[:200]}")

    @tag("admin")
    @task(3)
    def admin_inicio(self):
        """Ver la página de inicio del admin."""
        self.client.get("/admin/inicio", name="Admin – Inicio")

    @tag("admin")
    @task(2)
    def admin_consultar_empresas(self):
        """Ver lista de empresas."""
        self.client.get("/admin/consultar-empresas", name="Admin – Consultar Empresas")

    @tag("admin")
    @task(2)
    def admin_vacantes(self):
        """Ver vacantes activas."""
        self.client.get("/admin/vacantes", name="Admin – Vacantes")

    @tag("admin")
    @task(2)
    def admin_seguimiento(self):
        """Ver seguimiento de postulaciones."""
        self.client.get("/admin/seguimiento", name="Admin – Seguimiento")

    @tag("admin")
    @task(1)
    def admin_reportes(self):
        """Ver reportes."""
        self.client.get("/admin/reportes", name="Admin – Reportes")

    @tag("admin")
    @task(1)
    def admin_validar_empresa(self):
        """Ver empresas por validar."""
        self.client.get("/admin/validar-empresa", name="Admin – Validar Empresa")

    @tag("admin")
    @task(3)
    def notificaciones(self):
        """Consultar notificaciones (API JSON)."""
        self.client.get("/api/notificaciones", name="API – Notificaciones")


class EmpresaUser(HttpUser):
    """Simula un usuario empresa navegando su panel."""
    wait_time = between(2, 5)

    def on_start(self):
        """Iniciar sesión como empresa."""
        with self.client.post("/auth/login", data={
            "correo": "empresa1@utoriental.edu.mx",
            "password": "empresa123",
            "rol": "empresa"
        }, name="Login Empresa", catch_response=True) as response:
            if response.status_code != 200 and not (300 <= response.status_code < 400):
                response.failure(f"Login Empresa falló: {response.status_code}")
                print(f"DEBUG: Login Empresa falló. Status: {response.status_code}, Text: {response.text[:200]}")

    @tag("empresa")
    @task(3)
    def empresa_inicio(self):
        """Ver la página de inicio de la empresa."""
        self.client.get("/empresa/", name="Empresa – Inicio")

    @tag("empresa")
    @task(2)
    def empresa_consultar(self):
        """Ver las vacantes de la empresa."""
        self.client.get("/empresa/consultar", name="Empresa – Consultar Vacantes")

    @tag("empresa")
    @task(1)
    def empresa_perfil(self):
        """Ver el perfil de la empresa."""
        self.client.get("/empresa/perfil", name="Empresa – Perfil")

    @tag("empresa")
    @task(1)
    def empresa_estadisticas(self):
        """Ver las estadísticas de la empresa."""
        self.client.get("/empresa/estadisticas", name="Empresa – Estadísticas")

    @tag("empresa")
    @task(2)
    def notificaciones(self):
        """Consultar notificaciones."""
        self.client.get("/api/notificaciones", name="API – Notificaciones (Empresa)")


class CandidatoUser(HttpUser):
    """Simula un candidato buscando vacantes y postulándose."""
    wait_time = between(1, 4)

    def on_start(self):
        """Iniciar sesión como candidato."""
        with self.client.post("/auth/login", data={
            "correo": "candidato1@utoriental.edu.mx",
            "password": "candidato123",
            "rol": "candidato"
        }, name="Login Candidato", catch_response=True) as response:
            if response.status_code != 200 and not (300 <= response.status_code < 400):
                response.failure(f"Login Candidato falló: {response.status_code}")
                print(f"DEBUG: Login Candidato falló. Status: {response.status_code}, Text: {response.text[:200]}")

    @tag("candidato")
    @task(4)
    def candidato_buscar_vacantes(self):
        """Buscar vacantes disponibles."""
        self.client.get("/candidato/buscar-vacantes", name="Candidato – Buscar Vacantes")

    @tag("candidato")
    @task(2)
    def candidato_perfil(self):
        """Ver el perfil del candidato."""
        self.client.get("/candidato/perfil", name="Candidato – Perfil")

    @tag("candidato")
    @task(2)
    def notificaciones(self):
        """Consultar notificaciones."""
        self.client.get("/api/notificaciones", name="API – Notificaciones (Candidato)")