import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from github import Github

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestor de Préstamos", layout="wide", page_icon="💰")

# --- ESTILOS CSS (DISEÑO) ---
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
    
    div.stButton > button {
        background: linear-gradient(90deg, #117864 0%, #1ABC9C 100%);
        color: white; border: none; padding: 12px 24px; border-radius: 8px; width: 100%;
        font-weight: bold; text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE AUTENTICACIÓN ---
def check_login():
    """Verifica usuario y contraseña"""
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['usuario'] = ''
        st.session_state['rol'] = ''

    if not st.session_state['logged_in']:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("### 🔐 Acceso al Sistema")
            usuario = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            
            if st.button("Ingresar"):
                # Verificar credenciales en Secrets
                credenciales = st.secrets["credenciales"]
                admins = st.secrets["config"]["admins"]
                
                if usuario in credenciales and credenciales[usuario] == password:
                    st.session_state['logged_in'] = True
                    st.session_state['usuario'] = usuario
                    # Definir Rol
                    if usuario in admins:
                        st.session_state['rol'] = 'Admin'
                    else:
                        st.session_state['rol'] = 'Visor'
                    st.success("Acceso correcto. Cargando...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
        return False
    return True

def logout():
    st.session_state['logged_in'] = False
    st.session_state['usuario'] = ''
    st.session_state['rol'] = ''
    st.rerun()

# --- CONEXIÓN GITHUB ---
def get_repo():
    token = st.secrets["GITHUB_TOKEN"]
    g = Github(token)
    return g.get_repo(st.secrets["REPO_NAME"])

def cargar_datos():
    try:
        repo = get_repo()
        contents = repo.get_contents("data.json")
        datos = json.loads(contents.decoded_content.decode())
        if not datos: return pd.DataFrame()
        return pd.DataFrame(datos)
    except: return pd.DataFrame()

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
        st.error(f"Error: {e}")
        return False

# --- EJECUCIÓN PRINCIPAL ---

if check_login():
    # BARRA LATERAL (SIDEBAR)
    st.sidebar.title(f"👤 {st.session_state['usuario'].title()}")
    st.sidebar.caption(f"Rol: {st.session_state['rol']}")
    
    if st.sidebar.button("Cerrar Sesión"):
        logout()
    
    st.sidebar.markdown("---")
    
    # MENÚ SEGÚN ROL
    opciones = ["📊 Dashboard de Préstamos"] # Todos ven esto
    
    if st.session_state['rol'] == 'Admin':
        opciones.insert(0, "📝 Registrar Operación") # Solo Admin ve esto
        
    menu = st.sidebar.radio("Menú Principal", opciones)

    # --- PÁGINA: REGISTRAR (SOLO ADMIN) ---
    if menu == "📝 Registrar Operación":
        st.title("💰 Registrar Nuevo Préstamo")
        st.info("💡 Modalidad: Pago mensual de interés (Capital al final).")
        
        with st.container():
            st.markdown("**Datos del Cliente**")
            c1, c2, c3 = st.columns(3)
            cliente = c1.text_input("Nombre Completo")
            dni = c2.text_input("DNI / C.E.")
            telefono = c3.text_input("Teléfono / Celular")

            st.markdown("**Condiciones Financieras**")
            col_A, col_B = st.columns(2)
            with col_A:
                monto = st.number_input("Monto a Prestar (S/)", min_value=0.0, step=50.0)
                fecha_prestamo = st.date_input("Fecha Desembolso", datetime.now())
            with col_B:
                tasa = st.number_input("Tasa Interés Mensual (%)", value=15.0, step=1.0)
                observaciones = st.text_area("Observaciones", placeholder="Ej: Comerciante, paga los días 15...")

        # Cálculos en vivo
        interes_mensual = monto * (tasa / 100)
        dia_pago = fecha_prestamo.day
        
        st.markdown("---")
        k1, k2, k3 = st.columns(3)
        k1.markdown(f'<div class="metric-card"><div class="metric-title">Capital</div><div class="metric-value">S/ {monto:,.2f}</div></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="metric-card" style="border-left-color:#27AE60"><div class="metric-title">Cobro Mensual</div><div class="metric-value" style="color:#27AE60">S/ {interes_mensual:,.2f}</div><div class="metric-sub">Día {dia_pago} de cada mes</div></div>', unsafe_allow_html=True)
        k3.markdown(f'<div class="metric-card" style="border-left-color:#E67E22"><div class="metric-title">Liquidación Total</div><div class="metric-value">S/ {(monto+interes_mensual):,.2f}</div></div>', unsafe_allow_html=True)

        st.write("")
        if st.button("💾 GUARDAR PRÉSTAMO"):
            if cliente and monto > 0:
                reg = {
                    "Cliente": cliente, "DNI": dni, "Telefono": telefono,
                    "Fecha_Prestamo": str(fecha_prestamo), "Dia_Cobro": dia_pago,
                    "Monto_Capital": monto, "Tasa_Interes": tasa,
                    "Pago_Mensual_Interes": interes_mensual, "Estado": "Activo",
                    "Observaciones": observaciones,
                    "Registrado_Por": st.session_state['usuario'] # Auditoría
                }
                with st.spinner("Procesando..."):
                    if guardar_nuevo_prestamo(reg):
                        st.success("✅ ¡Operación registrada con éxito!")
                        time.sleep(1)
                        st.rerun()
            else:
                st.warning("Faltan datos obligatorios")

    # --- PÁGINA: DASHBOARD (TODOS) ---
    elif menu == "📊 Dashboard de Préstamos":
        st.title("📊 Estado de la Cartera")
        df = cargar_datos()
        
        if not df.empty:
            capital_calle = df[df["Estado"]=="Activo"]["Monto_Capital"].sum()
            flujo_mensual = df[df["Estado"]=="Activo"]["Pago_Mensual_Interes"].sum()
            clientes_activos = len(df[df["Estado"]=="Activo"])
            
            c1, c2, c3 = st.columns(3)
            c1.markdown(f'<div class="metric-card"><div class="metric-title">Capital Activo</div><div class="metric-value">S/ {capital_calle:,.2f}</div></div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="metric-card" style="border-left-color:#27AE60"><div class="metric-title">Ingreso Mensual Fijo</div><div class="metric-value" style="color:#27AE60">S/ {flujo_mensual:,.2f}</div></div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="metric-card"><div class="metric-title">Préstamos</div><div class="metric-value">{clientes_activos}</div></div>', unsafe_allow_html=True)
            
            st.write("---")
            st.markdown("#### 📋 Listado Detallado")
            
            # Filtro de búsqueda
            filtro = st.text_input("🔍 Buscar cliente por nombre...")
            if filtro:
                df = df[df["Cliente"].str.contains(filtro, case=False, na=False)]
            
            # Mostrar tabla
            cols_ver = ["Cliente", "Telefono", "Fecha_Prestamo", "Dia_Cobro", "Monto_Capital", "Pago_Mensual_Interes", "Observaciones"]
            df_show = df[cols_ver].rename(columns={
                "Monto_Capital": "Deuda (S/)", "Pago_Mensual_Interes": "Mensualidad (S/)", 
                "Dia_Cobro": "Día Pago", "Fecha_Prestamo": "Inicio"
            })
            st.dataframe(df_show, use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos cargados en el sistema.")
