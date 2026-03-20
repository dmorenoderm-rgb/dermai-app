import streamlit as st
import re
import json
import pandas as pd
from datetime import datetime
from io import BytesIO

# -----------------------
# CONFIGURACIÓN UI
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
# CONTROL RESET FORMULARIO
# -----------------------
if "reset_form" not in st.session_state:
    st.session_state.reset_form = False

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
            "Etanercept 50 mg semanal",
            "Infliximab 5 mg/kg cada 8 semanas",
            "Certolizumab 200 mg/2 semanas",
            "Certolizumab 400 mg/4 semanas",
            "Ustekinumab 45 mg/12 semanas",
            "Ustekinumab 90 mg/12 semanas",
            "Secukinumab 300 mg/4 semanas",
            "Ixekizumab 80 mg/4 semanas",
            "Brodalumab 210 mg/2 semanas",
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
        "texto": "Inmunoterapia / terapias dirigidas",
        "drugs": [
            "Nivolumab 240 mg/2 semanas",
            "Nivolumab 480 mg/4 semanas",
            "Pembrolizumab 200 mg/3 semanas",
            "Pembrolizumab 400 mg/6 semanas",
            "Ipilimumab 3 mg/kg",
            "Dabrafenib + trametinib",
            "Encorafenib + binimetinib",
            "Vemurafenib + cobimetinib",
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

    # Inicialización valores vacíos
    if "paciente" not in st.session_state:
        st.session_state.paciente = ""

    paciente = st.text_input("Paciente (AN + 10 dígitos)", key="paciente")

    solicitante = st.selectbox(
        "Solicitante",
        solicitantes,
        key="solicitante"
    )

    enfermedad = st.selectbox(
        "Enfermedad",
        list(protocolos.keys()),
        key="enfermedad"
    )

    st.write(protocolos[enfermedad]["texto"])

    tratamiento = st.selectbox(
        "Tratamiento",
        protocolos[enfermedad]["drugs"],
        key="tratamiento"
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

            # 🔥 RESET LIMPIO
            st.success("Solicitud creada")
st.rerun()

            st.success("Solicitud creada")

# -----------------------
# EXPORTAR EXCEL
# -----------------------
st.subheader("Solicitudes")

df = pd.DataFrame(st.session_state.requests)

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

if not df.empty:
    excel_data = to_excel(df)

    st.download_button(
        label="Descargar Excel",
        data=excel_data,
        file_name="solicitudes_dermai.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# -----------------------
# TABLA
# -----------------------
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

    st.divider()
