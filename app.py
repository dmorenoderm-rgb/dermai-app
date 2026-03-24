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

# =======================
# DB
# =======================
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
        "estado_director TEXT,"
        "estado_farmacia TEXT,"
        "comentario_director TEXT,"
        "comentario_farmacia TEXT,"
        "fecha_solicitud TEXT,"
        "fecha_director TEXT,"
        "fecha_farmacia TEXT,"
        "director TEXT,"
        "farmacia TEXT)"
    )

    conn.commit()
    conn.close()

init_db()

# =======================
# SOLICITANTES
# =======================
solicitantes = [
    "Dra. Carrizosa","Dra. Conejo-Mir","Dr. de la Torre","Dra. Eiris",
    "Dra. Fernández Orland","Dra. Ferrándiz","Dra. García Morales",
    "Dr. Marcos","Dra. Ojeda","Dr. Ruiz de Casas","Dra. Ruz",
    "Dra. Sánchez del Campo","Dr. Sánchez Leiro","Dra. Serrano",
]

# =======================
# PROTOCOLOS COMPLETOS
# =======================
protocolos = {
    "Psoriasis en placas": {
        "texto": "1º Adalimumab → 2º Ustekinumab → 3º Tildrakizumab → 4º Bimekizumab",
        "drugs": [
            "Adalimumab 40 mg cada 2 semanas",
            "Ustekinumab 45 mg cada 12 semanas",
            "Ustekinumab 90 mg cada 12 semanas",
            "Secukinumab 300 mg cada 4 semanas",
            "Ixekizumab 80 mg cada 4 semanas",
            "Guselkumab 100 mg cada 8 semanas",
            "Risankizumab 150 mg cada 12 semanas",
            "Tildrakizumab 100 mg cada 12 semanas",
            "Bimekizumab 320 mg cada 8 semanas",
        ],
    },
    "Dermatitis atópica": {
        "texto": "1º Dupilumab → 2º Tralokinumab → 3º JAK",
        "drugs": [
            "Dupilumab 300 mg cada 2 semanas",
            "Tralokinumab 300 mg cada 2 semanas",
            "Tralokinumab 300 mg cada 4 semanas",
            "Lebrikizumab 250 mg cada 2 semanas",
            "Lebrikizumab 250 mg cada 4 semanas",
            "Upadacitinib 15 mg",
            "Upadacitinib 30 mg",
            "Baricitinib 2 mg",
            "Baricitinib 4 mg",
            "Abrocitinib 100 mg",
            "Abrocitinib 200 mg",
        ],
    },
    "Hidradenitis supurativa": {
        "texto": "Adalimumab primera línea",
        "drugs": [
            "Adalimumab semanal",
            "Secukinumab 300 mg cada 4 semanas",
            "Bimekizumab 320 mg cada 4 semanas",
        ],
    },
    "Urticaria crónica espontánea": {
        "texto": "Omalizumab",
        "drugs": ["Omalizumab 300 mg cada 4 semanas"],
    },
    "Alopecia areata": {
        "texto": "JAK",
        "drugs": [
            "Baricitinib 2 mg",
            "Baricitinib 4 mg",
            "Ritlecitinib 50 mg",
        ],
    },
    "Vitíligo": {
        "texto": "Ruxolitinib tópico",
        "drugs": ["Ruxolitinib crema 1,5%"],
    },
    "Melanoma": {
        "texto": "Inmunoterapia",
        "drugs": [
            "Nivolumab 240 mg cada 2 semanas",
            "Nivolumab 480 mg cada 4 semanas",
            "Pembrolizumab 200 mg cada 3 semanas",
            "Pembrolizumab 400 mg cada 6 semanas",
        ],
    },
    "Carcinoma basocelular": {
        "texto": "Hedgehog",
        "drugs": [
            "Vismodegib 150 mg diario",
            "Sonidegib 200 mg diario",
        ],
    },
    "Carcinoma escamoso cutáneo": {
        "texto": "Anti-PD1",
        "drugs": [
            "Cemiplimab 350 mg cada 3 semanas",
            "Pembrolizumab 200 mg cada 3 semanas",
            "Pembrolizumab 400 mg cada 6 semanas",
        ],
    },
}

# =======================
# NUEVA SOLICITUD
# =======================
if role == "Dermatólogo":

    paciente = st.text_input("Paciente (AN + 10 dígitos)", value="AN")
    solicitante = st.selectbox("Solicitante", ["Seleccionar"] + solicitantes)
    enfermedad = st.selectbox("Enfermedad", ["Seleccionar"] + list(protocolos.keys()))

    if enfermedad != "Seleccionar":
        st.info(protocolos[enfermedad]["texto"])
        tratamiento = st.selectbox("Tratamiento", protocolos[enfermedad]["drugs"])
    else:
        tratamiento = None

    if st.button("Enviar solicitud"):

        if solicitante == "Seleccionar":
            st.error("Seleccione solicitante")
        elif enfermedad == "Seleccionar":
            st.error("Seleccione enfermedad")
        elif not re.fullmatch(r"AN\d{10}", paciente):
            st.error("Formato incorrecto")
        else:
            conn = get_conn()
            c = conn.cursor()

            c.execute(
                "INSERT INTO requests VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    str(uuid.uuid4()),
                    paciente,
                    solicitante,
                    enfermedad,
                    tratamiento,
                    "Pendiente",
                    "",
                    "",
                    "",
                    datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "",
                    "",
                    "",
                    "",
                ),
            )

            conn.commit()
            conn.close()
            st.success("Solicitud creada")
            st.rerun()

# =======================
# LISTADO
# =======================
conn = get_conn()
df = pd.read_sql_query("SELECT * FROM requests ORDER BY fecha_solicitud DESC", conn)
conn.close()

if not df.empty:
    st.dataframe(df[["paciente","solicitante","enfermedad","tratamiento","estado_director"]])
