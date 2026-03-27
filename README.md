# UT Oriental Emplea v2.0

¡Bienvenido a la plataforma oficial de vinculación laboral de la Universidad Tecnológica de Oriental! Esta aplicación es un ecosistema integral diseñado para conectar a estudiantes y egresados con el sector empresarial de manera segura, eficiente y profesional.

## 🚀 Propósito del Proyecto
El sistema facilita la gestión del talento universitario, permitiendo que:
- Los **Candidatos** construyan un perfil profesional sólido y se vinculen con vacantes reales.
- Las **Empresas** gestionen sus ofertas laborales y encuentren perfiles específicos de la UT.
- Los **Administradores** supervisen la integridad del sistema y generen inteligencia de negocios.

## 🛠️ Stack Tecnológico
- **Backend:** Python 3.x con Flask Framework.
- **Base de Datos:** PostgreSQL (Consultas parametrizadas con Psycopg2).
- **Frontend:** HTML5, CSS3 (Vanilla + Media Queries para Responsividad), JavaScript (ES6+).
- **Reportes:** Openpyxl para generación de archivos Excel (.xlsx).
- **Documentos:** html2pdf.js / jsPDF para exportación de manuales y CVs.
- **Seguridad Auth:** Werkzeug (Hashing de contraseñas) + Flask-Login.

## 🛡️ Pilares de Seguridad (Blindaje Total)
La seguridad es el núcleo de esta versión 2.0:
1. **Segundo Factor de Autenticación (2FA):** Verificación obligatoria vía email para Candidatos y Empresas.
2. **Protección contra Inyecciones SQL:** Uso estricto de queries parametrizadas y middleware de detección proactiva.
3. **Escudo Anti-Scripts (XSS):** Sanitización automática de entradas de usuario (`strip_tags`) y bloqueo de patrones `<script>`.
4. **Seguridad de Archivos (Deep-Scan):** Validación de "Magic Numbers" (firmas binarias) para asegurar que los archivos subidos (PDF/Fotos) sean legítimos.
5. **Aislamiento de Datos:** Los documentos sensibles (CVs) se guardan fuera del directorio público.

## 📦 Módulos Principales

### 1. Panel de Administración (Control Total)
- Validación manual de nuevas empresas y candidatos.
- Generación de reportes ejecutivos y de colocación en Excel con diseño institucional.
- Acceso al Manual Integral de la aplicación y herramientas de auditoría.

### 2. Ecosistema de Empresas (Gestión de Talento)
- Publicación de vacantes detalladas (perfiles, requisitos, sueldos).
- Seguimiento de postulaciones en tiempo real (Visto, Aceptado, Rechazado).
- Descarga segura de CVs (solo de candidatos postulados).

### 3. Portal de Candidatos (Talento UT)
- Constructor de CV dinámico (idiomas, certificaciones, experiencia).
- Búsqueda inteligente de vacantes y guardado de favoritas.
- Notificaciones automáticas sobre el estado de sus postulaciones.

## 📖 Guía de Instalación Rápida
1. Clonar el repositorio.
2. Instalar dependencias: `pip install flask psycopg2 flask-login openpyxl werkzeug`.
3. Configurar variables de entorno (DB_HOST, DB_NAME, DB_USER, DB_PASS).
4. Ejecutar: `python main.py`.

---
© 2026 Universidad Tecnológica de Oriental | Departamento de Desarrollo Tecnológico e Innovación
