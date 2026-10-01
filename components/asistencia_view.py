import streamlit as st
from datetime import datetime
from utils.data_loader import obtener_capacitacion_por_id, guardar_asistencia, cargar_asistencias


def _iniciales(nombre):
    partes = [p for p in nombre.strip().split(" ") if p]
    if not partes:
        return "?"
    if len(partes) == 1:
        return partes[0][0].upper()
    return (partes[0][0] + partes[1][0]).upper()


def render_asistencia(cap_id):
    """Vista pública (no requiere inicio de sesión) a la que apunta el QR / enlace
    de cada capacitación. Permite al empleado citado identificarse y marcar si
    asistió o no; el registro queda guardado en la base de datos."""

    # --- Estilos exclusivos de esta vista: fondo con degradado, tarjeta tipo
    # "tiquete de embarque", chips, animaciones de entrada y de confirmación ---
    st.markdown("""
        <style>
            .stApp {
                background: radial-gradient(circle at top, #1c1c1c 0%, #0d0d0d 65%) !important;
            }
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(18px); }
                to { opacity: 1; transform: translateY(0); }
            }
            @keyframes pulseGlow {
                0% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0.45); }
                70% { box-shadow: 0 0 0 14px rgba(255, 193, 7, 0); }
                100% { box-shadow: 0 0 0 0 rgba(255, 193, 7, 0); }
            }
            @keyframes bounceIn {
                0% { transform: scale(0.7); opacity: 0; }
                60% { transform: scale(1.05); opacity: 1; }
                100% { transform: scale(1); }
            }
            .jm-hero {
                text-align: center;
                animation: fadeInUp 0.6s ease-out;
                margin-bottom: 6px;
            }
            .jm-hero h1 {
                font-size: 1.9rem;
                margin-bottom: 2px;
                background: linear-gradient(90deg, #FFC107, #FFE082);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 800;
            }
            .jm-chip {
                display: inline-block;
                padding: 4px 16px;
                border-radius: 999px;
                background: rgba(255, 193, 7, 0.12);
                border: 1px solid rgba(255, 193, 7, 0.5);
                color: #FFC107;
                font-size: 0.8rem;
                font-weight: 600;
                letter-spacing: 0.5px;
            }
            .jm-ticket {
                position: relative;
                background: linear-gradient(145deg, #1E1E1E, #171717);
                border-radius: 16px;
                border: 1px solid #333333;
                padding: 26px 28px;
                animation: fadeInUp 0.7s ease-out;
                box-shadow: 0 10px 30px rgba(0,0,0,0.35);
            }
            .jm-ticket::before {
                content: "";
                position: absolute;
                left: 0; right: 0; bottom: -1px;
                border-bottom: 2px dashed #3a3a3a;
            }
            .jm-ticket-title {
                color: #FFC107;
                font-weight: 700;
                font-size: 1.15rem;
                margin-bottom: 14px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .jm-row {
                display: flex;
                align-items: center;
                gap: 10px;
                margin: 8px 0;
                color: #E0E0E0;
                font-size: 0.95rem;
            }
            .jm-row .ico {
                width: 30px; height: 30px;
                border-radius: 8px;
                background: rgba(255,193,7,0.1);
                display: flex; align-items: center; justify-content: center;
                flex-shrink: 0;
            }
            .jm-avatar {
                width: 42px; height: 42px;
                border-radius: 50%;
                background: linear-gradient(135deg, #FFC107, #FF8F00);
                color: #000;
                font-weight: 800;
                display: flex; align-items: center; justify-content: center;
                animation: pulseGlow 2.2s infinite;
                flex-shrink: 0;
            }
            .jm-status-card {
                animation: bounceIn 0.5s ease-out;
                border-radius: 14px;
                padding: 18px 22px;
                margin-top: 10px;
                font-weight: 600;
                text-align: center;
                font-size: 1.05rem;
            }
            .jm-status-ok {
                background: rgba(76, 175, 80, 0.12);
                border: 1px solid #4CAF50;
                color: #81C784;
            }
            .jm-status-bad {
                background: rgba(244, 67, 54, 0.12);
                border: 1px solid #F44336;
                color: #E57373;
            }
            .jm-prev-pill {
                display: inline-block;
                padding: 3px 12px;
                border-radius: 999px;
                font-size: 0.82rem;
                font-weight: 600;
                margin-top: 4px;
            }
            div.stButton > button {
                transition: transform 0.15s ease, box-shadow 0.15s ease;
            }
            div.stButton > button:hover {
                transform: translateY(-2px) scale(1.02);
                box-shadow: 0 6px 16px rgba(0,0,0,0.35);
            }
        </style>
    """, unsafe_allow_html=True)

    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        try:
            st.image("logo.png", width=200)
        except Exception:
            pass

    st.markdown("""
        <div class="jm-hero">
            <h1>INGENIERÍA Y SUMINISTROS J&M S.A.S.</h1>
            <span class="jm-chip">✅ Registro Digital de Asistencia</span>
        </div>
    """, unsafe_allow_html=True)
    st.write("")

    capacitacion = obtener_capacitacion_por_id(cap_id)

    if capacitacion is None:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
                <div class="jm-ticket" style="text-align:center;">
                    <div style="font-size:2.2rem;">⚠️</div>
                    <p style="color:#E57373; font-weight:600; margin-top:8px;">
                        Este código QR / enlace no corresponde a ninguna capacitación registrada.
                    </p>
                    <p style="color:#9E9E9E; font-size:0.9rem;">Verifica que estés usando el código más reciente.</p>
                </div>
            """, unsafe_allow_html=True)
        return

    nombre_cap = capacitacion.get('nombre', 'Capacitación')
    fecha_ini = capacitacion.get('fecha_inicio', '')
    hora_ini = capacitacion.get('hora_inicio', '')
    fecha_fin = capacitacion.get('fecha_fin', '')
    hora_fin = capacitacion.get('hora_fin', '')
    empleados_citados = [e.strip() for e in str(capacitacion.get('empleados', '')).split(",") if e.strip()]

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
            <div class="jm-ticket">
                <div class="jm-ticket-title">📚 {nombre_cap}</div>
                <div class="jm-row"><div class="ico">🟢</div><div><b>Inicio:</b> {fecha_ini} &nbsp;·&nbsp; {hora_ini}</div></div>
                <div class="jm-row"><div class="ico">🔴</div><div><b>Fin:</b> {fecha_fin} &nbsp;·&nbsp; {hora_fin}</div></div>
                <div class="jm-row"><div class="ico">👥</div><div><b>Personal citado:</b> {len(empleados_citados)} persona(s)</div></div>
            </div>
        """, unsafe_allow_html=True)

        st.write("")

        if not empleados_citados:
            st.warning("Esta capacitación no tiene empleados citados registrados todavía.")
            return

        st.markdown("<p style='font-weight:700; color:#FFC107; margin-bottom:2px;'>👤 Identifícate</p>", unsafe_allow_html=True)
        empleado_seleccionado = st.selectbox(
            "Selecciona tu nombre en la lista de citados",
            options=empleados_citados,
            label_visibility="collapsed",
        )

        iniciales = _iniciales(empleado_seleccionado)
        st.markdown(f"""
            <div class="jm-row" style="margin-top:10px;">
                <div class="jm-avatar">{iniciales}</div>
                <div style="font-size:1.05rem;"><b>{empleado_seleccionado}</b><br>
                <span style="color:#9E9E9E; font-size:0.8rem;">Confirma tu asistencia a continuación</span></div>
            </div>
        """, unsafe_allow_html=True)

        # Muestra si este empleado ya tiene un registro previo para esta capacitación
        df_asis_previo = cargar_asistencias()
        registro_previo = None
        if not df_asis_previo.empty:
            filtro = (
                (df_asis_previo['capacitacion_id'] == int(cap_id)) &
                (df_asis_previo['empleado_nombre'] == empleado_seleccionado)
            )
            coincidencias = df_asis_previo[filtro]
            if not coincidencias.empty:
                registro_previo = coincidencias.iloc[0]

        if registro_previo is not None:
            if bool(registro_previo['asistio']):
                st.markdown("<span class='jm-prev-pill' style='background:rgba(76,175,80,0.15); color:#81C784; border:1px solid #4CAF50;'>✅ Ya registraste tu asistencia</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='jm-prev-pill' style='background:rgba(244,67,54,0.15); color:#E57373; border:1px solid #F44336;'>❌ Ya marcaste que no asististe</span>", unsafe_allow_html=True)
            st.caption("Si fue un error, puedes volver a marcar abajo y se actualizará tu registro.")

        st.write("")
        st.markdown("**¿Asististe a esta capacitación?**")
        col_a, col_b = st.columns(2)
        marcar_asistio = None
        with col_a:
            if st.button("✅  Sí, asistí", type="primary", use_container_width=True):
                marcar_asistio = True
        with col_b:
            if st.button("❌  No asistí", type="secondary", use_container_width=True):
                marcar_asistio = False

        if marcar_asistio is not None:
            df_asis_actual = cargar_asistencias()
            nuevo_id = int(df_asis_actual['id'].max()) + 1 if not df_asis_actual.empty else 1

            registro = {
                "id": nuevo_id,
                "capacitacion_id": int(cap_id),
                "capacitacion_nombre": nombre_cap,
                "empleado_nombre": empleado_seleccionado,
                "fecha_capacitacion": f"{fecha_ini} {hora_ini} a {fecha_fin} {hora_fin}",
                "asistio": marcar_asistio,
                "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            guardar_asistencia(registro)

            if marcar_asistio:
                st.markdown(f"""
                    <div class="jm-status-card jm-status-ok">
                        🎉 ¡Gracias, {empleado_seleccionado}!<br>
                        <span style="font-weight:400; font-size:0.9rem;">Tu asistencia a <b>{nombre_cap}</b> quedó registrada correctamente.</span>
                    </div>
                """, unsafe_allow_html=True)
                st.balloons()
            else:
                st.markdown(f"""
                    <div class="jm-status-card jm-status-bad">
                        📋 Registro guardado<br>
                        <span style="font-weight:400; font-size:0.9rem;"><b>{empleado_seleccionado}</b> no asistió a <b>{nombre_cap}</b>.</span>
                    </div>
                """, unsafe_allow_html=True)