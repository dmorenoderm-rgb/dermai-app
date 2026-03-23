import streamlit as st
import sqlite3
import hashlib
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
# DB SETUP
# =======================
def get_connection():
    return sqlite3.connect(DB, check_same_thread=False)


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # tabla usuarios
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # tabla solicitudes
    c.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id TEXT PRIMARY KEY,
        paciente TEXT,
        solicitante TEXT,
        usuario_solicitud TEXT,
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

    # crear usuarios por defecto
    users = [
        ("director", hash_password("123"), "Director de Derma"),
        ("farmacia", hash_password("123"), "Farmacia"),
        ("derma", hash_password("123"), "Dermatólogo"),
    ]

    for u in users:
        try:
            c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (str(uuid.uuid4()), u[0], u[1], u[2]))
        except:
            pass

    conn.commit()
    conn.close()


def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()


init_db()

# =======================
# LOGIN
# =======================
if "user" not in st.session_state:
    st.session_state.user = None


def login():
    st.sidebar.subheader("Login")
    user = st.sidebar.text_input("Usuario")
    password = st.sidebar.text_input("Contraseña", type="password")

    if st.sidebar.button("Entrar"):
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT username, password, role FROM users WHERE username=?", (user,))
        result = c.fetchone()
        conn.close()

        if result and result[1] == hash_password(password):
            st.session_state.user = {
                "username": result[0],
                "role": result[2]
            }
            st.rerun()
        else:
            st.sidebar.error("Credenciales incorrectas")


if st.session_state.user is None:
    login()
    st.stop()

usuario = st.session_state.user["username"]
role = st.session_state.user["role"]

st.sidebar.success(f"Usuario: {usuario}")
st.sidebar.info(f"Rol: {role}")

if st.sidebar.button("Cerrar sesión"):
    st.session_state.user = None
    st.rerun()

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

            c.execute("INSERT INTO requests VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (
                str(uuid.uuid4()),
                paciente,
                usuario,
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
# LISTADO
# =======================
st.subheader("Solicitudes")

conn = get_connection()
df = pd.read_sql_query("SELECT * FROM requests ORDER BY fecha_solicitud DESC", conn)
conn.close()

st.dataframe(df, use_container_width=True)

# =======================
# ACCIONES
# =======================
for i, r in df.iterrows():
    st.write("---")
    st.write(f"Paciente: {r['paciente']} | {r['tratamiento']}")

    conn = get_connection()
    c = conn.cursor()

    # DIRECTOR
    if role == "Director de Derma" and r['estado_director'] == "Pendiente":
        col1, col2 = st.columns(2)

        if col1.button("Validar", key=f"val_{i}"):
            c.execute("UPDATE requests SET estado_director=?, fecha_director=?, director=? WHERE id=?", (
                "Validado",
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                usuario,
                r['id']
            ))
            conn.commit()
            st.rerun()

        if col2.button("No validar", key=f"noval_{i}"):
            c.execute("UPDATE requests SET estado_director=?, fecha_director=?, director=? WHERE id=?", (
                "No validado",
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                usuario,
                r['id']
            ))
            conn.commit()
            st.rerun()

    # FARMACIA
    if role == "Farmacia" and r['estado_director'] == "Validado" and r['estado_farmacia'] == "":
        col1, col2 = st.columns(2)

        if col1.button("Dispensar", key=f"disp_{i}"):
            c.execute("UPDATE requests SET estado_farmacia=?, fecha_farmacia=?, farmacia=? WHERE id=?", (
                "Pendiente de dispensación",
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                usuario,
                r['id']
            ))
            conn.commit()
            st.rerun()

        if col2.button("Rechazar", key=f"rech_{i}"):
            c.execute("UPDATE requests SET estado_farmacia=?, fecha_farmacia=?, farmacia=? WHERE id=?", (
                "No validado",
                datetime.now().strftime("%d/%m/%Y %H:%M"),
                usuario,
                r['id']
            ))
            conn.commit()
            st.rerun()

    conn.close()

    # ESTADOS
    if r['estado_director'] == "Pendiente":
        st.warning("Pendiente Director")
    elif r['estado_director'] == "No validado":
        st.error("Rechazado Director")
    elif r['estado_farmacia'] == "":
        st.info("Pendiente Farmacia")
    elif r['estado_farmacia'] == "Pendiente de dispensación":
        st.success("Dispensación en curso")
    elif r['estado_farmacia'] == "No validado":
        st.error("Rechazado Farmacia")
