import streamlit as st
import re
import json
from datetime import datetime
import pandas as pd

st.set_page_config(layout="wide")

st.title("DerMAI PRO")
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
# PROTOCOLOS COMPLETOS
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
            "Bimekizumab 320 mg/8 semanas",
        ],
    },

    "Dermatitis atópica": {
        "texto": "1º Dupilumab → 2º Tralokinumab → 3º JAK",
        "drugs": [
            "Dupilumab 300 mg/2 semanas",
            "Tralokinumab 300 mg/2 semanas",
            "Tralokinumab 300 mg/4 semanas",
            "Lebrikizumab 250 mg/2 semanas",
            "Lebrikizumab 250 mg/4 semanas",
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
            "Secukinumab 300 mg/4 semanas",
            "Bimekizumab 320 mg/4 semanas",
        ],
    },

    "Urticaria crónica espontánea": {
        "texto": "Omalizumab",
        "drugs": [
            "Omalizumab 300 mg/4 semanas",
        ],
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
        "drugs": [
            "Ruxolitinib crema 1,5%",
        ],
    },

    "Melanoma": {
        "texto": "Inmunoterapia",
        "drugs": [
            "Nivolumab 240 mg/2 semanas",
            "Nivolumab 480 mg/4 semanas",
            "Pembrolizumab 200 mg/3 semanas",
            "Pembrolizumab 400 mg/6 semanas",
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
            "Cemiplimab 350 mg/3 semanas",
            "Pembrolizumab 200 mg/3 semanas",
            "Pembrolizumab 400 mg/6 semanas",
        ],
    },
}

# -----------------------
# DASHBOARD
# -----------------------
st.subheader("Panel de control")

total = len(st.session_state.requests)
pendientes = sum(1 for r in st.session_state.requests if r["Estado Director"] == "Pendiente")
validados = sum(1 for r in st.session_state.requests if r["Estado Director"] == "Validado")
rechazados = sum(1 for r in st.session_state.requests if r["Estado Director"] == "No validado")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total", total)
c2.metric("Pendientes", pendientes)
c3.metric("Validados", validados)
c4.metric("Rechazados", rechazados)

# -----------------------
# FORMULARIO
# -----------------------
if role == "Dermatólogo":

    st.subheader("Nueva solicitud")

    with st.form("formulario"):

        paciente = st.text_input("Paciente (AN + 10 dígitos)", value="AN")

        solicitante = st.selectbox("Solicitante", ["Seleccionar"] + solicitantes)

        enfermedad = st.selectbox("Enfermedad", ["Seleccionar"] + list(protocolos.keys()))

        lista_tratamientos = ["Seleccionar"]

        if enfermedad != "Seleccionar":
            st.info(protocolos[enfermedad]["texto"])
            lista_tratamientos = ["Seleccionar"] + protocolos[enfermedad]["drugs"]

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
                st.error("Formato incorrecto")

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
                    "Fecha Farmacia": "",
                }

                st.session_state.requests.insert(0, nueva)
                save_data(st.session_state.requests)

                st.success("Solicitud creada")

# -----------------------
# FILTROS
# -----------------------
st.subheader("Filtros")

colf1, colf2, colf3 = st.columns(3)

f_estado_dir = colf1.selectbox("Estado Director", ["Todos","Pendiente","Validado","No validado"])
f_estado_far = colf2.selectbox("Estado Farmacia", ["Todos","","Pendiente de dispensación","No validado"])
f_enfermedad = colf3.selectbox("Enfermedad", ["Todas"] + list(protocolos.keys()))

filtered = st.session_state.requests

if f_estado_dir != "Todos":
    filtered = [r for r in filtered if r["Estado Director"] == f_estado_dir]

if f_estado_far != "Todos":
    filtered = [r for r in filtered if r["Estado Farmacia"] == f_estado_far]

if f_enfermedad != "Todas":
    filtered = [r for r in filtered if r["Enfermedad"] == f_enfermedad]

# -----------------------
# TABLA
# -----------------------
st.subheader("Solicitudes")

for r in filtered:
    st.write(r)
