import pandas as pd
import bcrypt
from database.conexion import obtener_motor

engine = obtener_motor()
TABLA_RIESGOS = "matriz_riesgos"
TABLA_CAPACITACIONES = "capacitaciones"
TABLA_EMPLEADOS = "empleados_usuarios"
TABLA_ASISTENCIAS = "asistencias_capacitaciones"

def cargar_datos_db():
    try:
        with engine.connect() as conn:
            df = pd.read_sql(f"SELECT * FROM {TABLA_RIESGOS}", conn)
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].apply(lambda x: x.encode('latin1', errors='ignore').decode('utf-8', errors='ignore') if isinstance(x, str) else x)
            return df
    except Exception as e:
        return pd.DataFrame()

def guardar_datos_db(df_editado):
    with engine.begin() as conn:
        df_editado.to_sql(TABLA_RIESGOS, conn, if_exists='replace', index=False)

def cargar_capacitaciones():
    try:
        with engine.connect() as conn:
            return pd.read_sql(f"SELECT * FROM {TABLA_CAPACITACIONES}", conn)
    except:
        return pd.DataFrame(columns=["id", "nombre", "empleados", "fecha_inicio", "fecha_fin", "link_asistencia", "material_nombre"])

def guardar_capacitacion(nueva_cap):
    df_caps = cargar_capacitaciones()
    df_nueva = pd.DataFrame([nueva_cap])
    df_final = pd.concat([df_caps, df_nueva], ignore_index=True)
    with engine.begin() as conn:
        df_final.to_sql(TABLA_CAPACITACIONES, conn, if_exists='replace', index=False)

# --- GESTIÓN DE EMPLEADOS Y USUARIOS ---
def cargar_empleados():
    try:
        with engine.connect() as conn:
            return pd.read_sql(f"SELECT * FROM {TABLA_EMPLEADOS}", conn)
    except:
        return pd.DataFrame(columns=[
            "id", "nombre", "correo", "celular", "direccion", 
            "cargo", "puede_editar", "rol", "username", "password_hash"
        ])

def guardar_empleado(nuevo_empleado):
    df_emp = cargar_empleados()
    df_nuevo = pd.DataFrame([nuevo_empleado])
    df_final = pd.concat([df_emp, df_nuevo], ignore_index=True)
    with engine.begin() as conn:
        df_final.to_sql(TABLA_EMPLEADOS, conn, if_exists='replace', index=False)

# --- CAPACITACIÓN POR ID (para la vista pública de registro de asistencia) ---
def obtener_capacitacion_por_id(cap_id):
    df_caps = cargar_capacitaciones()
    if df_caps.empty or 'id' not in df_caps.columns:
        return None
    try:
        cap_id = int(cap_id)
    except (TypeError, ValueError):
        return None
    resultado = df_caps[df_caps['id'] == cap_id]
    if resultado.empty:
        return None
    return resultado.iloc[0]

# --- GESTIÓN DE ASISTENCIA A CAPACITACIONES (registro vía QR / enlace) ---
def cargar_asistencias():
    try:
        with engine.connect() as conn:
            return pd.read_sql(f"SELECT * FROM {TABLA_ASISTENCIAS}", conn)
    except Exception:
        return pd.DataFrame(columns=[
            "id", "capacitacion_id", "capacitacion_nombre", "empleado_nombre",
            "fecha_capacitacion", "asistio", "fecha_registro"
        ])

def guardar_asistencia(registro):
    """Guarda o actualiza el registro de asistencia de un empleado a una capacitación.
    Si el empleado ya tiene un registro para esa misma capacitación, se reemplaza
    (para permitir que corrija su respuesta si se equivoca al marcar)."""
    df_asis = cargar_asistencias()

    if not df_asis.empty:
        mask = (
            (df_asis['capacitacion_id'] == registro['capacitacion_id']) &
            (df_asis['empleado_nombre'] == registro['empleado_nombre'])
        )
        df_asis = df_asis[~mask]

    df_nuevo = pd.DataFrame([registro])
    df_final = pd.concat([df_asis, df_nuevo], ignore_index=True)
    with engine.begin() as conn:
        df_final.to_sql(TABLA_ASISTENCIAS, conn, if_exists='replace', index=False)

def verificar_credenciales(username, password):
    df_emp = cargar_empleados()
    if df_emp.empty:
        return None
    
    usuario = df_emp[df_emp['username'] == username]
    if usuario.empty:
        return None
    
    user_data = usuario.iloc[0]
    hashed_password = user_data['password_hash'].encode('utf-8')
    
    if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
        return {
            "nombre": user_data['nombre'],
            "rol": user_data['rol'],
            "puede_editar": bool(user_data['puede_editar']),
            "correo": user_data['correo']
        }
    return None