import streamlit as st
import sqlite3
import uuid
from datetime import datetime
import pandas as pd
import re

st.set_page_config(layout="wide")
st.title("DerMAI PRO")

DB = "dermai.db"

# ======================
# LOGIN SIMPLE
# ======================
USUARIOS = {
    "director": {"password": "123", "rol": "Director de Derma"},
    "farmacia": {"password": "123", "rol": "Farmacia"},
    "derma": {"password": "123", "rol": "Dermatólogo"},
}

if "user" not in st.session_state:
    st.session_state.user = None

user = st.sidebar.text_input("Usuario")
password = st.sidebar.text_input("Contraseña", type="password")

if st.sidebar.button("Entrar"):
    if user in USUARIOS and USUARIOS[user]["password"] == password:
        st.session_state.user = {"username": user, "role": USUARIOS[user]["rol"]}
        st.rerun()
    else:
        st.sidebar.error("Credenciales incorrectas")

if st.session_state.user is None:
    st.stop()

usuario = st.session_state.user["username"]
role = st.session_state.user["role"]

# ======================
# DB
# ======================
def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute(
        "CREATE TABLE IF NOT EXISTS requests ("
        "id TEXT PRIMARY KEY,"
        "paciente TEXT,"
        "solicitante TEXT,"
        "enfermedad TEXT,"
        "tratamiento TEXT,"
        "estado TEXT,"
        "fecha TEXT)"
    )

    conn.commit()
    conn.close()

init_db()

# ======================
# SOLICITANTES
# ======================
solicitantes = [
    "Dra. Carrizosa","Dra. Conejo-Mir","Dr. de la Torre","Dra. Eiris",
    "Dra. Fernández Orland","Dra. Ferrándiz","Dra. García Morales",
    "Dr. Marcos","Dra. Ojeda","Dr. Ruiz de Casas","Dra. Ruz",
    "Dra. Sánchez del Campo","Dr. Sánchez Leiro","Dra. Serrano",
]

# ======================
# PROTOCOLOS
# ======================
protocolos = {
    "Psoriasis": [
        "Adalimumab",
        "Ustekinumab",
        "Bimekizumab"
    ],
    "Dermatitis atópica": [
        "Dupilumab",
        "Tralokinumab",
        "Upadacitinib"
    ]
}

# ======================
# NUEVA SOLICITUD
# ======================
if role == "Dermatólogo":

    paciente = st.text_input("Paciente (AN + 10 dígitos)", value="AN")
    solicitante = st.selectbox("Solicitante", ["Seleccionar"] + solicitantes)
    enfermedad = st.selectbox("Enfermedad", ["Seleccionar"] + list(protocolos.keys()))

    if enfermedad != "Seleccionar":
        tratamiento = st.selectbox("Tratamiento", protocolos[enfermedad])
    else:
        tratamiento = None

    if st.button("Enviar"):

        if solicitante == "Seleccionar":
            st.error("Selecciona solicitante")

        elif enfermedad == "Seleccionar":
            st.error("Selecciona enfermedad")

        elif not re.fullmatch(r"AN\d{10}", paciente):
            st.error("Formato incorrecto")

        else:
            conn = get_conn()
            c = conn.cursor()

            c.execute(
                "INSERT INTO requests VALUES (?,?,?,?,?,?,?)",
                (
                    str(uuid.uuid4()),
                    paciente,
                    solicitante,
                    enfermedad,
                    tratamiento,
                    "Pendiente",
                    datetime.now().strftime("%d/%m/%Y %H:%M"),
                ),
            )

            conn.commit()
            conn.close()

            st.success("OK")
            st.rerun()

# ======================
# LISTADO
# ======================
conn = get_conn()
df = pd.read_sql_query("SELECT * FROM requests", conn)
conn.close()

if not df.empty:
    st.dataframe(df)
