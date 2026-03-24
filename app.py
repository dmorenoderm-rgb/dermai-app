import streamlit as st
import sqlite3
import uuid
from datetime import datetime
import pandas as pd
import re

# =======================
# CONFIG
# =======================
st.set_page_config(layout="wide")
st.title("DerMAI PRO")
st.write("Gestión de Medicamentos de Alto Impacto en Dermatología HUVM")

DB = "dermai.db"

# =======================
# USUARIOS
# =======================
USUARIOS = {
    "director": {"password": "123", "rol": "Director de Derma"},
    "farmacia": {"password": "123", "rol": "Farmacia"},
    "derma": {"password": "123", "rol": "Dermatólogo"},
}

# =======================
# LOGIN
# =======================
if "user" not in st.session_state:
    st.session_state.user = None

st.sidebar.subheader("Login")
user = st.sidebar.text_input("Usuario")
password = st.sidebar.text_input("Contraseña", type="password")

if st.sidebar.button("Entrar"):
    if user in USUARIOS and USUARIOS[user]["password"] == password:
        st.session_state.user = {
            "username": user,
            "role": USUARIOS[user]["rol"]
        }
        st.rerun()
    else:
        st.sidebar.error("Credenciales incorrectas")

if st.session_state.user is None:
    st.stop()

usuario = st.session_state.user["username"]
role = st.session_state.user["role"]

st.sidebar.success(f"Usuario: {usuario}")
st.sidebar.info(f"Rol: {role}")

if st.sidebar.button("Cerrar sesión"):
    st.session_state.user = None
    st.rerun()

# =======================
# DB
# =======================
def get_connection():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id TEXT PRIMARY KEY,
        paciente TEXT,
        solicitante TEXT,
        enfermedad TEXT,
        tratamiento TEXT,
        estado_director TEXT,
        estado_farmacia TEXT,
        fecha_solicitud TEXT,
        fecha_director TEXT,
        fecha_farmacia TEXT,
        director TEXT,
        farmacia TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =======================
# PROTOCOLOS
# =======================
protocolos = {
    "Psoriasis en placas": {
        "texto": "1º Adalimumab → 2º Ustekinumab → 3º Tildrakizumab → 4º Bimekizumab",
        "drugs": [
            "Adalimumab 40 mg/2 semanas",
            "Ustekinumab 45 mg/12 semanas",
            "Ustekinumab 90 mg/12 semanas",
            "Secukinumab 300 mg/4 semanas",
            "Ixekizumab 80 mg/4 semanas",
            "Guselkumab 100 mg/8 semanas",
            "Risankizumab 150 mg/12 semanas",
            "Tildrakizumab 100 mg/12 semanas",
            "Bimekizumab 320 mg/8 semanas",
        ],
    }
}

# =======================
# NUEVA SOLICITUD
# =======================
if role == "Dermatólogo":
    st.subheader("Nueva solicitud")

    paciente = st.text_input("Paciente (AN + 10 dígitos)", value="AN")
    enfermedad = st.selectbox("Enfermedad", list(protocolos.keys()))
    tratamiento = st.selectbox("Tratamiento", protocolos[enfermedad]["drugs"])

    if st.button("Enviar solicitud"):
        paciente = paciente.strip().upper()

        if not re.fullmatch(r"AN\d{10}", paciente):
            st.error("Formato incorrecto")
        else:
            conn = get_connection()
            c = conn.cursor()

            c.execute("""
            INSERT INTO requests (
                id,
                paciente,
                solicitante,
                enfermedad,
                tratamiento,
                estado_director,
                estado_farmacia,
                fecha_solicitud,
                fecha_director,
                fecha_farmacia,
                director,
                farmacia
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                paciente,
                usuario,
                enfermedad,
                tratamiento,
                "Pendiente",
                "",
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                "",
                "",
                "",
                ""
            ))

            conn.commit()
            conn.close()

            st.success("Solicitud creada")
            st.rerun()

# =======================
# ESTADO GLOBAL
# =======================
def estado_global(r):
    if r["estado_director"] == "Pendiente":
        return "Pendiente Director"
    elif r["estado_director"] == "No validado":
        return "Rechazado Director"
    elif r["estado_farmacia"] == "":
        return "Pendiente Farmacia"
    elif r["estado_farmacia"] == "Pendiente de dispensación":
        return "En dispensación"
    elif r["estado_farmacia"] == "No validado":
        return "Rechazado Farmacia"

# =======================
# LISTADO
# =======================
st.subheader("Solicitudes")

conn = get_connection()
df = pd.read_sql_query("SELECT * FROM requests ORDER BY fecha_solicitud DESC", conn)
conn.close()

if not df.empty:
    df["Estado"] = df.apply(estado_global, axis=1)

    df_view = df[["paciente", "tratamiento", "Estado", "fecha_solicitud"]]
    st.dataframe(df_view, use_container_width=True)

# =======================
# ACCIONES
# =======================
for i, r in df.iterrows():
    st.write("---")
    st.write(f"Paciente: {r['paciente']} | {r['tratamiento']}")

    conn = get_connection()
    c = conn.cursor()

    # DIRECTOR
    if role == "Director de Derma" and r["estado_director"] == "Pendiente":
        col1, col2, col3 = st.columns(3)

        if col1.button("Validar", key=f"val_{i}"):
            c.execute("""
            UPDATE requests SET estado_director=?, fecha_director=?, director=? WHERE id=?
            """, ("Validado", datetime.now().strftime("%d/%m/%Y %H:%M"), usuario, r["id"]))
            conn.commit()
            st.rerun()

        if col2.button("Rechazar", key=f"noval_{i}"):
            c.execute("""
            UPDATE requests SET estado_director=?, fecha_director=?, director=? WHERE id=?
            """, ("No validado", datetime.now().strftime("%d/%m/%Y %H:%M"), usuario, r["id"]))
            conn.commit()
            st.rerun()

        if col3.button("Eliminar", key=f"del_{i}"):
            st.warning("⚠️ Confirmar eliminación")
            if st.button("Confirmar", key=f"confirm_{i}"):
                c.execute("DELETE FROM requests WHERE id=?", (r["id"],))
                conn.commit()
                st.success("Registro eliminado")
                st.rerun()

    # FARMACIA
    if role == "Farmacia" and r["estado_director"] == "Validado" and r["estado_farmacia"] == "":
        col1, col2 = st.columns(2)

        if col1.button("Dispensar", key=f"disp_{i}"):
            c.execute("""
            UPDATE requests SET estado_farmacia=?, fecha_farmacia=?, farmacia=? WHERE id=?
            """, ("Pendiente de dispensación", datetime.now().strftime("%d/%m/%Y %H:%M"), usuario, r["id"]))
            conn.commit()
            st.rerun()

        if col2.button("Rechazar", key=f"rech_{i}"):
            c.execute("""
            UPDATE requests SET estado_farmacia=?, fecha_farmacia=?, farmacia=? WHERE id=?
            """, ("No validado", datetime.now().strftime("%d/%m/%Y %H:%M"), usuario, r["id"]))
            conn.commit()
            st.rerun()

    conn.close()
