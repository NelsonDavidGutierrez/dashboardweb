import streamlit as st


def _inyectar_estilos_dashboard():
    st.markdown("""
        <style>
            .stApp {
                background: radial-gradient(circle at top, #1c1c1c 0%, #0d0d0d 65%) !important;
            }
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(16px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .jm-banner {
                background: linear-gradient(145deg, #1E1E1E, #171717);
                border-radius: 16px; border: 1px solid #333333;
                padding: 18px 24px; animation: fadeInUp 0.6s ease-out;
                box-shadow: 0 10px 26px rgba(0,0,0,0.3);
                display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap;
            }
            .jm-badge-rol {
                display:inline-block; padding:4px 14px; border-radius:999px;
                background: rgba(255,193,7,0.12); border:1px solid rgba(255,193,7,0.5);
                color:#FFC107; font-weight:700; font-size:0.8rem;
            }
            .jm-stat {
                background: linear-gradient(145deg, #1E1E1E, #171717);
                border-radius: 14px; border: 1px solid #333333;
                padding: 16px 18px; animation: fadeInUp 0.7s ease-out;
                box-shadow: 0 8px 22px rgba(0,0,0,0.3);
                display: flex; align-items: center; gap: 14px;
                transition: transform 0.15s ease;
            }
            .jm-stat:hover { transform: translateY(-3px); }
            .jm-stat .ico {
                width: 46px; height: 46px; border-radius: 12px;
                display: flex; align-items: center; justify-content: center;
                font-size: 1.4rem; flex-shrink: 0;
            }
            .jm-stat .val { font-size: 1.6rem; font-weight: 800; color: #F5F5F5; line-height:1; }
            .jm-stat .lbl { font-size: 0.8rem; color: #9E9E9E; margin-top: 2px; }
            .jm-menu-card {
                background: linear-gradient(145deg, #1E1E1E, #171717);
                border-radius: 14px; border: 1px solid #333333;
                padding: 18px 18px 10px 18px; animation: fadeInUp 0.8s ease-out;
                box-shadow: 0 8px 22px rgba(0,0,0,0.3);
                transition: transform 0.15s ease, border-color 0.15s ease;
                text-align: center;
            }
            .jm-menu-card:hover { transform: translateY(-4px); border-color: #FFC107; }
            .jm-menu-card .ico { font-size: 1.9rem; margin-bottom: 6px; }
            .jm-menu-card .ttl { font-weight: 700; color: #E0E0E0; margin-bottom: 2px; }
            .jm-menu-card .desc { font-size: 0.78rem; color: #9E9E9E; margin-bottom: 8px; }
            div.stButton > button {
                transition: transform 0.15s ease, box-shadow 0.15s ease;
            }
            div.stButton > button:hover {
                transform: translateY(-2px) scale(1.02);
                box-shadow: 0 6px 16px rgba(0,0,0,0.35);
            }
        </style>
    """, unsafe_allow_html=True)


def render_dashboard(df, ir_a_tabla_callback, ir_a_capacitaciones_callback, ir_a_empleados_callback, logout_callback):
    _inyectar_estilos_dashboard()
    usuario = st.session_state.get('usuario_actual', {})

    col_l1, col_l2 = st.columns([1.2, 5])
    with col_l1:
        try:
            st.image("logo.png", width=160)
        except:
            st.write("Logo J&M")
    with col_l2:
        st.markdown("<h3 style='color: #FFC107; margin-bottom: 0;'>INGENIERÍA Y SUMINISTROS J&M S.A.S.</h3>", unsafe_allow_html=True)
        st.title("📊 Panel de Control General")

    st.markdown(f"""
        <div class="jm-banner">
            <div>
                <span style="color:#E0E0E0; font-size:1.05rem;">👋 Bienvenido, <b>{usuario.get('nombre')}</b></span><br>
                <span style="color:#9E9E9E; font-size:0.85rem;">Aquí tienes un resumen rápido de tu operación</span>
            </div>
            <span class="jm-badge-rol">🏷️ {usuario.get('rol')}</span>
        </div>
    """, unsafe_allow_html=True)

    st.write("")
    col_out1, col_out2 = st.columns([5, 1])
    with col_out2:
        if st.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True):
            logout_callback()

    st.write("")

    nulos = df.isna().sum().sum() if not df.empty else 0
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
            <div class="jm-stat">
                <div class="ico" style="background:rgba(255,193,7,0.12);">📦</div>
                <div><div class="val">{len(df)}</div><div class="lbl">Total de Registros (Riesgos)</div></div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="jm-stat">
                <div class="ico" style="background:rgba(33,150,243,0.12);">📋</div>
                <div><div class="val">{len(df.columns) if not df.empty else 0}</div><div class="lbl">Columnas Totales</div></div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="jm-stat">
                <div class="ico" style="background:rgba(244,67,54,0.12);">⚠️</div>
                <div><div class="val">{int(nulos)}</div><div class="lbl">Valores Vacíos</div></div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.markdown("---")
    st.subheader("🧭 Menú Principal de Módulos")

    es_admin = usuario.get('rol') in ["Super Admin", "Admin"]
    col_btn1, col_btn2, col_btn3 = st.columns(3)

    with col_btn1:
        st.markdown("""
            <div class="jm-menu-card">
                <div class="ico">✏️</div>
                <div class="ttl">Gestión de Riesgos</div>
                <div class="desc">Edita la matriz IPVRDC / GTC-45</div>
            </div>
        """, unsafe_allow_html=True)
        st.button("Ingresar →", key="btn_riesgos", type="primary", use_container_width=True, on_click=ir_a_tabla_callback)

    with col_btn2:
        st.markdown("""
            <div class="jm-menu-card">
                <div class="ico">🎓</div>
                <div class="ttl">Capacitaciones</div>
                <div class="desc">Crea sesiones y controla asistencia</div>
            </div>
        """, unsafe_allow_html=True)
        st.button("Ingresar →", key="btn_capacitaciones", type="secondary", use_container_width=True, on_click=ir_a_capacitaciones_callback)

    if es_admin:
        with col_btn3:
            st.markdown("""
                <div class="jm-menu-card">
                    <div class="ico">👥</div>
                    <div class="ttl">Personal y Permisos</div>
                    <div class="desc">Administra empleados y roles</div>
                </div>
            """, unsafe_allow_html=True)
            st.button("Ingresar →", key="btn_empleados", type="secondary", use_container_width=True, on_click=ir_a_empleados_callback)

    st.markdown("---")
    if not df.empty:
        st.subheader("📈 Vista Rápida de Datos Numéricos")
        df_num = df.select_dtypes(include=['number'])
        if not df_num.empty:
            st.line_chart(df_num, use_container_width=True)