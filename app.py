import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestor de Préstamos Web", layout="wide", page_icon="💰")

# --- CONEXIÓN A GOOGLE SHEETS ---
# Esta función conecta con tu hoja y descarga los datos frescos cada vez
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    # Leemos la hoja completa. ttl=0 significa que no guarde caché (datos siempre frescos)
    try:
        df = conn.read(worksheet="Hoja 1", ttl=0)
        # Aseguramos que los números sean números y no texto
        df = df.dropna(how="all") # Eliminar filas vacías
        return df
    except Exception as e:
        st.error(f"Error al conectar con la Hoja: {e}")
        return pd.DataFrame()

def guardar_nuevo_prestamo(nuevo_dato_dict):
    try:
        # Cargamos lo actual
        df_actual = cargar_datos()
        # Creamos un pequeño DF con el nuevo dato
        df_nuevo = pd.DataFrame([nuevo_dato_dict])
        # Unimos ambos
        df_final = pd.concat([df_actual, df_nuevo], ignore_index=True)
        # Subimos todo de nuevo a Google Sheets
        conn.update(worksheet="Hoja 1", data=df_final)
        st.success("✅ ¡Datos guardados en la Nube correctamente!")
        st.cache_data.clear() # Limpiamos memoria para forzar recarga
        return True
    except Exception as e:
        st.error(f"No se pudo guardar: {e}")
        return False

# --- LÓGICA MATEMÁTICA ---
def calcular_totales(monto, tasa, plazo_meses):
    interes_total = monto * (tasa / 100) * plazo_meses
    total_pagar = monto + interes_total
    cuota_mensual = total_pagar / plazo_meses
    return total_pagar, interes_total, cuota_mensual

# --- CSS PERSONALIZADO (Diseño Profesional) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    div.stButton > button {
        background-color: #004d40;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #00695c;
        border: 1px solid white;
    }
    .metric-container {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 10px;
    }
    h1 { color: #1a237e; }
    </style>
""", unsafe_allow_html=True)

# --- INTERFAZ PRINCIPAL ---

st.title("🏦 Sistema de Préstamos en la Nube")
st.caption("Conectado a Google Sheets en Tiempo Real")

menu = st.sidebar.radio("Navegación", ["Nuevo Préstamo", "Cartera de Clientes"])

if menu == "Nuevo Préstamo":
    st.header("📝 Registrar Crédito")
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            cliente = st.text_input("Nombre Completo")
            dni = st.text_input("DNI / Cédula")
            fecha = st.date_input("Fecha desembolso")
        
        with col2:
            monto = st.number_input("Monto ($)", min_value=0.0, step=100.0)
            tasa = st.number_input("Tasa Mensual (%)", value=5.0)
            plazo = st.number_input("Plazo (meses)", value=12, min_value=1)

    # Cálculos en vivo
    total, ganancia, cuota = calcular_totales(monto, tasa, plazo)

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.info(f"💵 Cuota: **${cuota:,.2f}**")
    c2.warning(f"💰 Total a Cobrar: **${total:,.2f}**")
    c3.success(f"📈 Ganancia Neta: **${ganancia:,.2f}**")

    if st.button("GUARDAR EN LA NUBE"):
        if cliente and monto > 0:
            nuevo_registro = {
                "Cliente": cliente,
                "DNI": dni,
                "Fecha": str(fecha),
                "Monto": monto,
                "Tasa": tasa,
                "Plazo": plazo,
                "Total_Pagar": total,
                "Ganancia": ganancia,
                "Estado": "Activo"
            }
            guardar_nuevo_prestamo(nuevo_registro)
        else:
            st.warning("Falta el nombre o el monto.")

elif menu == "Cartera de Clientes":
    st.header("📊 Panel de Control")
    
    # Cargar datos desde Google Sheets
    df = cargar_datos()
    
    if not df.empty:
        # Métricas
        total_prestado = df["Monto"].sum()
        ganancia_proyectada = df["Ganancia"].sum()
        
        m1, m2 = st.columns(2)
        m1.markdown(f"<div class='metric-container'><h3>Capital en Calle</h3><h1>${total_prestado:,.2f}</h1></div>", unsafe_allow_html=True)
        m2.markdown(f"<div class='metric-container'><h3>Ganancia Esperada</h3><h1 style='color:green'>${ganancia_proyectada:,.2f}</h1></div>", unsafe_allow_html=True)
        
        st.markdown("### Listado Detallado")
        
        # Filtro simple
        filtro = st.text_input("Buscar cliente por nombre...")
        if filtro:
            df = df[df["Cliente"].str.contains(filtro, case=False, na=False)]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("La base de datos está vacía o no se pudo conectar.")