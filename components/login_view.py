import streamlit as st
import bcrypt
from utils.data_loader import cargar_empleados, guardar_empleado, verificar_credenciales


def _inyectar_estilos_login():
    st.markdown("""
        <style>
            .stApp {
                background: radial-gradient(circle at top, #1c1c1c 0%, #0d0d0d 65%) !important;
            }
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(18px); }
                to { opacity: 1; transform: translateY(0); }
            }
            @keyframes pulseRing {
                0% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.45); }
                70% { box-shadow: 0 0 0 16px rgba(255, 193, 7, 0); }
                100% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0); }
            }
            .jm-hero { text-align: center; animation: fadeInUp 0.6s ease-out; margin-bottom: 4px; }
            .jm-hero h1 {
                font-size: 1.8rem; margin-bottom: 2px; font-weight: 800;
                background: linear-gradient(90deg, #FFC107, #FFE082);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            }
            .jm-chip {
                display: inline-block; padding: 4px 16px; border-radius: 999px;
                background: rgba(255, 193, 7, 0.12); border: 1px solid rgba(255, 193, 7, 0.5);
                color: #FFC107; font-size: 0.8rem; font-weight: 600; letter-spacing: 0.5px;
            }
            .jm-lock-ico {
                width: 64px; height: 64px; border-radius: 50%; margin: 6px auto 4px auto;
                background: linear-gradient(135deg, #FFC107, #FF8F00);
                display: flex; align-items: center; justify-content: center;
                font-size: 1.7rem; animation: pulseRing 2.4s infinite;
            }
            .jm-card {
                background: linear-gradient(145deg, #1E1E1E, #171717);
                border-radius: 16px; border: 1px solid #333333;
                padding: 28px 30px; animation: fadeInUp 0.7s ease-out;
                box-shadow: 0 10px 30px rgba(0,0,0,0.35);
            }
            div[data-testid="stForm"] {
                background: linear-gradient(145deg, #1E1E1E, #171717) !important;
                border-radius: 16px !important; border: 1px solid #333333 !important;
                box-shadow: 0 10px 30px rgba(0,0,0,0.35) !important;
                animation: fadeInUp 0.7s ease-out;
            }
            div.stButton > button, div.stFormSubmitButton > button {
                transition: transform 0.15s ease, box-shadow 0.15s ease;
            }
            div.stButton > button:hover, div.stFormSubmitButton > button:hover {
                transform: translateY(-2px) scale(1.02);
                box-shadow: 0 6px 16px rgba(0,0,0,0.35);
            }
            .stTextInput input {
                border-radius: 8px !important;
            }
        </style>
    """, unsafe_allow_html=True)


def render_login():
    _inyectar_estilos_login()

    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        try:
            st.image("logo.png", width=240)
        except:
            st.warning("⚠️ Logo no encontrado. Asegúrate de guardar 'logo.png' en la raíz.")

        st.markdown("""
            <div class="jm-hero">
                <h1>INGENIERÍA Y SUMINISTROS J&M S.A.S.</h1>
                <span class="jm-chip">🛠️ Contratista Oil &amp; Gas · Meta · Huila · Casanare · Bogotá</span>
            </div>
        """, unsafe_allow_html=True)

    st.write("")
    df_empleados = cargar_empleados()

    if df_empleados.empty:
        col1, col2, col3 = st.columns([1, 1.8, 1])
        with col2:
            st.markdown("""
                <div class="jm-card" style="text-align:center; margin-bottom: 14px;">
                    <div class="jm-lock-ico">👑</div>
                    <p style="color:#FFC107; font-weight:700; font-size:1.05rem; margin:4px 0 0 0;">
                        Configuración Inicial del Sistema
                    </p>
                    <p style="color:#9E9E9E; font-size:0.85rem; margin-top:2px;">
                        No hay usuarios registrados todavía. Crea el <b>Super Administrador</b> para comenzar.
                    </p>
                </div>
            """, unsafe_allow_html=True)

            with st.form("form_super_admin"):
                st.markdown("##### 👑 Datos del Super Administrador")
                nombre = st.text_input("🧑 Nombre Completo", value="Administrador Principal")
                correo = st.text_input("📧 Correo electrónico", value="admin@empresa.com")
                celular = st.text_input("📱 Celular", value="3000000000")
                direccion = st.text_input("📍 Dirección", value="Sede Central")
                cargo = st.text_input("💼 Cargo", value="Director TI")
                st.markdown("---")
                username = st.text_input("👤 Nombre de Usuario (Login)", value="superadmin")
                password = st.text_input("🔑 Contraseña", type="password", value="admin123")

                btn_crear_sa = st.form_submit_button("👑 Crear Super Administrador", type="primary", use_container_width=True)
                if btn_crear_sa:
                    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    nuevo_sa = {
                        "id": 1,
                        "nombre": nombre,
                        "correo": correo,
                        "celular": celular,
                        "direccion": direccion,
                        "cargo": cargo,
                        "puede_editar": True,
                        "rol": "Super Admin",
                        "username": username,
                        "password_hash": hashed
                    }
                    guardar_empleado(nuevo_sa)
                    st.success("¡Super Administrador creado con éxito! Por favor recarga la página.")
                    st.rerun()
        return

    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown("""
            <div style="text-align:center; margin-bottom:10px;">
                <div class="jm-lock-ico">🔐</div>
                <p style="color:#E0E0E0; font-weight:700; font-size:1.1rem; margin:4px 0 0 0;">Acceso a la Plataforma</p>
                <p style="color:#9E9E9E; font-size:0.85rem;">Inicia sesión con tus credenciales corporativas</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            user_input = st.text_input("👤 Usuario")
            pass_input = st.text_input("🔑 Contraseña", type="password")

            submit_login = st.form_submit_button("🚀 Ingresar", type="primary", use_container_width=True)

            if submit_login:
                user_auth = verificar_credenciales(user_input, pass_input)
                if user_auth:
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = user_auth
                    st.success(f"¡Bienvenido, {user_auth['nombre']}! 🎉")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")