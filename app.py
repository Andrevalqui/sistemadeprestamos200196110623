import streamlit as st
import pandas as pd
import json
from datetime import datetime
from github import Github

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestor Financiero", layout="wide", page_icon="🏦")

# --- CONEXIÓN A GITHUB (TU BASE DE DATOS GRATIS) ---
def get_repo():
    """Conecta con GitHub usando el Token secreto"""
    token = st.secrets["GITHUB_TOKEN"]
    g = Github(token)
    return g.get_repo(st.secrets["REPO_NAME"])

def cargar_datos():
    """Descarga el archivo JSON desde GitHub"""
    try:
        repo = get_repo()
        contents = repo.get_contents("data.json")
        datos = json.loads(contents.decoded_content.decode())
        if not datos:
            return pd.DataFrame()
        return pd.DataFrame(datos)
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

def guardar_nuevo_prestamo(nuevo_registro):
    """Sube el nuevo dato a GitHub"""
    try:
        repo = get_repo()
        contents = repo.get_contents("data.json")
        
        # Descargar datos actuales
        datos_actuales = json.loads(contents.decoded_content.decode())
        
        # Agregar el nuevo
        datos_actuales.append(nuevo_registro)
        
        # Convertir a JSON bonito
        json_data = json.dumps(datos_actuales, indent=4)
        
        # Subir actualización a GitHub
        repo.update_file(
            path=contents.path,
            message="Nuevo préstamo registrado desde Web",
            content=json_data,
            sha=contents.sha
        )
        return True
    except Exception as e:
        st.error(f"No se pudo guardar: {e}")
        return False

# --- CSS PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    .metric-card {
        background-color: #ffffff;
        border-left: 5px solid #2E86C1;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-title { color: #7f8c8d; font-size: 0.9rem; text-transform: uppercase; margin-bottom: 5px; }
    .metric-value { color: #2c3e50; font-size: 1.8rem; font-weight: 700; }
    .metric-positive { color: #27AE60; }
    div.stButton > button {
        background: linear-gradient(90deg, #1A5276 0%, #2E86C1 100%);
        color: white; border: none; padding: 12px 24px; border-radius: 8px; width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA ---
def calcular(monto, tasa, plazo):
    interes = monto * (tasa/100) * plazo
    total = monto + interes
    cuota = total / plazo
    return total, interes, cuota

# --- UI PRINCIPAL ---
st.title("🏦 Dashboard Financiero")

# Menú
menu = st.sidebar.radio("Navegación", ["📝 Nuevo Préstamo", "📊 Panel Gerencial"])

if menu == "📝 Nuevo Préstamo":
    st.markdown("### Registrar Operación")
    with st.container():
        c1, c2 = st.columns(2)
        cliente = c1.text_input("Nombre Cliente")
        dni = c2.text_input("DNI / ID")
        
        c3, c4, c5 = st.columns(3)
        monto = c3.number_input("Monto ($)", min_value=0.0, step=100.0)
        tasa = c4.number_input("Tasa %", value=5.0)
        plazo = c5.number_input("Meses", value=12)

    total, ganancia, cuota = calcular(monto, tasa, plazo)

    st.markdown("---")
    k1, k2, k3 = st.columns(3)
    k1.markdown(f'<div class="metric-card"><div class="metric-title">Cuota</div><div class="metric-value">${cuota:,.2f}</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="metric-card"><div class="metric-title">Total</div><div class="metric-value">${total:,.2f}</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="metric-card" style="border-color:#27AE60"><div class="metric-title">Ganancia</div><div class="metric-value metric-positive">${ganancia:,.2f}</div></div>', unsafe_allow_html=True)

    st.write("")
    if st.button("💾 GUARDAR OPERACIÓN"):
        if cliente and monto > 0:
            reg = {
                "Cliente": cliente, "DNI": dni, "Fecha": str(datetime.now().date()),
                "Monto": monto, "Tasa": tasa, "Plazo": plazo,
                "Total_Pagar": total, "Ganancia": ganancia, "Estado": "Activo"
            }
            with st.spinner("Guardando en base de datos..."):
                if guardar_nuevo_prestamo(reg):
                    st.success("¡Guardado exitoso! La página se recargará en unos segundos...")
                    st.rerun()
        else:
            st.warning("Completa los datos principales")

elif menu == "📊 Panel Gerencial":
    st.markdown("### Estado de la Cartera")
    df = cargar_datos()
    
    if not df.empty:
        # Tarjetas KPI
        tot = df["Monto"].sum()
        gan = df["Ganancia"].sum()
        cnt = len(df)
        
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="metric-card"><div class="metric-title">Capital Prestado</div><div class="metric-value">${tot:,.2f}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card" style="border-color:#27AE60"><div class="metric-title">Utilidad Neta</div><div class="metric-value metric-positive">${gan:,.2f}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card"><div class="metric-title">Préstamos</div><div class="metric-value">{cnt}</div></div>', unsafe_allow_html=True)
        
        st.write("---")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("La base de datos está vacía. Registra el primer préstamo.")
