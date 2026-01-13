import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
import calendar # Importamos calendario para calcular días exactos
from github import Github
import urllib.parse # NUEVO: Para codificar mensajes de WhatsApp

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="Sistema Financiero", 
    layout="wide", 
    page_icon="🏦",
    initial_sidebar_state="expanded"
)

# --- 2. ESTILOS CSS PREMIUM (DISEÑO TOTAL CENTRADO) ---
st.markdown("""
    <style>
    /* Importar fuente profesional Roboto */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        background-color: #F0F2F6; /* Fondo gris muy suave */
    }
    
    /* --- CENTRADO GLOBAL FORZADO --- */
    h1, h2, h3, h4, h5, h6, .stMarkdown, p {
        text-align: center !important;
    }
  
    /* --- MÉTRICAS DORADAS EJECUTIVAS --- */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%) !important;
        border: 2px solid #996515 !important;
        border-radius: 15px !important;
        padding: 15px !important;
        box-shadow: 0 8px 15px rgba(0,0,0,0.2) !important;
    }
    
    /* Color de los títulos de las métricas (Labels) */
    [data-testid="stMetricLabel"] div p {
        color: #1C1C1C !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }

    /* Color de los números de las métricas (Values) */
    [data-testid="stMetricValue"] div {
        color: #1C1C1C !important;
        font-weight: 700 !important;
    }
    
    /* Color de la flechita de variación (Delta) */
    [data-testid="stMetricDelta"] div {
        background-color: rgba(28, 28, 28, 0.1) !important;
        border-radius: 5px;
        padding: 2px 5px;
    }
    
    /* --- ESTILOS DE LOGIN --- */
    .login-container {
        background-color: white;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        text-align: center;
        margin-top: 50px;
        margin-bottom: 50px;
    }
    
    /* --- TARJETAS DE MÉTRICAS (KPIs) --- */
    .metric-card {
        background: linear-gradient(to bottom right, #ffffff, #f8f9fa);
        border-radius: 12px;
        padding: 20px;
        border-left: 6px solid #154360; /* Azul Corporativo */
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s;
        text-align: center; /* Centrar texto interno */
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
        text-align: center;
    }
    .metric-value {
        color: #154360;
        font-size: 1.8rem;
        font-weight: 700;
        text-align: center;
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
    
    /* --- BOTÓN WHATSAPP PREMIUM --- */
    .wa-button {
        background-color: #25D366;
        color: white !important;
        padding: 10px 20px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        box-shadow: 0 4px 10px rgba(37, 211, 102, 0.3);
        transition: 0.3s;
        width: 100%;
        margin-top: 5px;
    }
    .wa-button:hover {
        background-color: #128C7E;
        transform: scale(1.02);
    }
    
    /* --- TABLAS DE DATOS --- */
    [data-testid="stDataFrame"] {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin: auto; /* Centrar tabla si sobra espacio */
    }
    
    /* --- ALERTAS --- */
    .alert-box {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        font-weight: 500;
        display: flex;
        align-items: center;
        justify-content: center; /* Centrar contenido de alerta */
    }
    .alert-danger { background-color: #FDEDEC; color: #E74C3C; border: 1px solid #FADBD8; }
    .alert-warning { background-color: #FEF9E7; color: #F1C40F; border: 1px solid #FCF3CF; }
    .alert-success { background-color: #E8F8F5; color: #186A3B; border: 1px solid #A9DFBF; }
    
    /* Eliminar borde feo del formulario de Streamlit */
    [data-testid="stForm"] { border: none; padding: 0; }

    /* --- CAMBIO A DORADO EJECUTIVO --- */
    :root { --gold: #D4AF37; --dark: #1C1C1C; }
    h1, h2, h3, .stMarkdown h1, .stMarkdown h2 { color: #D4AF37 !important; font-family: 'Playfair Display', serif; }
    div.stButton > button {
        background: linear-gradient(90deg, #D4AF37 0%, #996515 100%) !important;
        border: 1px solid #C5A059 !important;
    }
    [data-testid="stMetric"] { border: 1px solid #D4AF37; border-radius: 10px; background: #1C1C1C; }

    /* --- ACTUALIZACIÓN SPLASH SCREEN CON GIF --- */
    @keyframes fade-out {
        0% { opacity: 1; }
        90% { opacity: 1; }
        100% { opacity: 0; }
    }
    .splash-overlay {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: #0E1117;
        display: flex; flex-direction: column;
        justify-content: center; align-items: center;
        z-index: 99999;
        animation: fade-out 3s forwards;
    }
    .gif-container {
        width: 300px;
        height: 300px;
    }

    .header-box {
        background-color: #1C1C1C;
        border: 2px solid #D4AF37;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
        text-align: center;
    }
    
    </style>
""", unsafe_allow_html=True)

