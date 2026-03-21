import streamlit as st
import re
import json
from datetime import datetime
import pandas as pd

# -----------------------
# CONFIGURACIÓN
# -----------------------
st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: Arial !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

    with st.form("formulario", clear_on_submit=True):

        # PACIENTE
        paciente_input = st.text_input("Paciente", placeholder="AN1234567890")

        # SOLICITANTE
        solicitante = st.selectbox(
            "Solicitante",
            ["Seleccionar"] + solicitantes
        )

        # ENFERMEDAD
        enfermedad = st.selectbox(
            "Enfermedad",
            ["Seleccionar"] + list(protocolos.keys())
        )

        # PROTOCOLO
        if enfermedad != "Seleccionar":
            st.info(protocolos[enfermedad]["texto"])

        # TRATAMIENTO (FIX CLAVE)
        if enfermedad == "Seleccionar":
            lista_tratamientos = ["Seleccionar"]
        else:
            lista_tratamientos = ["Seleccionar"] + protocolos[enfermedad]["drugs"]

        tratamiento = st.selectbox("Tratamiento", lista_tratamientos)

        # BOTÓN
        submitted = st.form_submit_button("Enviar solicitud")

        # VALIDACIÓN
        if submitted:

            if not re.match(r"^AN\d{10}$", paciente_input):
                st.error("Formato: AN + 10 dígitos")

            elif solicitante == "Seleccionar" or enfermedad == "Seleccionar" or tratamiento == "Seleccionar":
                st.error("Debe completar todos los campos")

            else:
                nueva = {
                    "Paciente": paciente_input,
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
# EXPORTACIÓN CSV (ESTABLE)
# -----------------------
def generar_csv(data):
    df = pd.DataFrame(data)
    return df.to_csv(index=False).encode('utf-8')

if st.session_state.requests:
    csv = generar_csv(st.session_state.requests)

    st.download_button(
        label="Descargar Excel (CSV)",
        data=csv,
        file_name="solicitudes_dermai.csv",
        mime="text/csv"
    )

# -----------------------
# TABLA
# -----------------------
st.subheader("Solicitudes")

for i, r in enumerate(st.session_state.requests):

    col1, col2, col3, col4, col5, col6 = st.columns([2,2,3,2,2,3])

    col1.write(r["Paciente"])
    col2.write(r["Enfermedad"])
    col3.write(r["Tratamiento"])

    with col4:
        st.write(r["Estado Director"])
        if r["Fecha Director"]:
            st.caption(r["Fecha Director"])

    with col5:
        st.write(r["Estado Farmacia"] or "-")
        if r["Fecha Farmacia"]:
            st.caption(r["Fecha Farmacia"])

    with col6:
        if r["Estado Director"] == "No validado" or r["Estado Farmacia"] == "No validado":
            st.write("Solicitar a Comisión Derma-Farmacia")

    # DIRECTOR
    if role == "Director de Derma" and r["Estado Director"] == "Pendiente":

        if st.button(f"Validar {i}"):
            r["Estado Director"] = "Validado"
            r["Fecha Director"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            save_data(st.session_state.requests)
            st.rerun()

        if st.button(f"No validar {i}"):
            r["Estado Director"] = "No validado"
            r["Fecha Director"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            save_data(st.session_state.requests)
            st.rerun()

    # FARMACIA
    if role == "Farmacia" and r["Estado Director"] == "Validado":

        if st.button(f"Pendiente dispensación {i}"):
            r["Estado Farmacia"] = "Pendiente de dispensación"
            r["Fecha Farmacia"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            save_data(st.session_state.requests)
            st.rerun()

        if st.button(f"No validar farmacia {i}"):
            r["Estado Farmacia"] = "No validado"
            r["Fecha Farmacia"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            save_data(st.session_state.requests)
            st.rerun()

    st.divider()
