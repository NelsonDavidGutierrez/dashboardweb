# 📊 Dashboard Web – INGENIERÍA Y SUMINISTROS J&M S.A.S.

Aplicación web desarrollada con **Streamlit** y **PostgreSQL** para gestionar la matriz de riesgos (GTC-45), el personal y las capacitaciones de la empresa, con registro de asistencia mediante código QR.

## ✨ Funcionalidades

| Módulo | Descripción |
|---|---|
| 🔐 **Inicio de sesión** | Acceso con usuario y contraseña (contraseñas cifradas con `bcrypt`). |
| 📊 **Panel de control** | Menú principal de módulos y vista rápida de datos numéricos. |
| 📝 **Editor de la matriz de riesgos** | Edición de los registros de la matriz y guardado en la base de datos. Exportación a **Excel** y **PDF**. |
| 👥 **Personal y permisos** | Registro de empleados, cargos, roles y permiso de edición. |
| 🎓 **Capacitaciones** | Programación de capacitaciones, carga de material, envío de notificaciones por correo y generación de enlace/QR de asistencia. |
| ✅ **Registro de asistencia (público)** | Los empleados citados escanean el QR y marcan si asistieron, **sin iniciar sesión**. |

## 🗂️ Estructura del proyecto

```
dashboardweb/
├── app.py                  # Punto de entrada y navegación
├── logo.png
├── requirements.txt
├── components/             # Vistas de la interfaz
│   ├── login_view.py
│   ├── dashboard_view.py
│   ├── editor_view.py
│   ├── empleados_view.py
│   ├── capacitaciones_view.py
│   └── asistencia_view.py
├── database/
│   └── conexion.py         # Conexión a PostgreSQL (SQLAlchemy)
└── utils/
    ├── data_loader.py      # Lectura/escritura de datos
    ├── exportadores.py     # Exportación a Excel y PDF
    └── notificaciones.py   # Envío de correos (SMTP)
```

## 🧰 Requisitos

- Python 3.10 o superior
- PostgreSQL
- Librerías: `streamlit`, `pandas`, `sqlalchemy`, `psycopg2-binary`, `qrcode`, `bcrypt`, `openpyxl`, `reportlab`

## 🚀 Instalación y ejecución

```bash
# 1. Clonar el repositorio
git clone https://github.com/NelsonDavidGutierrez/dashboardweb.git
cd dashboardweb

# 2. (Recomendado) Crear un entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar la base de datos y los secretos (ver secciones siguientes)

# 5. Ejecutar la aplicación
streamlit run app.py
```

La app se abre en `http://localhost:8501`.

## 🗄️ Base de datos

La aplicación usa **PostgreSQL**. La conexión está definida en `database/conexion.py` (por defecto: servidor `localhost`, puerto `5432`, base de datos `matriz_unica_db`).

Tablas que utiliza:

| Tabla | Contenido |
|---|---|
| `matriz_riesgos` | Matriz de identificación de peligros y valoración de riesgos (GTC-45). Debe existir y contener datos antes de iniciar. |
| `empleados_usuarios` | Personal, roles, usuarios y contraseñas cifradas. |
| `capacitaciones` | Capacitaciones programadas. |
| `asistencias_capacitaciones` | Registros de asistencia a las capacitaciones. |

> ⚠️ **Importante:** ajusta la cadena de conexión (`DB_URL`) en `database/conexion.py` con tus propias credenciales. Evita dejar contraseñas escritas directamente en el código de un repositorio.

## 🔑 Configuración de secretos (correo)

El envío de notificaciones de capacitaciones usa SMTP. Crea el archivo `.streamlit/secrets.toml` (está excluido del repositorio por `.gitignore`):

```toml
[email]
servidor = "smtp.ejemplo.com"
puerto = 587
usuario = "usuario@ejemplo.com"
password = "tu_contraseña_o_clave_de_aplicación"
remitente = "usuario@ejemplo.com"
```

Si usas Gmail u Outlook, genera una **contraseña de aplicación** en lugar de usar la contraseña normal de la cuenta.

Para **Streamlit Community Cloud**, pega este mismo contenido en *Advanced settings → Secrets*.

## 📱 Registro de asistencia por QR

Cada capacitación genera un enlace con este formato:

```
https://<tu-dominio>/?view=asistencia&id=<ID_CAPACITACION>
```

Quien abra el enlace (o escanee el QR) accede directamente a la vista de asistencia, sin necesidad de iniciar sesión. Para que funcione fuera de tu red local, la aplicación debe estar desplegada en un servidor accesible.

## 🔒 Seguridad

- No subas `.streamlit/secrets.toml`, `.env` ni credenciales al repositorio.
- Si alguna credencial se publicó por error, cámbiala de inmediato: queda en el historial de Git aunque se borre después.
- Cambia las contraseñas por defecto de PostgreSQL antes de usar la app en producción.

## 🛠️ Tecnologías

Python · Streamlit · PostgreSQL · SQLAlchemy · Pandas · bcrypt · OpenPyXL · ReportLab · qrcode

## 📄 Licencia

Proyecto de uso interno de INGENIERÍA Y SUMINISTROS J&M S.A.S.
