import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from github import Github

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="Sistema Financiero", 
    layout="wide", 
    page_icon="🏦",
    initial_sidebar_state="expanded"
)

# --- 2. ESTILOS CSS PREMIUM (DISEÑO TOTAL) ---
st.markdown("""
    <style>
    /* Importar fuente profesional Roboto */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        background-color: #F0F2F6; /* Fondo gris muy suave */
    }
    
    /* --- ESTILOS DE LOGIN --- */
    .login-container {
        background-color: white;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        text-align: center;
        margin-top: 50px;
    }
    
    /* --- TARJETAS DE MÉTRICAS (KPIs) --- */
    .metric-card {
        background: linear-gradient(to bottom right, #ffffff, #f8f9fa);
        border-radius: 12px;
        padding: 20px;
        border-left: 6px solid #154360; /* Azul Corporativo */
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
    }
    .metric-title {
        color: #7F8C8D;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .metric-value {
        color: #154360;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .metric-sub {
        font-size: 0.85rem;
        color: #95A5A6;
        margin-top: 5px;
    }
    
    /* --- BOTONES PERSONALIZADOS --- */
    div.stButton > button {
        background: linear-gradient(90deg, #1A5276 0%, #2980B9 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
        text-transform: uppercase;
        width: 100%;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #154360 0%, #2471A3 100%);
        box-shadow: 0 4px 12px rgba(41, 128, 185, 0.4);
    }
    
    /* --- TABLAS DE DATOS --- */
    [data-testid="stDataFrame"] {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* --- ALERTAS --- */
    .alert-box {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        font-weight: 500;
        display: flex;
        align-items: center;
    }
    .alert-danger { background-color: #FDEDEC; color: #E74C3C; border: 1px solid #FADBD8; }
    .alert-warning { background-color: #FEF9E7; color: #F1C40F; border: 1px solid #FCF3CF; }
    
    </style>
""", unsafe_allow_html=True)

# --- 3. GESTIÓN DE SESIÓN Y GITHUB ---
def check_login():
    if 'logged_in' not in st.session_state:
        st.session_state.update({'logged_in': False, 'usuario': '', 'rol': ''})

    if not st.session_state['logged_in']:
        # Diseño de Login Centrado
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.title("🔒 Acceso Seguro")
            st.caption("Sistema de Gestión de Créditos")
            
            usuario = st.text_input("Usuario", placeholder="Ingrese su usuario")
            password = st.text_input("Contraseña", type="password", placeholder="••••••")
            
            st.write("")
            if st.button("INICIAR SESIÓN"):
                creds = st.secrets["credenciales"]
                if usuario in creds and creds[usuario] == password:
                    st.session_state.update({'logged_in': True, 'usuario': usuario})
                    st.session_state['rol'] = 'Admin' if usuario in st.secrets["config"]["admins"] else 'Visor'
                    st.toast(f"¡Bienvenido, {usuario.title()}!", icon="👋")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
            st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

def logout():
    st.session_state.update({'logged_in': False, 'usuario': '', 'rol': ''})
    st.rerun()

def get_repo():
    return Github(st.secrets["GITHUB_TOKEN"]).get_repo(st.secrets["REPO_NAME"])

def cargar_datos():
    try:
        c = get_repo().get_contents("data.json")
        return json.loads(c.decoded_content.decode()), c.sha
    except: return [], None

def guardar_datos(datos, sha, mensaje):
    try:
        repo = get_repo()
        repo.update_file("data.json", mensaje, json.dumps(datos, indent=4), sha)
        return True
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return False

