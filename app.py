import streamlit as st
import re
import json
from datetime import datetime

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
# PROTOCOLOS (mínimo para probar)
# -----------------------
protocolos = {
    "Psoriasis en placas": {
        "texto": "Adalimumab → Ustekinumab",
        "drugs": [
            "Adalimumab 40 mg/2 semanas",
            "Ustekinumab 45 mg/12 semanas"
        ],
    }
}

solicitantes = ["Dra. Carrizosa", "Dr. Marcos"]

# -----------------------
# FORMULARIO
# -----------------------
if role == "Dermatólogo":

    st.subheader("Nueva solicitud")

    paciente = st.text_input("Paciente (AN + 10 dígitos)")
    solicitante = st.selectbox("Solicitante", solicitantes)
    enfermedad = st.selectbox("Enfermedad", list(protocolos.keys()))

    st.write(protocolos[enfermedad]["texto"])

    tratamiento = st.selectbox("Tratamiento", protocolos[enfermedad]["drugs"])

    if st.button("Enviar solicitud"):

        if not re.match(r"^AN\d{10}$", paciente):
            st.error("Formato incorrecto")
        else:
            nueva = {
                "Paciente": paciente,
                "Enfermedad": enfermedad,
                "Tratamiento": tratamiento,
                "Estado Director": "Pendiente",
                "Estado Farmacia": ""
            }

            st.session_state.requests.insert(0, nueva)
            save_data(st.session_state.requests)

            st.success("Solicitud creada")
            st.rerun()

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

    if role == "Director de Derma" and r["Estado Director"] == "Pendiente":
        if st.button(f"Validar {i}"):
            r["Estado Director"] = "Validado"
            save_data(st.session_state.requests)
            st.rerun()

    if role == "Farmacia" and r["Estado Director"] == "Validado":
        if st.button(f"Dispensar {i}"):
            r["Estado Farmacia"] = "Pendiente de dispensación"
            save_data(st.session_state.requests)
            st.rerun()

    st.divider()
