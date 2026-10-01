import os
import html
import smtplib
import mimetypes
from email.message import EmailMessage
from email.utils import formataddr

import streamlit as st

LIMITE_ADJUNTO_MB = 15


def _config_smtp():
    cfg = {}
    try:
        cfg = dict(st.secrets["email"])
    except Exception:
        pass
    return {
        "servidor": cfg.get("servidor") or os.getenv("SMTP_SERVIDOR", "smtp.gmail.com"),
        "puerto": int(cfg.get("puerto") or os.getenv("SMTP_PUERTO", 587)),
        # Quitamos espacios: las "Contraseñas de aplicación" de Google se copian
        # como "abcd efgh ijkl mnop" y los espacios rompen la autenticación.
        "usuario": (cfg.get("usuario") or os.getenv("SMTP_USUARIO", "")).strip(),
        "password": (cfg.get("password") or os.getenv("SMTP_PASSWORD", "")).replace(" ", "").strip(),
        "remitente": cfg.get("remitente") or "INGENIERÍA Y SUMINISTROS J&M S.A.S.",
    }


def _construir_mensaje(cfg, nombre, correo, cap, adjunto):
    msg = EmailMessage()
    msg["Subject"] = f"📚 Nueva capacitación asignada: {cap['nombre']}"
    msg["From"] = formataddr((cfg["remitente"], cfg["usuario"]))
    msg["To"] = correo

    nom = html.escape(str(nombre))
    cap_nombre = html.escape(str(cap["nombre"]))
    inicio = f"{cap['fecha_inicio']} {cap['hora_inicio']}"
    fin = f"{cap['fecha_fin']} {cap['hora_fin']}"
    link = str(cap.get("link_asistencia", ""))
    material = str(cap.get("material_nombre", "Sin archivo"))

    texto = (
        f"Hola {nombre},\n\n"
        f"Se te ha asignado una nueva capacitación:\n\n"
        f"Capacitación: {cap['nombre']}\n"
        f"Inicio: {inicio}\n"
        f"Fin: {fin}\n"
        f"Material: {material}\n"
        f"Registro de asistencia: {link}\n\n"
        f"También puedes ingresar a la plataforma para ver y descargar el material.\n\n"
        f"{cfg['remitente']}"
    )
    msg.set_content(texto)

    cuerpo_html = f"""
    <div style="font-family:Arial,sans-serif;max-width:560px;margin:auto;border:1px solid #ddd;border-radius:10px;overflow:hidden;">
      <div style="background:#121212;padding:16px 20px;">
        <h2 style="color:#FFC107;margin:0;font-size:18px;">{html.escape(cfg['remitente'])}</h2>
      </div>
      <div style="padding:20px;color:#222;">
        <p>Hola <b>{nom}</b>,</p>
        <p>Se te ha asignado una nueva capacitación:</p>
        <table style="width:100%;border-collapse:collapse;font-size:14px;">
          <tr><td style="padding:6px 0;"><b>🎓 Capacitación:</b></td><td>{cap_nombre}</td></tr>
          <tr><td style="padding:6px 0;"><b>🕒 Inicio:</b></td><td>{html.escape(inicio)}</td></tr>
          <tr><td style="padding:6px 0;"><b>🕔 Fin:</b></td><td>{html.escape(fin)}</td></tr>
          <tr><td style="padding:6px 0;"><b>📎 Material:</b></td><td>{html.escape(material)}</td></tr>
        </table>
        <p style="margin-top:18px;">
          <a href="{html.escape(link)}" style="background:#FFC107;color:#000;padding:10px 18px;border-radius:6px;text-decoration:none;font-weight:bold;">
            Registrar asistencia
          </a>
        </p>
        <p style="font-size:12px;color:#777;">También puedes ingresar a la plataforma para ver y descargar el material.</p>
      </div>
    </div>
    """
    msg.add_alternative(cuerpo_html, subtype="html")

    if adjunto:
        nombre_adj, datos = adjunto
        tipo, _ = mimetypes.guess_type(nombre_adj)
        maintype, subtype = (tipo or "application/octet-stream").split("/", 1)
        msg.add_attachment(datos, maintype=maintype, subtype=subtype, filename=nombre_adj)

    return msg


