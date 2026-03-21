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
        "drugs": ["Omalizumab 300 mg/4 semanas"],
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
# FORMULARIO
# -----------------------
if role == "Dermatólogo":

    st.subheader("Nueva solicitud")

    paciente = st.text_input("Paciente (AN + 10 dígitos)", value="AN")

    solicitante = st.selectbox("Solicitante", ["Seleccionar"] + solicitantes)

    enfermedad = st.selectbox("Enfermedad", ["Seleccionar"] + list(protocolos.keys()))

    if enfermedad != "Seleccionar":
        st.info(protocolos[enfermedad]["texto"])
        tratamientos = ["Seleccionar"] + protocolos[enfermedad]["drugs"]
    else:
        tratamientos = ["Seleccionar"]

    tratamiento = st.selectbox("Tratamiento", tratamientos)

    if st.button("Enviar solicitud"):

        paciente = paciente.strip().upper()

        if solicitante == "Seleccionar":
            st.error("Debe seleccionar un solicitante")

        elif enfermedad == "Seleccionar":
            st.error("Debe seleccionar una enfermedad")

        elif tratamiento == "Seleccionar":
            st.error("Debe seleccionar un tratamiento")

        elif not re.fullmatch(r"AN\d{10}", paciente):
            st.error("Formato AN + 10 dígitos")

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
# TABLA + VALIDACIONES
# -----------------------
st.subheader("Solicitudes")

if st.session_state.requests:

    df = pd.DataFrame(st.session_state.requests)
    st.dataframe(df, use_container_width=True)

    for i, r in enumerate(st.session_state.requests):

        st.write("---")
        st.write(f"Paciente: {r['Paciente']} | {r['Enfermedad']}")

        # DIRECTOR
        if role == "Director de Derma" and r["Estado Director"] == "Pendiente":

            col1, col2 = st.columns(2)

            if col1.button("Validar", key=f"val_{i}"):
                r["Estado Director"] = "Validado"
                r["Fecha Director"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                save_data(st.session_state.requests)
                st.rerun()

            if col2.button("No validar", key=f"noval_{i}"):
                r["Estado Director"] = "No validado"
                r["Fecha Director"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                save_data(st.session_state.requests)
                st.rerun()

        # FARMACIA
        if role == "Farmacia" and r.get["Estado Director"] == "Validado":

            col1, col2 = st.columns(2)

            if col1.button("Dispensar", key=f"disp_{i}"):
                r["Estado Farmacia"] = "Pendiente de dispensación"
                r["Fecha Farmacia"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                save_data(st.session_state.requests)
                st.rerun()

            if col2.button("Rechazar", key=f"rech_{i}"):
                r["Estado Farmacia"] = "No validado"
                r["Fecha Farmacia"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                save_data(st.session_state.requests)
                st.rerun()