# --- 4. INTERFAZ PRINCIPAL ---
if check_login():
    # --- SIDEBAR (Menú Lateral) ---
    with st.sidebar:
        st.markdown(f"## 👤 {st.session_state['usuario'].title()}")
        st.caption(f"Perfil: {st.session_state['rol']}")
        st.markdown("---")
        
        opciones = ["📊 Dashboard General"]
        if st.session_state['rol'] == 'Admin':
            opciones = ["📝 Nuevo Préstamo", "💸 Registrar Pago"] + opciones
        
        menu = st.radio("Navegación", opciones)
        
        st.markdown("---")
        if st.button("Cerrar Sesión"): logout()

    # --- LÓGICA DE PÁGINAS ---

    # 1. REGISTRAR NUEVO PRÉSTAMO
    if menu == "📝 Nuevo Préstamo":
        st.subheader("📝 Solicitud de Crédito")
        st.markdown("ingrese los datos del nuevo cliente.")
        
        with st.container(border=True):
            st.markdown("#### Datos Personales")
            c1, c2, c3 = st.columns(3)
            cliente = c1.text_input("Nombre Completo")
            dni = c2.text_input("DNI / C.E.")
            telefono = c3.text_input("Teléfono / Celular")
            
            st.markdown("#### Condiciones Financieras")
            col_A, col_B = st.columns(2)
            with col_A:
                monto = st.number_input("Capital a Prestar (S/)", min_value=0.0, step=50.0)
                fecha = st.date_input("Fecha Desembolso", datetime.now())
            with col_B:
                tasa = st.number_input("Tasa Interés Mensual (%)", value=15.0)
                obs = st.text_area("Observaciones", placeholder="Ej: Negocio propio, paga puntual...")

        # Cálculos
        interes = monto * (tasa/100)
        
        st.markdown("---")
        k1, k2, k3 = st.columns(3)
        k1.markdown(f'<div class="metric-card"><div class="metric-title">Monto Capital</div><div class="metric-value">S/ {monto:,.2f}</div></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="metric-card" style="border-left-color:#27AE60"><div class="metric-title">Cuota Interés Mensual</div><div class="metric-value" style="color:#27AE60">S/ {interes:,.2f}</div><div class="metric-sub">Cobrar día {fecha.day} de cada mes</div></div>', unsafe_allow_html=True)
        k3.markdown(f'<div class="metric-card" style="border-left-color:#F39C12"><div class="metric-title">Tasa Aplicada</div><div class="metric-value">{tasa}%</div></div>', unsafe_allow_html=True)
        
        st.write("")
        if st.button("💾 GUARDAR OPERACIÓN"):
            if cliente and monto > 0:
                nuevo = {
                    "Cliente": cliente, "DNI": dni, "Telefono": telefono,
                    "Fecha_Prestamo": str(fecha), "Dia_Cobro": fecha.day,
                    "Monto_Capital": monto, "Tasa_Interes": tasa,
                    "Pago_Mensual_Interes": interes, "Estado": "Activo",
                    "Observaciones": obs
                }
                datos, sha = cargar_datos()
                datos.append(nuevo)
                if guardar_datos(datos, sha, f"Nuevo prestamo: {cliente}"):
                    st.success("✅ Préstamo registrado correctamente.")
                    time.sleep(1)
                    st.rerun()
            else:
                st.warning("⚠️ Complete Nombre y Monto.")

    # 2. CAJA Y PAGOS
    elif menu == "💸 Registrar Pago":
        st.subheader("💸 Gestión de Cobranza")
        datos, sha = cargar_datos()
        
        activos = [d for d in datos if d.get('Estado') == 'Activo']
        
        if activos:
            mapa = {f"{d['Cliente']} | Deuda: S/{d['Monto_Capital']}": i for i, d in enumerate(datos) if d.get('Estado') == 'Activo'}
            seleccion = st.selectbox("Buscar Cliente", list(mapa.keys()))
            idx = mapa[seleccion]
            data = datos[idx]
            
            with st.container(border=True):
                st.markdown(f"### 👤 {data['Cliente']}")
                st.caption(f"📞 Teléfono: {data.get('Telefono', 'No registrado')}")
                
                c_info1, c_info2 = st.columns(2)
                c_info1.metric("Deuda Capital Actual", f"S/ {data['Monto_Capital']:,.2f}")
                c_info2.metric("Interés que DEBE pagar", f"S/ {data['Pago_Mensual_Interes']:,.2f}")

            st.write("")
            st.markdown("### 💰 Ingreso de Dinero")
            st.caption("Ingresa los montos exactos que recibiste. El sistema ajustará la deuda automáticamente.")

            col_pago1, col_pago2 = st.columns(2)
            
            with col_pago1:
                pago_interes = st.number_input("1. ¿Cuánto pagó de INTERÉS?", 
                                               min_value=0.0, 
                                               value=float(data['Pago_Mensual_Interes']), 
                                               step=10.0,
                                               help="Si paga menos de lo que debe, la diferencia aumenta la deuda.")
            
            with col_pago2:
                pago_capital = st.number_input("2. ¿Cuánto pagó de CAPITAL?", 
                                               min_value=0.0, 
                                               value=0.0, 
                                               step=50.0,
                                               help="Dinero extra para bajar la deuda.")

            # --- LÓGICA DE NEGOCIO ---
            interes_pendiente = data['Pago_Mensual_Interes'] - pago_interes
            # Regla: Nuevo Capital = Capital Anterior - Lo que amortizó + Lo que no pagó de interés
            nuevo_capital = data['Monto_Capital'] - pago_capital + interes_pendiente
            
            # Recalcular interés para el próximo mes
            nueva_cuota = nuevo_capital * (data['Tasa_Interes'] / 100)

            st.markdown("---")
            st.markdown("#### 📊 Resultado de la Operación")
            
            col_res1, col_res2 = st.columns(2)
            
            with col_res1:
                # Análisis del pago de interés
                if interes_pendiente > 0:
                    st.warning(f"⚠️ **Pago Incompleto:** Faltaron S/ {interes_pendiente:,.2f} de interés.")
                    st.markdown(f"👉 Esos **S/ {interes_pendiente:,.2f}** se sumarán a la deuda de Capital.")
                elif interes_pendiente < 0:
                     st.success(f"🎉 **Pago Extra:** Pagó S/ {abs(interes_pendiente):,.2f} de más en intereses.")
                     st.markdown("👉 Este excedente restará la deuda de Capital.")
                else:
                    st.success("✅ Interés pagado completo.")

                # Análisis del pago de capital
                if pago_capital > 0:
                    st.info(f"📉 **Amortización:** La deuda baja S/ {pago_capital:,.2f} adicionales.")

            with col_res2:
                st.markdown(f"""
                <div style="background-color:#EBF5FB; padding:15px; border-radius:10px; border:1px solid #AED6F1;">
                    <h4 style="margin:0; color:#1B4F72;">Nueva Deuda Total: S/ {nuevo_capital:,.2f}</h4>
                    <p style="margin:0; color:#5D6D7E; font-size:0.9em;">(Anterior: S/ {data['Monto_Capital']:,.2f})</p>
                    <hr style="margin:10px 0;">
                    <h4 style="margin:0; color:#186A3B;">Nueva Cuota Mensual: S/ {nueva_cuota:,.2f}</h4>
                    <p style="margin:0; color:#5D6D7E; font-size:0.9em;">(A cobrar el próximo mes)</p>
                </div>
                """, unsafe_allow_html=True)
                
            st.write("")
            if st.button("💾 PROCESAR Y ACTUALIZAR"):
                # Actualizamos el registro en memoria
                data['Monto_Capital'] = nuevo_capital
                data['Pago_Mensual_Interes'] = nueva_cuota
                
                # Si la deuda llega a cero o menos, se cancela
                if nuevo_capital <= 0:
                    data['Estado'] = "Pagado"
                    data['Monto_Capital'] = 0
                    data['Pago_Mensual_Interes'] = 0
                    msg_log = "Deuda Cancelada Totalmente"
                else:
                    msg_log = f"Pago: Int S/{pago_interes} Cap S/{pago_capital}"
                
                # Guardamos en GitHub
                if guardar_datos(datos, sha, f"Actualizacion {data['Cliente']} - {msg_log}"):
                    st.success("✅ Cartera actualizada correctamente.")
                    time.sleep(2)
                    st.rerun()

    # 3. DASHBOARD GERENCIAL
    elif menu == "📊 Dashboard General":
        st.subheader("📊 Resumen Ejecutivo")
        datos, _ = cargar_datos()
        
        if datos:
            df = pd.DataFrame(datos)
            df = df[df['Estado'] == 'Activo']
            
            # --- NOTIFICACIONES ---
            hoy = datetime.now().day
            c1, c2 = st.columns([2, 1])
            
            with c1:
                # KPIs Principales
                total = df['Monto_Capital'].sum()
                ganancia = df['Pago_Mensual_Interes'].sum()
                
                k1, k2, k3 = st.columns(3)
                k1.markdown(f'<div class="metric-card"><div class="metric-title">Capital Activo</div><div class="metric-value">S/ {total:,.2f}</div></div>', unsafe_allow_html=True)
                k2.markdown(f'<div class="metric-card" style="border-left-color:#27AE60"><div class="metric-title">Flujo Mensual</div><div class="metric-value" style="color:#27AE60">S/ {ganancia:,.2f}</div></div>', unsafe_allow_html=True)
                k3.markdown(f'<div class="metric-card" style="border-left-color:#8E44AD"><div class="metric-title">Clientes</div><div class="metric-value">{len(df)}</div></div>', unsafe_allow_html=True)
            
            with c2:
                # Alertas Compactas
                st.markdown("##### 📅 Vencimientos Próximos")
                hay_alertas = False
                for _, row in df.iterrows():
                    dia = int(row['Dia_Cobro'])
                    diff = dia - hoy
                    if diff == 0:
                        st.markdown(f"<div class='alert-box alert-danger'>🚨 {row['Cliente']} paga HOY</div>", unsafe_allow_html=True)
                        hay_alertas = True
                    elif 0 < diff <= 3:
                        st.markdown(f"<div class='alert-box alert-warning'>⚠️ {row['Cliente']} paga en {diff} días</div>", unsafe_allow_html=True)
                        hay_alertas = True
                if not hay_alertas:
                    st.caption("No hay cobros urgentes para los próximos 3 días.")

            # --- TABLA BONITA ---
            st.markdown("### 📋 Cartera de Clientes")
            
            # Preparar tabla para visualización
            tabla_view = df[["Cliente", "Telefono", "Monto_Capital", "Pago_Mensual_Interes", "Dia_Cobro", "Observaciones"]]
            
            st.dataframe(
                tabla_view,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Cliente": st.column_config.TextColumn("Cliente", width="medium"),
                    "Telefono": st.column_config.TextColumn("Contacto", width="small"),
                    "Monto_Capital": st.column_config.NumberColumn("Deuda Capital", format="S/ %.2f"),
                    "Pago_Mensual_Interes": st.column_config.NumberColumn("Cuota Interés", format="S/ %.2f"),
                    "Dia_Cobro": st.column_config.NumberColumn("Día Pago", format="%d"),
                    "Observaciones": st.column_config.TextColumn("Notas", width="large"),
                }
            )
        else:
            st.info("No hay datos registrados en el sistema.")
