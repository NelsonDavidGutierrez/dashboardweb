import streamlit as st
import pandas as pd
import bcrypt
from utils.data_loader import cargar_empleados, guardar_empleado


def _inyectar_estilos_empleados():
    st.markdown("""
        <style>
            .stApp {
                background: radial-gradient(circle at top, #1c1c1c 0%, #0d0d0d 65%) !important;
            }
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(16px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .jm-stat {
                background: linear-gradient(145deg, #1E1E1E, #171717);
                border-radius: 14px; border: 1px solid #333333;
                padding: 14px 16px; animation: fadeInUp 0.6s ease-out;
                box-shadow: 0 8px 22px rgba(0,0,0,0.3);
                display: flex; align-items: center; gap: 12px;
            }
            .jm-stat .ico {
                width: 42px; height: 42px; border-radius: 10px;
                display: flex; align-items: center; justify-content: center;
                font-size: 1.25rem; flex-shrink: 0;
            }
            .jm-stat .val { font-size: 1.4rem; font-weight: 800; color: #F5F5F5; line-height:1; }
            .jm-stat .lbl { font-size: 0.78rem; color: #9E9E9E; margin-top: 2px; }
            div[data-testid="stForm"] {
                background: linear-gradient(145deg, #1E1E1E, #171717) !important;
                border-radius: 16px !important; border: 1px solid #333333 !important;
                box-shadow: 0 10px 26px rgba(0,0,0,0.3) !important;
                animation: fadeInUp 0.7s ease-out;
            }
            div.stButton > button, div.stFormSubmitButton > button {
                transition: transform 0.15s ease, box-shadow 0.15s ease;
            }
            div.stButton > button:hover, div.stFormSubmitButton > button:hover {
                transform: translateY(-2px) scale(1.02);
                box-shadow: 0 6px 16px rgba(0,0,0,0.35);
            }
        </style>
    """, unsafe_allow_html=True)


def _color_por_rol(valor):
    colores = {
        "Super Admin": "background-color: rgba(255,193,7,0.18); color:#FFC107; font-weight:700;",
        "Admin": "background-color: rgba(33,150,243,0.18); color:#64B5F6; font-weight:700;",
        "Usuario / Empleado": "background-color: rgba(158,158,158,0.18); color:#BDBDBD; font-weight:600;",
    }
    return colores.get(valor, "")


def render_empleados(volver_dashboard_callback):
    _inyectar_estilos_empleados()

    if st.button("⬅️ Volver al Dashboard General", on_click=volver_dashboard_callback):
        pass

    col_l1, col_l2 = st.columns([1.2, 6])
    with col_l1:
        try:
            st.image("logo.png", width=140)
        except:
            pass
    with col_l2:
        st.markdown("<h4 style='color: #FFC107; margin-bottom: 0;'>INGENIERÍA Y SUMINISTROS J&M S.A.S.</h4>", unsafe_allow_html=True)
        st.title("👥 Módulo de Personal y Permisos")

    st.markdown("Añade nuevos empleados, define sus cargos, datos de contacto, permisos de edición y credenciales de acceso.")

    # --- Tarjetas resumen ---
    df_preview = cargar_empleados()
    total_emp = len(df_preview) if not df_preview.empty else 0
    total_admins = int((df_preview['rol'].isin(["Super Admin", "Admin"])).sum()) if not df_preview.empty else 0
    total_editores = int(df_preview['puede_editar'].sum()) if not df_preview.empty and 'puede_editar' in df_preview.columns else 0

    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.markdown(f"""
            <div class="jm-stat"><div class="ico" style="background:rgba(255,193,7,0.12);">👥</div>
            <div><div class="val">{total_emp}</div><div class="lbl">Personal Registrado</div></div></div>
        """, unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"""
            <div class="jm-stat"><div class="ico" style="background:rgba(33,150,243,0.12);">🛡️</div>
            <div><div class="val">{total_admins}</div><div class="lbl">Admins / Super Admins</div></div></div>
        """, unsafe_allow_html=True)
    with col_s3:
        st.markdown(f"""
            <div class="jm-stat"><div class="ico" style="background:rgba(76,175,80,0.12);">✏️</div>
            <div><div class="val">{total_editores}</div><div class="lbl">Con permiso de edición</div></div></div>
        """, unsafe_allow_html=True)

    st.write("")
    st.markdown("---")

    with st.form("form_nuevo_empleado", clear_on_submit=True):
        st.subheader("➕ Registrar Nuevo Empleado / Usuario")

        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("🧑 Nombre Completo")
            correo = st.text_input("📧 Correo Electrónico")
            celular = st.text_input("📱 Número de Celular")
        with col2:
            direccion = st.text_input("📍 Dirección")
            cargo = st.text_input("💼 Cargo en la Empresa")
            rol = st.selectbox("🏷️ Rol en la Plataforma", ["Usuario / Empleado", "Admin", "Super Admin"])

        st.markdown("---")
        st.subheader("🔐 Credenciales de Acceso y Permisos")

        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            username = st.text_input("👤 Nombre de Usuario (Login)")
        with col_p2:
            password = st.text_input("🔑 Contraseña de Acceso", type="password")
        with col_p3:
            puede_editar = st.checkbox("✏️ ¿Puede editar contenido y registros?", value=False)

        btn_guardar_emp = st.form_submit_button("💾 Guardar y Crear Usuario", type="primary", use_container_width=True)

        if btn_guardar_emp:
            if nombre and username and password:
                df_actual = cargar_empleados()
                if not df_actual.empty and username in df_actual['username'].values:
                    st.error("⚠️ El nombre de usuario ya existe. Elige otro.")
                else:
                    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    nuevo_reg = {
                        "id": len(df_actual) + 1,
                        "nombre": nombre,
                        "correo": correo,
                        "celular": celular,
                        "direccion": direccion,
                        "cargo": cargo,
                        "puede_editar": puede_editar,
                        "rol": rol,
                        "username": username,
                        "password_hash": hashed
                    }
                    guardar_empleado(nuevo_reg)
                    st.success(f"¡Empleado '{nombre}' y credenciales creadas con éxito! 🎉")
                    st.rerun()
            else:
                st.error("Por favor completa los campos obligatorios: Nombre, Usuario y Contraseña.")

    st.markdown("---")
    st.subheader("📋 Lista de Personal Registrado")
    df_empleados = cargar_empleados()
    if not df_empleados.empty:
        df_mostrar = df_empleados.drop(columns=["password_hash"])
        estilos = df_mostrar.style.map(_color_por_rol, subset=["rol"]) if "rol" in df_mostrar.columns else df_mostrar
        st.dataframe(estilos, use_container_width=True)
    else:
        st.info("No hay personal registrado.")