def _conectar(cfg, modo):
    """modo: 'starttls' (587) o 'ssl' (465)."""
    if modo == "ssl":
        servidor = smtplib.SMTP_SSL(cfg["servidor"], 465, timeout=20)
    else:
        servidor = smtplib.SMTP(cfg["servidor"], cfg["puerto"] or 587, timeout=20)
        servidor.ehlo()
        servidor.starttls()
        servidor.ehlo()
    servidor.login(cfg["usuario"], cfg["password"])
    return servidor


def _mensaje_amigable(error: Exception) -> str:
    txt = str(error)
    if isinstance(error, smtplib.SMTPAuthenticationError) or "Username and Password not accepted" in txt:
        return (
            "Gmail rechazó el usuario/contraseña. Debes usar una **Contraseña de aplicación** de 16 "
            "caracteres (no la contraseña normal de la cuenta). Genera una en "
            "https://myaccount.google.com/apppasswords (requiere verificación en 2 pasos activada) "
            "y pégala sin espacios en .streamlit/secrets.toml."
        )
    if "Connection unexpectedly closed" in txt or isinstance(error, (smtplib.SMTPServerDisconnected, ConnectionResetError)):
        return (
            "El servidor de Gmail cerró la conexión al autenticar. Casi siempre significa que el "
            "'password' en secrets.toml es la contraseña normal de la cuenta en vez de una "
            "Contraseña de aplicación de 16 caracteres, o que tiene espacios. Genera una nueva en "
            "https://myaccount.google.com/apppasswords."
        )
    return f"{txt}"


def enviar_notificacion_capacitacion(df_destinatarios, cap, ruta_material=None):
    """
    df_destinatarios: DataFrame con columnas 'nombre' y 'correo'
    cap: dict de la capacitación
    ruta_material: ruta completa del archivo a adjuntar (opcional)

    Devuelve: {"enviados": [...], "sin_correo": [...], "fallidos": [(nombre, error)], "error_general": str|None}
    """
    resultado = {"enviados": [], "sin_correo": [], "fallidos": [], "error_general": None}
    cfg = _config_smtp()

    if not cfg["usuario"] or not cfg["password"]:
        resultado["error_general"] = (
            "No hay credenciales de correo configuradas (archivo .streamlit/secrets.toml)."
        )
        return resultado

    # Adjuntar el material solo si no supera el límite
    adjunto = None
    if ruta_material and os.path.exists(ruta_material):
        tam_mb = os.path.getsize(ruta_material) / (1024 * 1024)
        if tam_mb <= LIMITE_ADJUNTO_MB:
            with open(ruta_material, "rb") as f:
                adjunto = (str(cap.get("material_nombre", os.path.basename(ruta_material))), f.read())

    # Separar quienes tienen correo válido
    destinos = []
    for _, fila in df_destinatarios.iterrows():
        correo = str(fila.get("correo", "") or "").strip()
        if "@" in correo:
            destinos.append((fila["nombre"], correo))
        else:
            resultado["sin_correo"].append(fila["nombre"])

    if not destinos:
        return resultado

    # Intenta primero con el modo configurado (587/STARTTLS por defecto) y,
    # si falla por conexión, reintenta automáticamente con el otro modo (465/SSL).
    modo_inicial = "ssl" if cfg["puerto"] == 465 else "starttls"
    modo_alterno = "starttls" if modo_inicial == "ssl" else "ssl"

    servidor = None
    ultimo_error = None
    for modo in (modo_inicial, modo_alterno):
        try:
            servidor = _conectar(cfg, modo)
            break
        except Exception as e:
            ultimo_error = e
            servidor = None

    if servidor is None:
        resultado["error_general"] = f"No se pudo conectar/autenticar con el servidor de correo: {_mensaje_amigable(ultimo_error)}"
        return resultado

    try:
        for nombre, correo in destinos:
            try:
                msg = _construir_mensaje(cfg, nombre, correo, cap, adjunto)
                servidor.send_message(msg)
                resultado["enviados"].append(nombre)
            except Exception as e:
                resultado["fallidos"].append((nombre, _mensaje_amigable(e)))
    finally:
        try:
            servidor.quit()
        except Exception:
            pass

    return resultado