# --- 3. FUNCIONES DE LÓGICA DE CALENDARIO ---
def sumar_un_mes(fecha_str):
    """Suma 1 mes exacto respetando si el mes siguiente tiene menos días (ej: 31 Enero -> 28 Febrero)"""
    fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d")
    mes_nuevo = fecha_dt.month + 1
    anio_nuevo = fecha_dt.year
    
    if mes_nuevo > 12:
        mes_nuevo = 1
        anio_nuevo += 1
    
    # Obtener el último día del nuevo mes
    _, ult_dia_mes = calendar.monthrange(anio_nuevo, mes_nuevo)
    
    # Si el día original es 31, pero el nuevo mes tiene 28, usamos 28.
    dia_nuevo = min(fecha_dt.day, ult_dia_mes)
    
    return datetime(anio_nuevo, mes_nuevo, dia_nuevo).strftime("%Y-%m-%d")

# --- NUEVA FUNCIÓN: GENERAR LINK WHATSAPP ---
def generar_link_whatsapp(telefono, cliente, monto, fecha, tipo):
    # Limpiar el teléfono de espacios o caracteres
    tel_limpio = "".join(filter(str.isdigit, str(telefono)))
    # Añadir prefijo de país si no lo tiene (Ejemplo 51 para Perú, cámbialo si es otro país)
    if len(tel_limpio) == 9: tel_limpio = "51" + tel_limpio
    
    if tipo == "recordatorio":
        mensaje = f"Hola *{cliente}* 👋, te recordamos que tu cuota de *S/ {monto:,.2f}* vence el próximo *{fecha}*. ¡Que tengas un gran día!"
    elif tipo == "hoy":
        mensaje = f"Hola *{cliente}* 🔔, te informamos que *hoy* vence tu cuota de *S/ {monto:,.2f}*. Por favor, realiza el pago para evitar recargos. Gracias."
    elif tipo == "mora":
        mensaje = f"Estimado(a) *{cliente}* ⚠️, tu cuota de *S/ {monto:,.2f}* presenta un retraso. Por favor, comunícate con nosotros lo antes posible para regularizar tu situación."
    
    msg_encoded = urllib.parse.quote(mensaje)
    return f"https://wa.me/{tel_limpio}?text={msg_encoded}"

def registrar_auditoria(accion, detalle, cliente="-"):
    try:
        repo = get_repo()
        try:
            c = repo.get_contents("audit.json")
            logs = json.loads(c.decoded_content.decode())
            sha = c.sha
        except:
            logs = []; sha = None
        
        nuevo_log = {
            "Fecha/Hora": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "Usuario": st.session_state.get('usuario', 'Sistema').title(),
            "Perfil": st.session_state.get('rol', '-'),
            "Operación": accion,
            "Cliente Afectado": cliente,
            "Detalle del Movimiento": detalle
        }
        logs.append(nuevo_log)
        
        if sha: repo.update_file("audit.json", f"Log: {accion}", json.dumps(logs, indent=4), sha)
        else: repo.create_file("audit.json", "Init Audit", json.dumps(logs, indent=4))
    except Exception as e:
        print(f"Error Auditoría: {e}")
        
