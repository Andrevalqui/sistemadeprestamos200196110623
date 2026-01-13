import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestor Financiero", layout="wide", page_icon="🏦")

# --- CSS PREMIUM / GERENCIAL ---
st.markdown("""
    <style>
    /* Importar fuente moderna */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
    }

    /* Estilo del Contenedor Principal */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Tarjetas de Métricas (KPIs) */
    .metric-card {
        background-color: #ffffff;
        border-left: 5px solid #2E86C1;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        text-align: center;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-title {
        color: #7f8c8d;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    .metric-value {
        color: #2c3e50;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .metric-positive { color: #27AE60; }
    
    /* Inputs y Formularios */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #ffffff;
        border: 1px solid #dcdce6;
        border-radius: 5px;
        color: #2c3e50;
    }
    
    /* Botón Principal */
    div.stButton > button {
        background: linear-gradient(90deg, #1A5276 0%, #2E86C1 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-radius: 8px;
        width: 100%;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        box-shadow: 0 5px 15px rgba(46, 134, 193, 0.4);
    }

    /* Tablas */
    div[data-testid="stDataFrame"] {
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        df = conn.read(worksheet="Hoja 1", ttl=0)
        df = df.dropna(how="all")
        return df
    except:
        return pd.DataFrame()

def guardar_nuevo_prestamo(data):
    try:
        df_actual = cargar_datos()
        df_nuevo = pd.DataFrame([data])
        df_final = pd.concat([df_actual, df_nuevo], ignore_index=True)
        conn.update(worksheet="Hoja 1", data=df_final)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def calcular(monto, tasa, plazo):
    interes = monto * (tasa/100) * plazo
    total = monto + interes
    cuota = total / plazo
    return total, interes, cuota

# --- UI PRINCIPAL ---
st.title("🏦 Dashboard Financiero")
st.markdown("### Gestión de Créditos Personales")

menu = st.sidebar.selectbox("Menú Principal", ["📝 Nuevo Préstamo", "📊 Panel Gerencial"])

if menu == "📝 Nuevo Préstamo":
    with st.container():
        st.markdown("#### Información del Cliente")
        c1, c2 = st.columns(2)
        cliente = c1.text_input("Nombre Completo")
        dni = c2.text_input("DNI / Identificación")
        
        st.markdown("#### Detalles del Crédito")
        c3, c4, c5 = st.columns(3)
        monto = c3.number_input("Monto Solicitado ($)", min_value=0.0, step=100.0)
        tasa = c4.number_input("Tasa Interés (%)", value=5.0)
        plazo = c5.number_input("Plazo (Meses)", value=12)

    total, ganancia, cuota = calcular(monto, tasa, plazo)

    # Vista previa estilo tarjeta
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Cuota Mensual</div>
            <div class="metric-value">${cuota:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)
    
    col2.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total a Cobrar</div>
            <div class="metric-value">${total:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)
    
    col3.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #27AE60;">
            <div class="metric-title">Ganancia Neta</div>
            <div class="metric-value metric-positive">+${ganancia:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

    st.write("") # Espacio
    if st.button("CONFIRMAR Y GUARDAR OPERACIÓN"):
        if cliente and monto > 0:
            reg = {
                "Cliente": cliente, "DNI": dni, "Fecha": str(datetime.now().date()),
                "Monto": monto, "Tasa": tasa, "Plazo": plazo,
                "Total_Pagar": total, "Ganancia": ganancia, "Estado": "Activo"
            }
            if guardar_nuevo_prestamo(reg):
                st.success("Operación registrada correctamente en la base de datos.")
        else:
            st.warning("Complete los campos obligatorios.")

elif menu == "📊 Panel Gerencial":
    df = cargar_datos()
    
    if not df.empty:
        # KPIs Superiores
        total_calle = df["Monto"].sum()
        utilidad = df["Ganancia"].sum()
        tickets = len(df)
        
        k1, k2, k3 = st.columns(3)
        k1.markdown(f"""<div class="metric-card"><div class="metric-title">Capital Colocado</div><div class="metric-value">${total_calle:,.2f}</div></div>""", unsafe_allow_html=True)
        k2.markdown(f"""<div class="metric-card" style="border-left: 5px solid #27AE60;"><div class="metric-title">Utilidad Proyectada</div><div class="metric-value metric-positive">${utilidad:,.2f}</div></div>""", unsafe_allow_html=True)
        k3.markdown(f"""<div class="metric-card"><div class="metric-title">Créditos Activos</div><div class="metric-value">{tickets}</div></div>""", unsafe_allow_html=True)
        
        st.markdown("### 📑 Base de Datos de Clientes")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No hay datos para mostrar.")
