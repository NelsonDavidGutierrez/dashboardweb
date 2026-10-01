import os
import re
import mimetypes
import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from utils.data_loader import cargar_capacitaciones, guardar_capacitacion, cargar_empleados, cargar_asistencias
from utils.notificaciones import enviar_notificacion_capacitacion

# IMPORTANTE: cuando despliegues la app en un servidor (no en tu computador local),
# cambia esta URL por la dirección/IP pública donde quede corriendo Streamlit.
# Mientras sea "localhost" el QR y el enlace del correo solo funcionarán desde el mismo equipo.
BASE_URL = "http://localhost:8501"

# Carpeta donde se guardan los materiales adjuntos (dashboard/materiales)
MATERIALES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "materiales")


def _guardar_material(archivo, id_cap):
    """Guarda el archivo subido en disco y devuelve el nombre con el que quedó guardado."""
    os.makedirs(MATERIALES_DIR, exist_ok=True)
    nombre_limpio = re.sub(r"[^A-Za-z0-9._-]", "_", archivo.name)
    nombre_guardado = f"{id_cap}_{nombre_limpio}"
    with open(os.path.join(MATERIALES_DIR, nombre_guardado), "wb") as f:
        f.write(archivo.getvalue())
    return nombre_guardado


def _ruta_material(nombre_guardado):
    """Devuelve la ruta completa del material si existe en disco, si no None."""
    if isinstance(nombre_guardado, str) and nombre_guardado.strip():
        ruta = os.path.join(MATERIALES_DIR, nombre_guardado)
        if os.path.exists(ruta):
            return ruta
    return None