# --- 4. GESTIÓN DE SESIÓN Y GITHUB ---
def check_login():
    # --- PERSISTENCIA F5 ---
    q = st.query_params
    if 'logged_in' not in st.session_state:
        if "user" in q:
            st.session_state.update({'logged_in': True, 'usuario': q["user"], 'rol': q["rol"], 'splash_visto': True})
        else:
            st.session_state.update({'logged_in': False, 'usuario': '', 'rol': ''})

    if not st.session_state['logged_in']:
        # Diseño de Login Centrado
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.title("🔒 Acceso Seguro")
            st.caption("Sistema de Gestión de Créditos")
            
            with st.form("login_form"):
                usuario = st.text_input("Usuario", placeholder="Ingrese su usuario")
                password = st.text_input("Contraseña", type="password", placeholder="••••••")
                st.write("")
                submit_button = st.form_submit_button("INICIAR SESIÓN", type="primary")

            if submit_button:
                creds = st.secrets["credenciales"]
                if usuario in creds and creds[usuario] == password:
                    st.session_state.update({'logged_in': True, 'usuario': usuario})
                    st.session_state['rol'] = 'Admin' if usuario in st.secrets["config"]["admins"] else 'Visor'
                    
                    # LOG DE AUDITORÍA DE ACCESO
                    registrar_auditoria("INICIO DE SESIÓN", f"El usuario {usuario} accedió al portal con perfil {st.session_state['rol']}")
                    
                    st.toast(f"¡Bienvenido, {usuario.title()}!", icon="👋")
                    st.query_params["user"] = usuario
                    st.query_params["rol"] = st.session_state['rol']
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas, contáctese con el administrador del portal.")
            
            st.markdown('</div>', unsafe_allow_html=True)
        return False

    # --- SPLASH SCREEN CON GIF DE ALIEN ---
    if 'splash_visto' not in st.session_state:
        placeholder = st.empty()
        with placeholder.container():
            st.markdown(f"""
                <div class="splash-overlay">
                    <div class="gif-container">
                        <iframe src="https://tenor.com/embed/1281825661231862493" 
                                width="100%" height="100%" frameborder="0" allowfullscreen>
                        </iframe>
                    </div>
                    <h2 style="color:#D4AF37; margin-top:20px;">INICIANDO SISTEMA FINANCIERO...</h2>
                </div>
            """, unsafe_allow_html=True)
            time.sleep(3.5) # Tiempo suficiente para ver la animación
        placeholder.empty()
        st.session_state['splash_visto'] = True

    return True

def logout():
    st.session_state.update({'logged_in': False, 'usuario': '', 'rol': ''})
    st.rerun()

def get_repo():
    return Github(st.secrets["GITHUB_TOKEN"]).get_repo(st.secrets["REPO_NAME"])

def cargar_datos(file="data.json"):
    try:
        c = get_repo().get_contents(file)
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

