import streamlit as st
import re
import json
from datetime import datetime

# -----------------------
# CONFIG UI
# -----------------------
st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        font-family: Arial !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("DerMAI")

# -----------------------
# LOGIN
# -----------------------
roles = ["Dermatólogo", "Director de Derma", "Farmacia"]
role = st.sidebar.selectbox("Acceso", roles)

credentials = {
    "Director de Derma": "123",
    "Farmacia": "123"
}

auth = True

if role in credentials:
    password = st.sidebar.text_input("Contraseña", type="password")
    if password != credentials[role]:
        st.warning("Acceso restringido")
        auth = False

if not auth:
    st.stop()

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
            "Bimekizumab 320 mg/8 semanas",
        ],
    },
    "Dermatitis atópica": {
        "texto": "1º Dupilumab → 2º Tralokinumab → 3º JAK",
        "drugs": [
            "Dupilumab 300 mg/2 semanas",
            "Upadacitinib 15 mg",
            "Upadacitinib 30 mg",
        ],
    },
}

# -----------------------
# PERSISTENCIA
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
# FORMULARIO
# -----------------------
if role == "Dermatólogo":
    st.subheader("Nueva solicitud")

    paciente = st.text_input("Paciente (AN + 10 dígitos)")
    solicitante = st.selectbox("Solicitante", solicitantes)
    enfermedad = st.selectbox("Enfermedad", list(protocolos.keys()))

    st.write(protocolos[enfermedad]["texto"])

    tratamiento = st.selectbox(
        "Tratamiento",
        protocolos[enfermedad]["drugs"]
    )

    if st.button("Enviar solicitud"):
        if not re.match(r"^AN\d{10}$", paciente):
            st.error("Formato incorrecto")
        else:
            new = {
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
            st.session_state.requests.insert(0, new)
            save_data(st.session_state.requests)
            st.success("Solicitud creada")

# -----------------------
# TABLA
# -----------------------
st.subheader("Solicitudes")

for i, r in enumerate(st.session_state.requests):

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.write(r["Paciente"])
    col2.write(r["Enfermedad"])
    col3.write(r["Tratamiento"])
    col4.write(r["Estado Director"])
    col5.write(r["Estado Farmacia"])

    # -----------------------
    # DIRECTOR
    # -----------------------
    if role == "Director de Derma" and r["Estado Director"] == "Pendiente":

        if st.button(f"Validar {i}"):
            r["Estado Director"] = "Validado"
            r["Fecha Director"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            save_data(st.session_state.requests)

        if st.button(f"No validar {i}"):
            r["Estado Director"] = "No validado"
            r["Fecha Director"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            save_data(st.session_state.requests)

    # -----------------------
    # FARMACIA
    # -----------------------
    if role == "Farmacia" and r["Estado Director"] == "Validado":

        if st.button(f"Pendiente dispensación {i}"):
            r["Estado Farmacia"] = "Pendiente de dispensación"
            r["Fecha Farmacia"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            save_data(st.session_state.requests)

        if st.button(f"No validar farmacia {i}"):
            r["Estado Farmacia"] = "No validado"
            r["Fecha Farmacia"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            save_data(st.session_state.requests)

    # -----------------------
    # ALERTA
    # -----------------------
    if r["Estado Director"] == "No validado" or r["Estado Farmacia"] == "No validado":
        st.write("Solicitar a Comisión Derma-Farmacia")

    st.divider()
