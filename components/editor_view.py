import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_loader import guardar_datos_db
from utils.exportadores import generar_excel_riesgos, generar_pdf_riesgos


def _bloque_exportacion(df_para_exportar: pd.DataFrame):
    """Muestra los botones para descargar la matriz de riesgos actual
    en formato .xlsx y .pdf."""
    if df_para_exportar is None or df_para_exportar.empty:
        return

    st.markdown("##### 📤 Exportar Matriz")
    col_pdf, col_xlsx = st.columns(2)
    marca_tiempo = datetime.now().strftime("%Y%m%d_%H%M")

    with col_pdf:
        try:
            pdf_bytes = generar_pdf_riesgos(df_para_exportar)
            st.download_button(
                label="📄 Descargar PDF",
                data=pdf_bytes,
                file_name=f"matriz_riesgos_{marca_tiempo}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"No se pudo generar el PDF: {e}")

    with col_xlsx:
        try:
            xlsx_bytes = generar_excel_riesgos(df_para_exportar)
            st.download_button(
                label="📊 Descargar Excel (.xlsx)",
                data=xlsx_bytes,
                file_name=f"matriz_riesgos_{marca_tiempo}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"No se pudo generar el Excel: {e}")


def render_editor(df, volver_dashboard_callback):
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
        st.title("📝 Editor de Registros - Matriz de Riesgos")

    # Permiso habilitado para que cualquier usuario o empleado pueda editar la tabla de riesgos
    st.markdown("Añade, edita celdas o elimina filas de la matriz de riesgos sincronizada con la base de datos.")

    if not df.empty:
        df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="editor_interactivo_riesgos")

        col_guardar, _ = st.columns([1, 3])
        with col_guardar:
            if st.button("💾 Guardar cambios en la Base de Datos", type="primary"):
                try:
                    guardar_datos_db(df_editado)
                    st.cache_data.clear()
                    st.success("¡Cambios en la matriz de riesgos guardados correctamente!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

        st.markdown("---")
        _bloque_exportacion(df_editado)
    else:
        st.warning("La tabla está vacía. Crea una estructura inicial abajo:")
        df_vacio = pd.DataFrame(columns=["id", "riesgo", "nivel"])
        df_editado = st.data_editor(df_vacio, num_rows="dynamic", use_container_width=True, key="editor_vacio_riesgos")

        if st.button("💾 Crear Tabla y Guardar", type="primary"):
            try:
                guardar_datos_db(df_editado)
                st.cache_data.clear()
                st.success("¡Tabla de riesgos creada con éxito!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")