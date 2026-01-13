import streamlit as st
import pandas as pd
import json
from datetime import datetime
from github import Github

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestor de Préstamos", layout="wide", page_icon="💰")

# --- CONEXIÓN A GITHUB ---
def get_repo():
    token = st.secrets["GITHUB_TOKEN"]
    g = Github(token)
    return g.get_repo(st.secrets["REPO_NAME"])

def cargar_datos():
    try:
        repo = get_repo()
        contents = repo.get_contents("data.json")
        datos = json.loads(contents.decoded_content.decode())
        if not datos:
            return pd.DataFrame()
        return pd.DataFrame(datos)
    except Exception as e:
        # Si falla, devolvemos vacío pero no mostramos error feo
        return pd.DataFrame()

def guardar_nuevo_prestamo(nuevo_registro):
    try:
        repo = get_repo()
        contents = repo.get_contents("data.json")
        datos_actuales = json.loads(contents.decoded_content.decode())
        datos_actuales.append(nuevo_registro)
        json_data = json.dumps(datos_actuales, indent=4)
        repo.update_file(contents.path, "Nuevo préstamo", json_data, contents.sha)
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# --- CSS PREMIUM / GERENCIAL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    
    .metric-card {
        background-color: #ffffff;
        border-left: 5px solid #1A5276;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-title { color: #7f8c8d; font-size: 0.85rem; text-transform: uppercase; margin-bottom: 5px; font-weight: bold;}
    .metric-value { color: #2c3e50; font-size: 1.6rem; font-weight: 700; }
    .metric-sub { font-size: 0.8rem; color: #95a5a6; margin-top: 5px; }
    
    /* Botón Guardar */
    div.stButton > button {
        background: linear-gradient(90deg, #117864 0%, #1ABC9C 100%);
        color: white; border: none; padding: 12px 24px; border-radius: 8px; width: 100%;
        font-weight: bold; text-transform: uppercase;
    }
    div.stButton > button:hover { box-shadow: 0 5px 15px rgba(26, 188, 156, 0.4); }
    </style>
""", unsafe_allow_html=True)

# --- UI PRINCIPAL ---
st.title("💰 Gestor de Préstamos Personales")

menu = st.sidebar.radio("Menú", ["📝 Registrar Operación", "📊 Dashboard de Préstamos"])

if menu == "📝 Registrar Operación":
    st.markdown("### Nueva Solicitud de Crédito")
    st.info("💡 Este sistema calcula el interés mensual fijo (modalidad pago de intereses).")
    
    with st.container():
        st.markdown("**Datos del Cliente**")
        c1, c2, c3 = st.columns(3)
        cliente = c1.text_input("Nombre Completo")
        dni = c2.text_input("DNI / C.E.")
        telefono = c3.text_input("Teléfono / Celular")

        st.markdown("**Condiciones del Préstamo**")
        col_A, col_B = st.columns(2)
        
        with col_A:
            monto = st.number_input("Monto a Prestar (S/)", min_value=0.0, step=50.0)
            fecha_prestamo = st.date_input("Fecha del Préstamo", datetime.now())
        
        with col_B:
            tasa = st.number_input("Tasa de Interés Mensual (%)", value=15.0, step=1.0)
            observaciones = st.text_area("Observaciones (Opcional)", placeholder="Ej: Paga los días 15, es comerciante...")

    # --- LÓGICA DE PRESTAMISTA ---
    # Interés mensual puro
    interes_mensual = monto * (tasa / 100)
    # Día de pago sugerido (el mismo día del mes siguiente)
    dia_pago = fecha_prestamo.day

    st.markdown("---")
    st.markdown("#### 🔎 Resumen de la Operación")
    
    k1, k2, k3 = st.columns(3)
    
    # Tarjeta 1: Lo que te deben (Capital)
    k1.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Capital Prestado</div>
            <div class="metric-value">S/ {monto:,.2f}</div>
            <div class="metric-sub">Dinero entregado</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Tarjeta 2: Tu ganancia mensual (Lo importante)
    k2.markdown(f"""
        <div class="metric-card" style="border-left-color: #27AE60;">
            <div class="metric-title">Interés Mensual a Cobrar</div>
            <div class="metric-value" style="color: #27AE60;">S/ {interes_mensual:,.2f}</div>
            <div class="metric-sub">Cobrar cada día {dia_pago} del mes</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Tarjeta 3: Liquidación (Si paga todo en 1 mes)
    liquidacion = monto + interes_mensual
    k3.markdown(f"""
        <div class="metric-card" style="border-left-color: #E67E22;">
            <div class="metric-title">Monto para Liquidar</div>
            <div class="metric-value">S/ {liquidacion:,.2f}</div>
            <div class="metric-sub">Capital + 1 mes de interés</div>
        </div>
    """, unsafe_allow_html=True)

    st.write("")
    if st.button("💾 CONFIRMAR Y GUARDAR PRÉSTAMO"):
        if cliente and monto > 0:
            reg = {
                "Cliente": cliente,
                "DNI": dni,
                "Telefono": telefono,
                "Fecha_Prestamo": str(fecha_prestamo),
                "Dia_Cobro": dia_pago,
                "Monto_Capital": monto,
                "Tasa_Interes": tasa,
                "Pago_Mensual_Interes": interes_mensual,
                "Estado": "Activo",
                "Observaciones": observaciones
            }
            with st.spinner("Registrando en el sistema..."):
                if guardar_nuevo_prestamo(reg):
                    st.success(f"✅ Préstamo registrado. Debes cobrar S/ {interes_mensual:.2f} mensualmente a {cliente}.")
                    st.rerun()
        else:
            st.warning("⚠️ Por favor ingresa el Nombre del Cliente y el Monto.")

elif menu == "📊 Dashboard de Préstamos":
    st.markdown("### Estado de Cartera y Cobranzas")
    df = cargar_datos()
    
    if not df.empty:
        # Cálculos Gerenciales
        capital_calle = df[df["Estado"]=="Activo"]["Monto_Capital"].sum()
        flujo_mensual = df[df["Estado"]=="Activo"]["Pago_Mensual_Interes"].sum()
        clientes_activos = len(df[df["Estado"]=="Activo"])
        
        # Tarjetas Superiores
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="metric-card"><div class="metric-title">Capital en la Calle</div><div class="metric-value">S/ {capital_calle:,.2f}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card" style="border-left-color:#27AE60"><div class="metric-title">Flujo Mensual (Ganancia)</div><div class="metric-value" style="color:#27AE60">S/ {flujo_mensual:,.2f}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card"><div class="metric-title">Clientes Activos</div><div class="metric-value">{clientes_activos}</div></div>', unsafe_allow_html=True)
        
        st.write("---")
        st.markdown("#### 📋 Listado de Clientes")
        
        # Mostramos la tabla solo con las columnas útiles
        columnas_visibles = ["Cliente", "Telefono", "Fecha_Prestamo", "Dia_Cobro", "Monto_Capital", "Pago_Mensual_Interes", "Observaciones"]
        
        # Renombramos para que se vea bonito en la tabla
        df_display = df[columnas_visibles].rename(columns={
            "Monto_Capital": "Deuda Capital (S/)",
            "Pago_Mensual_Interes": "Pagar x Mes (S/)",
            "Dia_Cobro": "Día Pago",
            "Fecha_Prestamo": "Fecha Inicio"
        })
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
    else:
        st.info("📭 Aún no tienes préstamos registrados. Ve a 'Registrar Operación' para comenzar.")
