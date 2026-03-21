import streamlit as st
import re
import json
from datetime import datetime
import pandas as pd

st.set_page_config(layout="wide")

st.title("DerMAI")
st.write("Gestión de Medicamentos de Alto Impacto en Dermatología HUVM")

# -----------------------
# LOGIN
# -----------------------
roles = ["Dermatólogo", "Director de Derma", "Farmacia"]
role = st.sidebar.selectbox("Acceso", roles)

if role in ["Director de Derma", "Farmacia"]:
    password = st.sidebar.text_input("Contraseña", type="password")
    if password != "123":
        st.warning("Acceso restringido")
        st.stop()

# -----------------------
# DATOS
# -----------------------
FILE = "data.json"

def load_data():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f)

if "requests" not in st.session_state:
    st.session_state.requests = load_data()

# -----------------------
# SOLICITANTES
# -----------------------
solicitantes = [
    "Dra. Carrizosa","Dra. Conejo-Mir","Dr. de la Torre","Dra. Eiris",
    "Dra. Fernández Orland","Dra. Ferrándiz","Dra. García Morales",
    "Dr. Marcos","Dra. Ojeda","Dr. Ruiz de Casas","Dra. Ruz",
    "Dra. Sánchez del Campo","Dr. Sánchez Leiro","Dra. Serrano",
]

# -----------------------
# PROTOCOLOS
# -----------------------
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
            "Bimekizumab 320 mg/8 semanas"
        ]
    },
    "Dermatitis atópica": {
        "texto": "1º Dupilumab → 2º Tralokinumab → 3º JAK",
        "drugs": [
            "Dupilumab 300 mg/2 semanas",
            "Tralokinumab 300 mg/2 semanas",
            "Upadacitinib 15 mg",
            "Upadacitinib 30 mg"
        ]
    }
}

# -----------------------
# FORMULARIO (IMPORTANTE: enfermedad FUERA)
# -----------------------

if role == "Dermatólogo":

    st.subheader("Nueva solicitud")

    # 🔥 fuera del form → esto hace que funcione bien
    enfermedad = st.selectbox("Enfermedad", ["Seleccionar"] + list(protocolos.keys()))

    lista_tratamientos = ["Seleccionar"]

    if enfermedad != "Seleccionar":
        st.info(protocolos[enfermedad]["texto"])
        lista_tratamientos = ["Seleccionar"] + protocolos[enfermedad]["drugs"]

    with st.form("formulario"):

        paciente = st.text_input("Paciente (AN + 10 dígitos)", value="AN")

        solicitante = st.selectbox("Solicitante", ["Seleccionar"] + solicitantes)

        tratamiento = st.selectbox("Tratamiento", lista_tratamientos)

        submitted = st.form_submit_button("Enviar solicitud")

        if submitted:

            paciente = paciente.strip().upper()

            if solicitante == "Seleccionar":
                st.error("Debe seleccionar un solicitante")

            elif enfermedad == "Seleccionar":
                st.error("Debe seleccionar una enfermedad")

            elif tratamiento == "Seleccionar":
                st.error("Debe seleccionar un tratamiento")

            elif not re.fullmatch(r"AN\d{10}", paciente):
                st.error("Formato incorrecto: AN + 10 dígitos")

            else:
                nueva = {
                    "Paciente": paciente,
                    "Solicitante": solicitante,
                    "Enfermedad": enfermedad,
                    "Tratamiento": tratamiento,
                    "Estado Director": "Pendiente",
                    "Estado Farmacia": "",
                    "Fecha solicitud": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Fecha Director": "",
                    "Fecha Farmacia": ""
                }

                st.session_state.requests.insert(0, nueva)
                save_data(st.session_state.requests)

                st.success("Solicitud creada")

# -----------------------
# TABLA
# -----------------------

st.subheader("Solicitudes")

for i, r in enumerate(st.session_state.requests):

    col1, col2, col3 = st.columns(3)

    col1.write(r["Paciente"])
    col2.write(r["Enfermedad"])
    col3.write(r["Tratamiento"])
