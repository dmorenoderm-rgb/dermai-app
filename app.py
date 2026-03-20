import streamlit as st
import re

st.set_page_config(layout="wide")
st.title("🧴 DerMAI – Gestión de tratamientos dermatológicos")

# -----------------------
# ROLES
# -----------------------
rol = st.sidebar.selectbox("Rol", ["Dermatólogo", "Director", "Farmacia"])

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
        "texto": "Inmunoterapia / BRAF",
        "drugs": [
            "Nivolumab",
            "Pembrolizumab",
            "Ipilimumab",
            "Dabrafenib + trametinib",
            "Encorafenib + binimetinib",
        ],
    },
    "Carcinoma basocelular": {
        "texto": "Hedgehog",
        "drugs": ["Vismodegib", "Sonidegib"],
    },
    "Carcinoma escamoso cutáneo": {
        "texto": "Anti-PD1",
        "drugs": ["Cemiplimab", "Pembrolizumab"],
    },
}

# -----------------------
# BASE DE DATOS (memoria)
# -----------------------
if "requests" not in st.session_state:
    st.session_state.requests = []

# -----------------------
# FORMULARIO
# -----------------------
if rol == "Dermatólogo":
    st.subheader("📝 Nueva solicitud")

    paciente = st.text_input("Paciente (AN + 10 dígitos)")
    solicitante = st.selectbox("Solicitante", solicitantes)
    enfermedad = st.selectbox("Enfermedad", list(protocolos.keys()))

    st.info(protocolos[enfermedad]["texto"])

    tratamiento = st.selectbox(
        "Tratamiento",
        protocolos[enfermedad]["drugs"]
    )

    if st.button("Enviar solicitud"):
        if not re.match(r"^AN\d{10}$", paciente):
            st.error("Formato incorrecto: AN + 10 dígitos")
        else:
            st.session_state.requests.insert(0, {
                "Paciente": paciente,
                "Solicitante": solicitante,
                "Enfermedad": enfermedad,
                "Tratamiento": tratamiento,
                "Director": "",
                "Farmacia": "",
            })
            st.success("Solicitud registrada")

# -----------------------
# HISTÓRICO
# -----------------------
st.subheader("📊 Histórico")

for i, r in enumerate(st.session_state.requests):
    col1, col2, col3, col4, col5 = st.columns([2,2,2,2,3])

    col1.write(r["Paciente"])
    col2.write(r["Enfermedad"])
    col3.write(r["Tratamiento"])
    col4.write(r["Director"] or "-")
    col5.write(r["Farmacia"] or "-")

    # -----------------------
    # DIRECTOR
    # -----------------------
    if rol == "Director" and not r["Director"]:
        if st.button(f"✔ Validar {i}"):
            r["Director"] = "Validado"
        if st.button(f"✖ Rechazar {i}"):
            r["Director"] = "No validado"

    # -----------------------
    # FARMACIA
    # -----------------------
    if rol == "Farmacia" and r["Director"] == "Validado":
        if st.button(f"📅 Citar {i}"):
            r["Farmacia"] = "Citado"
        if st.button(f"❌ RechazarF {i}"):
            r["Farmacia"] = "No validado"

    # -----------------------
    # ALERTA
    # -----------------------
    if r["Director"] == "No validado" or r["Farmacia"] == "No validado":
        st.warning("Solicitar a Comisión Derma-Farmacia")

    st.divider()