# --- 5. INTERFAZ PRINCIPAL ---
if check_login():
    # --- SIDEBAR (Menú Lateral) ---
    with st.sidebar:
        st.markdown(f"<h2 style='text-align: center;'>👤 {st.session_state['usuario'].title()}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: gray;'>Perfil: {st.session_state['rol']}</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        opciones = ["📊 Dashboard General"]
        if st.session_state['rol'] == 'Admin':
            opciones = ["📝 Nuevo Préstamo", "💸 Registrar Pago", "📜 Auditoría"] + opciones
        
        menu = st.radio("Navegación", opciones)
        
        st.markdown("---")
        if st.button("Cerrar Sesión"): logout()

    # --- LÓGICA DE PÁGINAS ---

    # 1. REGISTRAR NUEVO PRÉSTAMO
    if menu == "📝 Nuevo Préstamo":
        st.markdown("""<div class="header-box">
                    <h1>📝 SOLICITUD DE CRÉDITO</h1>
                    <p style="color:#D4AF37;">Ingrese los datos del nuevo cliente para la emisión del préstamo.</p>
                   </div>""", unsafe_allow_html=True)
        
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
                fecha_inicio = st.date_input("Fecha Desembolso", datetime.now())
            with col_B:
                tasa = st.number_input("Tasa Interés Mensual (%)", value=15.0)
                obs = st.text_area("Observaciones", placeholder="Ej: Negocio propio, paga puntual...")

        # Cálculos Avanzados
        interes = monto * (tasa/100)
        
        # Calcular la PRIMERA fecha de pago (Mes exacto siguiente)
        fecha_inicio_str = str(fecha_inicio)
        prox_pago = sumar_un_mes(fecha_inicio_str)
        # Formato bonito para mostrar
        fecha_bonita = datetime.strptime(prox_pago, "%Y-%m-%d").strftime("%d/%m/%Y")

        st.markdown("---")
        k1, k2, k3 = st.columns(3)
        k1.markdown(f'<div class="metric-card"><div class="metric-title">Monto Capital</div><div class="metric-value">S/ {monto:,.2f}</div></div>', unsafe_allow_html=True)
        k2.markdown(f'<div class="metric-card" style="border-left-color:#27AE60"><div class="metric-title">Cuota Interés Mensual</div><div class="metric-value" style="color:#27AE60">S/ {interes:,.2f}</div></div>', unsafe_allow_html=True)
        k3.markdown(f'<div class="metric-card" style="border-left-color:#F39C12"><div class="metric-title">1er Vencimiento</div><div class="metric-value">{fecha_bonita}</div></div>', unsafe_allow_html=True)
        
        st.write("")
        
        if 'guardando_prestamo' not in st.session_state:
            st.session_state.guardando_prestamo = False

        if st.button("💾 GUARDAR OPERACIÓN", disabled=st.session_state.guardando_prestamo):
            if cliente and monto > 0:
                st.session_state.guardando_prestamo = True # Bloquear el botón
                
                nuevo = {
                    "Cliente": cliente, "DNI": dni, "Telefono": telefono,
                    "Fecha_Prestamo": str(fecha_inicio),
                    "Fecha_Proximo_Pago": prox_pago,
                    "Monto_Capital": monto, "Tasa_Interes": tasa,
                    "Pago_Mensual_Interes": interes, "Estado": "Activo",
                    "Observaciones": obs
                }
                datos, sha = cargar_datos()
                datos.append(nuevo)
                if guardar_datos(datos, sha, f"Nuevo prestamo: {cliente}"):
                    registrar_auditoria("CREACIÓN CRÉDITO", f"Desembolso de S/ {monto}", cliente=cliente)
                    st.success("✅ Préstamo registrado correctamente.")
                    time.sleep(1)
                    st.session_state.guardando_prestamo = False # Liberar
                    st.rerun()
            else:
                st.warning("⚠️ Complete Nombre y Monto.")

    # 2. CAJA Y PAGOS
    elif menu == "💸 Registrar Pago":
        st.markdown("""<div class="header-box">
                    <h1>💸 GESTIÓN DE COBRANZA</h1>
                    <p style="color:#D4AF37;">Registre los ingresos de capital e intereses de la cartera activa.</p>
                   </div>""", unsafe_allow_html=True)

        datos, sha = cargar_datos()
        
        activos = [d for d in datos if d.get('Estado') == 'Activo']
        
        if activos:
            mapa = {f"{d['Cliente']} | Vence: {d.get('Fecha_Proximo_Pago', 'N/A')}": i for i, d in enumerate(datos) if d.get('Estado') == 'Activo'}
            col_sel1, col_sel2, col_sel3 = st.columns([1, 2, 1])
            with col_sel2:
                seleccion = st.selectbox("Buscar Cliente", list(mapa.keys()))
            
            idx = mapa[seleccion]
            data = datos[idx]
            
            fecha_venc_dt = datetime.strptime(data['Fecha_Proximo_Pago'], "%Y-%m-%d").date()
            hoy = datetime.now().date()
            dias_restantes = (fecha_venc_dt - hoy).days

            with st.container(border=True):
                st.markdown(f"### 👤 {data['Cliente']}")
                
                c_info1, c_info2, c_info3 = st.columns(3)
                c_info1.metric("Deuda Capital", f"S/ {data['Monto_Capital']:,.2f}")
                c_info2.metric("Cuota Interés", f"S/ {data['Pago_Mensual_Interes']:,.2f}")
                
                color_delta = "normal"
                txt_venc = f"En {dias_restantes} días"
                if dias_restantes < 0: 
                    txt_venc = f"Vencido hace {abs(dias_restantes)} días"
                    color_delta = "inverse"
                elif dias_restantes == 0:
                    txt_venc = "Vence HOY"
                    color_delta = "off"

                c_info3.metric("Vencimiento", fecha_venc_dt.strftime("%d/%m/%Y"), delta=txt_venc, delta_color=color_delta)

            st.write("")
            st.markdown("### 💰 Ingreso de Dinero")
            st.caption("Ingresa los montos exactos que recibiste.")

            col_pago1, col_pago2 = st.columns(2)
            with col_pago1:
                pago_interes = st.number_input("1. ¿Cuánto pagó de INTERÉS?", 
                                               min_value=0.0, value=float(data['Pago_Mensual_Interes']), step=10.0)
            with col_pago2:
                pago_capital = st.number_input("2. ¿Cuánto pagó de CAPITAL?", 
                                               min_value=0.0, value=0.0, step=50.0)

            st.write("")
            col_chk1, col_chk2 = st.columns([1, 3])
            with col_chk2:
                sugerir_renovar = (pago_interes >= (data['Pago_Mensual_Interes'] - 5))
                renovar = st.checkbox("📅 **¿Renovar vencimiento al próximo mes?**", value=sugerir_renovar)

            interes_pendiente = data['Pago_Mensual_Interes'] - pago_interes
            nuevo_capital = data['Monto_Capital'] - pago_capital + interes_pendiente
            nueva_cuota = nuevo_capital * (data['Tasa_Interes'] / 100)
            
            nueva_fecha_pago = data['Fecha_Proximo_Pago']
            txt_fecha_nueva = "Se mantiene igual"
            if renovar:
                nueva_fecha_pago = sumar_un_mes(data['Fecha_Proximo_Pago'])
                txt_fecha_nueva = datetime.strptime(nueva_fecha_pago, "%Y-%m-%d").strftime("%d/%m/%Y")

            st.markdown("---")
            st.markdown("#### 📊 Simulación")
            
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                if interes_pendiente > 0:
                    st.warning(f"⚠️ **Faltan S/ {interes_pendiente:,.2f}** de interés.")
                else:
                    st.success("✅ Interés cubierto.")
                if pago_capital > 0:
                    st.info(f"📉 Capital baja S/ {pago_capital:,.2f}")

            with col_res2:
                st.markdown(f"""
                <div style="background-color:#EBF5FB; padding:15px; border-radius:10px; border:1px solid #AED6F1; text-align: center;">
                    <h4 style="margin:0; color:#1B4F72;">Nueva Deuda: S/ {nuevo_capital:,.2f}</h4>
                    <hr style="margin:10px 0;">
                    <p style="margin:0; font-weight:bold;">Próx. Vencimiento: {txt_fecha_nueva}</p>
                </div>
                """, unsafe_allow_html=True)
                
            st.write("")
            if 'procesando_pago' not in st.session_state:
                st.session_state.procesando_pago = False
                
            if st.button("💾 PROCESAR PAGO"):
                data['Monto_Capital'] = nuevo_capital
                data['Pago_Mensual_Interes'] = nueva_cuota
                data['Fecha_Proximo_Pago'] = nueva_fecha_pago
                
                if nuevo_capital <= 0:
                    data['Estado'] = "Pagado"
                    data['Monto_Capital'] = 0
                    msg_log = "Deuda Cancelada"
                else:
                    msg_log = f"Pago registrado. Vence: {nueva_fecha_pago}"
                
                if guardar_datos(datos, sha, f"Actualizacion {data['Cliente']} - {msg_log}"):
                    registrar_auditoria("COBRO", f"Pago Recibido: Interés S/ {pago_interes}, Capital S/ {pago_capital}", cliente=data['Cliente'])
                    st.success("✅ Cartera actualizada correctamente.")
                    time.sleep(2)
                    st.session_state.procesando_pago = False # Liberar
                    st.rerun()

    # 3. DASHBOARD GERENCIAL
    elif menu == "📊 Dashboard General":
        st.markdown("""<div class="header-box">
                <h1>📊 RESUMEN EJECUTIVO</h1>
                <p style="color:#D4AF37;">Visión general del capital activo y estado de cobranzas.</p>
               </div>""", unsafe_allow_html=True)
        datos, _ = cargar_datos()
        
        if datos:
            df = pd.DataFrame(datos)
            df = df[df['Estado'] == 'Activo']
            hoy = datetime.now().date()
            
            c1, c2 = st.columns([2, 1])
            
            with c1:
                total = df['Monto_Capital'].sum()
                ganancia = df['Pago_Mensual_Interes'].sum()
                
                k1, k2, k3 = st.columns(3)
                k1.markdown(f'<div class="metric-card"><div class="metric-title">Capital Activo</div><div class="metric-value">S/ {total:,.2f}</div></div>', unsafe_allow_html=True)
                k2.markdown(f'<div class="metric-card" style="border-left-color:#27AE60"><div class="metric-title">Flujo Mensual</div><div class="metric-value" style="color:#27AE60">S/ {ganancia:,.2f}</div></div>', unsafe_allow_html=True)
                k3.markdown(f'<div class="metric-card" style="border-left-color:#8E44AD"><div class="metric-title">Clientes</div><div class="metric-value">{len(df)}</div></div>', unsafe_allow_html=True)
            
            with c2:
                st.markdown("##### 📅 Estado de Cobranza")
                alertas = []
                for _, r in df.iterrows():
                    venc = datetime.strptime(r['Fecha_Proximo_Pago'], "%Y-%m-%d").date()
                    dias = (venc - hoy).days
                    
                    if dias < 0:
                        alertas.append(f"<div class='alert-box alert-danger'>🚨 {r['Cliente']} (Hace {abs(dias)} días)</div>")
                    elif dias == 0:
                        alertas.append(f"<div class='alert-box alert-warning'>⚠️ {r['Cliente']} paga HOY</div>")
                    elif dias <= 3:
                        alertas.append(f"<div class='alert-box alert-success'>🕒 {r['Cliente']} en {dias} días</div>")
                
                if alertas:
                    for a in alertas: st.markdown(a, unsafe_allow_html=True)
                else: st.caption("Todo al día.")

            st.markdown("---")
            st.markdown("### 🔔 ACCIONES DE COBRO PRIORITARIAS")
            
            avisos_hoy = []
            avisos_mora = []
            
            for _, r in df.iterrows():
                venc_dt = datetime.strptime(r['Fecha_Proximo_Pago'], "%Y-%m-%d").date()
                if venc_dt == hoy:
                    avisos_hoy.append(f"💰 **COBRAR A {r['Cliente'].upper()}**: S/ {r['Pago_Mensual_Interes']:,.2f} (Vence Hoy)")
                elif venc_dt < hoy:
                    dias_atraso = (hoy - venc_dt).days
                    avisos_mora.append(f"🚨 **URGENTE: COBRAR MORA A {r['Cliente'].upper()}** | S/ {r['Pago_Mensual_Interes']:,.2f} | ({dias_atraso} días de atraso)")

            if not avisos_hoy and not avisos_mora:
                st.success("✅ Excelente: No hay cobros pendientes para el día de hoy.")
            else:
                col_avisos1, col_avisos2 = st.columns(2)
                with col_avisos1:
                    for a in avisos_hoy: st.warning(a)
                with col_avisos2:
                    for a in avisos_mora: st.error(a)

            st.markdown("---")
            st.markdown("### 📲 Centro de Notificaciones Premium")
            notif_1, notif_2, notif_3 = st.columns(3)
            
            vencidos_list, hoy_list, proximos_list = [], [], []
            for _, r in df.iterrows():
                venc_f = datetime.strptime(r['Fecha_Proximo_Pago'], "%Y-%m-%d").date()
                d_diff = (venc_f - hoy).days
                info_cli = {"nombre": r['Cliente'], "tel": r['Telefono'], "monto": r['Pago_Mensual_Interes'], "fecha": venc_f.strftime("%d/%m/%Y")}
                
                if d_diff < 0: vencidos_list.append(info_cli)
                elif d_diff == 0: hoy_list.append(info_cli)
                elif 0 < d_diff <= 3: proximos_list.append(info_cli)
            
            with notif_1:
                st.markdown("⚠️ **En Mora**")
                if vencidos_list:
                    for c in vencidos_list:
                        link = generar_link_whatsapp(c['tel'], c['nombre'], c['monto'], c['fecha'], "mora")
                        st.markdown(f"""<a href="{link}" target="_blank" class="wa-button">🔔 {c['nombre']}</a>""", unsafe_allow_html=True)
                else: st.caption("Sin moras.")

            with notif_2:
                st.markdown("📅 **Vencen HOY**")
                if hoy_list:
                    for c in hoy_list:
                        link = generar_link_whatsapp(c['tel'], c['nombre'], c['monto'], c['fecha'], "hoy")
                        st.markdown(f"""<a href="{link}" target="_blank" class="wa-button">💰 {c['nombre']}</a>""", unsafe_allow_html=True)
                else: st.caption("Nada hoy.")

            with notif_3:
                st.markdown("⏳ **Próximos (3 días)**")
                if proximos_list:
                    for c in proximos_list:
                        link = generar_link_whatsapp(c['tel'], c['nombre'], c['monto'], c['fecha'], "recordatorio")
                        st.markdown(f"""<a href="{link}" target="_blank" class="wa-button">📝 {c['nombre']}</a>""", unsafe_allow_html=True)
                else: st.caption("Sin vencimientos cercanos.")

            st.markdown("---")
            st.markdown("### 📋 Cartera de Clientes")
            df['Vence'] = pd.to_datetime(df['Fecha_Proximo_Pago']).dt.strftime('%d/%m/%Y')
            tabla_view = df[["Cliente", "Telefono", "Monto_Capital", "Pago_Mensual_Interes", "Vence", "Observaciones"]]
            st.dataframe(tabla_view, use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos registrados en el sistema.")

    # 4. AUDITORÍA
    elif menu == "📜 Auditoría":
        st.markdown("""<div class="header-box"><h1>📜 BITÁCORA DE AUDITORÍA</h1></div>""", unsafe_allow_html=True)
        logs, _ = cargar_datos("audit.json")
        if logs:
            df_audit = pd.DataFrame(logs)
            # Ordenar por el más reciente arriba
            df_audit = df_audit.iloc[::-1]
            st.dataframe(df_audit, use_container_width=True, hide_index=True)
        else:
            st.info("No hay movimientos registrados en la bitácora.")