def render_capacitaciones(volver_dashboard_callback):
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
        st.title("🎓 Módulo de Capacitaciones")
        
    usuario = st.session_state.get('usuario_actual', {})
    rol = usuario.get('rol', '')
    nombre_usuario = usuario.get('nombre', '')
    
    # Cargar lista de empleados para el selector (incluyendo Admin y Super Admin)
    df_empleados = cargar_empleados()
    lista_nombres_empleados = []
    if not df_empleados.empty and 'nombre' in df_empleados.columns:
        lista_nombres_empleados = df_empleados['nombre'].tolist()
    else:
        lista_nombres_empleados = ["Administrador Principal"]

    # Formulario de creación solo visible para Administradores o Super Admins
    if rol in ["Super Admin", "Admin"]:
        with st.form("form_capacitacion", clear_on_submit=True):
            st.subheader("➕ Registrar Nueva Capacitación")
            nombre_cap = st.text_input("Nombre de la Capacitación")
            
            # Selector múltiple con el listado real de usuarios y empleados
            empleados_seleccionados = st.multiselect(
                "Empleados Asistentes (Selecciona de la lista)", 
                options=lista_nombres_empleados
            )
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                fecha_inicio = st.date_input("Fecha de Inicio")
                hora_inicio = st.time_input("Hora de Inicio")
            with col_f2:
                fecha_fin = st.date_input("Fecha de Fin")
                hora_fin = st.time_input("Hora de Fin")
                
            material_archivo = st.file_uploader("Subir Material (PDF, PPTX, Word, MP4)", type=["pdf", "pptx", "docx", "mp4"])

            enviar_correo = st.checkbox("📧 Notificar por correo a los empleados citados", value=True)
            
            btn_crear = st.form_submit_button("🚀 Crear Capacitación y Generar Enlace Automático", type="primary")
            if btn_crear:
                if nombre_cap and empleados_seleccionados:
                    lista_caps = cargar_capacitaciones()
                    id_nuevo = int(lista_caps['id'].max()) + 1 if not lista_caps.empty else 1
                    
                    # Generación automática del enlace de asistencia interno
                    link_automatico = f"{BASE_URL}/?view=asistencia&id={id_nuevo}"
                    nombre_archivo = material_archivo.name if material_archivo else "Sin archivo"

                    # Guardar físicamente el archivo para que los empleados puedan descargarlo
                    material_guardado = ""
                    if material_archivo is not None:
                        material_guardado = _guardar_material(material_archivo, id_nuevo)
                    
                    nueva_cap = {
                        "id": id_nuevo,
                        "nombre": nombre_cap,
                        "empleados": ", ".join(empleados_seleccionados),
                        "fecha_inicio": str(fecha_inicio),
                        "hora_inicio": str(hora_inicio),
                        "fecha_fin": str(fecha_fin),
                        "hora_fin": str(hora_fin),
                        "link_asistencia": link_automatico,
                        "material_nombre": nombre_archivo,
                        "material_ruta": material_guardado
                    }
                    guardar_capacitacion(nueva_cap)
                    st.success("¡Capacitación creada con éxito y enlace automático generado!")

                    # Notificación automática por correo a los empleados citados
                    if enviar_correo:
                        if not df_empleados.empty and 'correo' in df_empleados.columns:
                            df_destinatarios = df_empleados[df_empleados['nombre'].isin(empleados_seleccionados)]
                        else:
                            df_destinatarios = pd.DataFrame(columns=["nombre", "correo"])

                        with st.spinner("Enviando notificaciones por correo..."):
                            resultado = enviar_notificacion_capacitacion(
                                df_destinatarios,
                                nueva_cap,
                                _ruta_material(material_guardado)
                            )

                        if resultado["error_general"]:
                            st.warning(f"⚠️ La capacitación se creó, pero no se enviaron correos: {resultado['error_general']}")
                        else:
                            if resultado["enviados"]:
                                st.success(f"📧 Correo enviado a: {', '.join(resultado['enviados'])}")
                            if resultado["sin_correo"]:
                                st.warning(f"⚠️ Sin correo válido registrado: {', '.join(resultado['sin_correo'])}")
                            for nom_fallo, err in resultado["fallidos"]:
                                st.warning(f"⚠️ No se pudo enviar a {nom_fallo}: {err}")
                else:
                    st.error("Completa el nombre y selecciona al menos un empleado asistente.")

    st.markdown("---")
    st.subheader("📋 Listado de Capacitaciones Asignadas")
    df_caps = cargar_capacitaciones()
    
    if not df_caps.empty:
        # Si es un empleado normal, filtrar únicamente las capacitaciones donde esté citado
        if rol == "Usuario / Empleado":
            df_caps = df_caps[df_caps['empleados'].astype(str).str.contains(nombre_usuario, na=False)]
            
        if df_caps.empty:
            st.info("No tienes capacitaciones asignadas en este momento.")
        else:
            for index, row in df_caps.iterrows():
                h_ini = row.get('hora_inicio', '08:00')
                h_fin = row.get('hora_fin', '18:00')

                total_citados_row = len([e for e in str(row['empleados']).split(",") if e.strip()])
                df_asis_preview = cargar_asistencias()
                asistieron_n = 0
                if not df_asis_preview.empty:
                    reg_prev = df_asis_preview[
                        (df_asis_preview['capacitacion_id'] == row['id']) & (df_asis_preview['asistio'] == True)
                    ]
                    asistieron_n = len(reg_prev)
                badge_estado = f"🟢 {asistieron_n}/{total_citados_row} asistieron" if total_citados_row else "Sin citados"

                with st.expander(f"📌 {row['nombre']}  ·  {row['fecha_inicio']} ({h_ini}) → {row['fecha_fin']} ({h_fin})  ·  {badge_estado}"):
                    st.write(f"**Personal Citado:** {row['empleados']}")
                    st.write(f"**Enlace Automático de Asistencia:** [{row['link_asistencia']}]({row['link_asistencia']})")

                    # --- Material adjunto: ahora se puede descargar ---
                    nombre_material = row.get('material_nombre', 'Sin archivo')
                    if not isinstance(nombre_material, str) or not nombre_material.strip():
                        nombre_material = "Sin archivo"
                    st.write(f"**Material adjunto:** {nombre_material}")

                    ruta_mat = _ruta_material(row.get('material_ruta'))
                    if ruta_mat:
                        with open(ruta_mat, "rb") as f_mat:
                            datos_mat = f_mat.read()
                        st.download_button(
                            label="📥 Descargar material",
                            data=datos_mat,
                            file_name=nombre_material,
                            mime=mimetypes.guess_type(nombre_material)[0] or "application/octet-stream",
                            key=f"dl_material_{row['id']}"
                        )
                    elif nombre_material != "Sin archivo":
                        st.caption("⚠️ El archivo de esta capacitación no quedó guardado (se creó antes de esta corrección). Vuelve a crearla adjuntando el archivo.")
                    
                    # Generación del código QR con el enlace automático
                    qr = qrcode.QRCode(box_size=4, border=2)
                    qr.add_data(row['link_asistencia'])
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white")
                    buf = BytesIO()
                    img.save(buf)
                    buf.seek(0)
                    st.image(buf, caption="Código QR de Registro de Asistencia", width=150)

                    # Panel de asistencia (quién marcó que sí / no asistió) — solo visible
                    # para Admin y Super Admin, con el detalle de cada empleado citado.
                    if rol in ["Super Admin", "Admin"]:
                        st.markdown("""
                            <style>
                                .jm-pill { display:inline-block; padding:4px 12px; border-radius:999px;
                                    font-size:0.82rem; font-weight:600; margin:3px 4px 3px 0; }
                                .jm-pill-ok { background:rgba(76,175,80,0.15); color:#81C784; border:1px solid #4CAF50; }
                                .jm-pill-bad { background:rgba(244,67,54,0.15); color:#E57373; border:1px solid #F44336; }
                                .jm-pill-wait { background:rgba(158,158,158,0.15); color:#BDBDBD; border:1px solid #757575; }
                            </style>
                        """, unsafe_allow_html=True)

                        st.markdown("---")
                        st.markdown("##### 📊 Estado de Asistencia del Personal Citado")

                        df_asistencias = cargar_asistencias()
                        empleados_citados_row = [e.strip() for e in str(row['empleados']).split(",") if e.strip()]

                        if not df_asistencias.empty:
                            registros_cap = df_asistencias[df_asistencias['capacitacion_id'] == row['id']]
                        else:
                            registros_cap = pd.DataFrame()

                        asistieron, no_asistieron, pendientes = [], [], []
                        for emp in empleados_citados_row:
                            if not registros_cap.empty and emp in registros_cap['empleado_nombre'].values:
                                reg_emp = registros_cap[registros_cap['empleado_nombre'] == emp].iloc[0]
                                (asistieron if bool(reg_emp['asistio']) else no_asistieron).append(emp)
                            else:
                                pendientes.append(emp)

                        total_citados = len(empleados_citados_row)
                        porcentaje = int((len(asistieron) / total_citados) * 100) if total_citados else 0

                        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                        col_m1.metric("👥 Citados", total_citados)
                        col_m2.metric("✅ Asistieron", len(asistieron))
                        col_m3.metric("❌ No asistieron", len(no_asistieron))
                        col_m4.metric("⏳ Pendientes", len(pendientes))

                        st.progress(porcentaje / 100, text=f"📈 {porcentaje}% de asistencia confirmada")
                        st.write("")

                        col_r1, col_r2, col_r3 = st.columns(3)
                        with col_r1:
                            st.markdown("**✅ Asistieron**")
                            if asistieron:
                                st.markdown("".join(f"<span class='jm-pill jm-pill-ok'>{e}</span>" for e in asistieron), unsafe_allow_html=True)
                            else:
                                st.caption("Nadie registrado aún.")
                        with col_r2:
                            st.markdown("**❌ No asistieron**")
                            if no_asistieron:
                                st.markdown("".join(f"<span class='jm-pill jm-pill-bad'>{e}</span>" for e in no_asistieron), unsafe_allow_html=True)
                            else:
                                st.caption("Nadie registrado aún.")
                        with col_r3:
                            st.markdown("**⏳ Sin registrar**")
                            if pendientes:
                                st.markdown("".join(f"<span class='jm-pill jm-pill-wait'>{e}</span>" for e in pendientes), unsafe_allow_html=True)
                            else:
                                st.caption("¡Todos ya registraron!")

                    st.markdown("---")
                    st.markdown("##### 📤 Subir Evidencia de Asistencia")
                    st.markdown("Adjunta tu soporte de participación (Formatos permitidos: `.png`, `.jpg`, `.pdf`, `.docx`).")
                    
                    with st.form(key=f"form_evidencia_{row['id']}"):
                        evidencia_file = st.file_uploader(
                            "Seleccionar archivo de evidencia", 
                            type=["png", "jpg", "jpeg", "pdf", "docx"],
                            key=f"file_ev_{row['id']}"
                        )
                        btn_subir_ev = st.form_submit_button("💾 Guardar Evidencia", type="primary")
                        
                        if btn_subir_ev:
                            if evidencia_file is not None:
                                st.success(f"¡Evidencia '{evidencia_file.name}' cargada y guardada exitosamente para la capacitación '{row['nombre']}'!")
                            else:
                                st.error("Por favor selecciona un archivo antes de guardar.")
    else:
        st.info("No hay capacitaciones registradas en el sistema.")