import streamlit as st
from utils.data_loader import cargar_datos_db
from components.login_view import render_login
from components.dashboard_view import render_dashboard
from components.editor_view import render_editor
from components.capacitaciones_view import render_capacitaciones
from components.empleados_view import render_empleados
from components.asistencia_view import render_asistencia

st.set_page_config(
    page_title="INGENIERÍA Y SUMINISTROS J&M S.A.S.", 
    page_icon="📊", 
    layout="wide"
)

# Estilos CSS globales inspirados en la identidad visual (Negro, Amarillo Industrial, Gris)
st.markdown("""
    <style>
        /* Fondo principal de la aplicación */
        .stApp {
            background-color: #121212;
            color: #E0E0E0;
        }
        /* Botones principales tipo primario con el amarillo corporativo */
        .stButton>button[kind="primary"] {
            background-color: #FFC107 !important;
            color: #000000 !important;
            font-weight: bold;
            border-radius: 6px;
            border: none;
        }
        .stButton>button[kind="primary"]:hover {
            background-color: #FFD54F !important;
            color: #000000 !important;
        }
        /* Botones secundarios y contenedores */
        div.stButton>button {
            border-radius: 6px;
            border: 1px solid #424242;
        }
        /* Tarjetas y contenedores de formularios */
        .stForm {
            background-color: #1E1E1E;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #333333;
        }
        /* Métricas */
        [data-testid="stMetricValue"] {
            color: #FFC107 !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- RUTA PÚBLICA DE REGISTRO DE ASISTENCIA (accedida desde el QR o el enlace) ---
# No requiere inicio de sesión: cualquier empleado citado que escanee el QR
# llega directo a esta vista para marcar si asistió o no.
query_params = st.query_params
if query_params.get("view") == "asistencia" and query_params.get("id"):
    render_asistencia(query_params.get("id"))
    st.stop()

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = "dashboard"

def cambiar_a_tabla():
    st.session_state.pagina_actual = "tabla"

def cambiar_a_capacitaciones():
    st.session_state.pagina_actual = "capacitaciones"

def cambiar_a_empleados():
    st.session_state.pagina_actual = "empleados"

def cambiar_a_dashboard():
    st.session_state.pagina_actual = "dashboard"

def cerrar_sesion():
    st.session_state.autenticado = False
    st.session_state.usuario_actual = None
    st.session_state.pagina_actual = "dashboard"

if not st.session_state.autenticado:
    render_login()
else:
    df_actual = cargar_datos_db()
    
    if st.session_state.pagina_actual == "dashboard":
        render_dashboard(df_actual, cambiar_a_tabla, cambiar_a_capacitaciones, cambiar_a_empleados, cerrar_sesion)
    elif st.session_state.pagina_actual == "tabla":
        render_editor(df_actual, cambiar_a_dashboard)
    elif st.session_state.pagina_actual == "capacitaciones":
        render_capacitaciones(cambiar_a_dashboard)
    elif st.session_state.pagina_actual == "empleados":
        render_empleados(cambiar_a_dashboard)