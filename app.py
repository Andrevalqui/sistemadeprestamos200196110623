import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime, timedelta, timezone
import calendar
from github import Github
import urllib.parse

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
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Playfair+Display:wght@700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        background-color: #FFFFFF; /* FONDO OSCURO MIDNIGHT */
    }

    /* Forzar fondo oscuro en la base de Streamlit */
    .stApp {
        background: #FFFFFF !important;
    }
    
    /* --- CENTRADO GLOBAL FORZADO --- */
    h1, h2, h3, h4, h5, h6, .stMarkdown, p, label {
        text-align: center !important;
        color: #D4AF37 !important; 
        font-weight: 800 !important;
    }

    /* --- SUBMÓDULOS (TABS) CENTRADOS Y GRANDES --- */
    div[data-baseweb="tab-list"] {
        display: flex !important;
        justify-content: center !important;
        gap: 50px !important;
    }

    button[data-baseweb="tab"] {
        font-size: 22px !important; /* LETRAS GRANDES */
        font-weight: 900 !important; /* NEGRITA */
        color: #D4AF37 !important;
        transition: 0.3s !important;
    }

    button[data-baseweb="tab"]:hover {
        color: #B8860B !important;
        transform: translateY(-2px);
    }
  
    /* --- MÉTRICAS DORADAS CENTRADAS --- */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #D4AF37 0%, #B8860B 100%) !important;
        border: 2px solid #996515 !important;
        border-radius: 15px !important;
        padding: 15px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
    }

    /* Centrar Título */
    [data-testid="stMetricLabel"] {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    [data-testid="stMetricLabel"] div p {
        color: #1C1C1C !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        text-align: center !important;
    }

    /* Centrar Valor */
    [data-testid="stMetricValue"] {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    [data-testid="stMetricValue"] div {
        color: #1C1C1C !important;
        font-weight: 700 !important;
        text-align: center !important;
    }

    /* Centrar Flecha y Delta */
    [data-testid="stMetricDelta"] {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    [data-testid="stMetricDelta"] div {
        font-weight: 700 !important;
    }
    
    /* --- DISEÑO DE LOGIN EXCLUSIVO: MIDNIGHT GOLD --- */
    
    /* Fondo General del Login */
    [data-testid="stAppViewRoot"] {
        background: #8a8d8f !important;
    }

    .login-container {
        background: rgba(28, 28, 28, 0.6) !important;
        backdrop-filter: blur(20px); /* Efecto de cristal esmerilado */
        padding: 60px;
        border-radius: 25px;
        border: 1px solid rgba(212, 175, 55, 0.3); /* Borde dorado tenue */
        box-shadow: 0 25px 50px rgba(0,0,0,0.5);
        text-align: center;
        max-width: 450px;
        margin: auto;
    }

    /* Título Acceso Seguro */
    .login-title {
        font-family: 'Playfair Display', serif;
        color: #D4AF37;
        font-size: 32px;
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 5px;
        text-transform: uppercase;
    }

    .login-subtitle {
        color: #D4AF37; /* CAMBIADO A DORADO */
        font-size: 14px;
        margin-bottom: 30px;
        letter-spacing: 1px;
    }

    /* Personalización de los Campos de Texto */
    div[data-baseweb="input"], div[data-baseweb="textarea"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(212, 175, 55, 0.4) !important;
        border-radius: 12px !important;
        color: white !important;
        transition: all 0.3s ease;
    }

    div[data-baseweb="input"]:focus-within {
        border: 1px solid #D4AF37 !important;
        box-shadow: 0 0 10px rgba(212, 175, 55, 0.2) !important;
    }

    label p {
        color: #D4AF37 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        text-transform: uppercase;
        margin-bottom: 8px !important;
    }

    /* El Botón de Inicio de Sesión */
    div.stButton > button {
        background: linear-gradient(135deg, #D4AF37 0%, #996515 100%) !important;
        color: #000 !important; /* Texto negro para contraste premium */
        border: none !important;
        padding: 15px 0px !important;
        border-radius: 12px !important;
        font-size: 16px !important;
        font-weight: 800 !important;
        width: 100% !important;
        margin-top: 20px !important;
        box-shadow: 0 10px 20px rgba(212, 175, 55, 0.2) !important;
        transition: all 0.4s ease !important;
    }

    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 15px 30px rgba(212, 175, 55, 0.4) !important;
        filter: brightness(1.1);
    }
    
    /* --- TARJETAS DE MÉTRICAS (KPIs) --- */
    .metric-card {
        background: #111111; /* FONDO OSCURO */
        border-radius: 12px;
        padding: 20px;
        border: 1px solid rgba(212, 175, 55, 0.3); /* BORDE DORADO */
        border-left: 6px solid #D4AF37; /* CAMBIO A DORADO */
        box-shadow: 0 4px 6px rgba(0,0,0,0.5);
        transition: transform 0.2s;
        text-align: center; /* Centrar texto interno */
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(212, 175, 55, 0.2);
    }
    .metric-title {
        color: #D4AF37; /* DORADO */
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        margin-bottom: 8px;
        text-align: center;
    }
    .metric-value {
        color: #FFFFFF; /* BLANCO PARA RESALTAR */
        font-size: 1.8rem;
        font-weight: 700;
        text-align: center;
    }
    
    /* --- ESTILO PARA TODOS LOS BOTONES DEL SISTEMA (NORMAL, FORMULARIO Y CAMBIOS) --- */
    /* Incluye: Guardar Operación, Procesar Pago y Guardar Cambios */
    div.stButton > button, 
    div[data-testid="stFormSubmitButton"] > button,
    button[kind="secondaryFormSubmit"],
    button[kind="primaryFormSubmit"] {
        background: linear-gradient(90deg, #D4AF37 0%, #B8860B 100%) !important;
        color: #FFFFFF !important; /* LETRAS BLANCAS POR DEFECTO */
        border: 1px solid #996515 !important;
        border-radius: 12px !important; /* FORMA REDONDEADA IGUAL QUE LOS OTROS */
        font-weight: 900 !important; /* NEGRITA MÁXIMA */
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        padding: 12px 24px !important;
        transition: all 0.4s ease-in-out !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
        width: 100% !important; /* QUE OCUPE TODO EL ANCHO */
        display: block !important;
    }

    /* --- EFECTO HOVER PARA TODOS LOS BOTONES (INVERSIÓN TOTAL) --- */
    div.stButton > button:hover, 
    div[data-testid="stFormSubmitButton"] > button:hover,
    button[kind="secondaryFormSubmit"]:hover,
    button[kind="primaryFormSubmit"]:hover {
        background: #FFFFFF !important; /* FONDO BLANCO AL PASAR EL MOUSE */
        color: #B8860B !important;    /* LETRAS DORADAS AL PASAR EL MOUSE */
        border: 2px solid #D4AF37 !important; /* BORDE DORADO */
        transform: scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.4) !important;
    }

    /* --- CORRECCIÓN ADICIONAL PARA EL ICONO DEL DISKETTE --- */
    /* Si el icono molesta el color del texto, esto ayuda a unificar */
    div.stButton > button p, 
    div[data-testid="stFormSubmitButton"] > button p {
        color: inherit !important; /* Obliga al texto dentro del botón a seguir las reglas anteriores */
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
        background-color: #111111 !important; /* OSCURO */
        border-radius: 10px;
        padding: 10px;
        border: 1px solid rgba(212, 175, 55, 0.2);
        box-shadow: 0 2px 10px rgba(0,0,0,0.5);
        margin: auto; 
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
    .alert-danger { background-color: #2E1513; color: #E74C3C; border: 1px solid #E74C3C; }
    .alert-warning { background-color: #2E2813; color: #F1C40F; border: 1px solid #F1C40F; }
    .alert-success { background-color: #132E1B; color: #2ECC71; border: 1px solid #2ECC71; }
    
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
    
    /* --- CSS PARA ELIMINAR FANTASMAS --- */
    .splash-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw; 
        height: 100vh; 
        background-color: #FFFFFF !important;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        z-index: 9999999 !important; 
    }
    
    .gif-container {
        width: 300px;
        height: 300px;
    }

    /* --- ENCABEZADOS DE ALTA GAMA --- */
    .header-box {
        background: linear-gradient(145deg, #0A0A0A, #1C1C1C); /* MAS OSCURO */
        border: 1px solid rgba(212, 175, 55, 0.4);
        padding: 40px 20px;
        border-radius: 20px;
        margin-bottom: 40px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.8);
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    /* Efecto de brillo sutil en el fondo del cuadro */
    .header-box::after {
        content: '';
        position: absolute;
        top: -50%; left: -50%; width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(212,175,55,0.05) 0%, transparent 70%);
    }

    .luxury-title {
        font-family: 'Playfair Display', serif !important;
        font-weight: 900 !important;
        text-transform: uppercase !important;
        letter-spacing: 5px !important;
        font-size: 38px !important;
        background: linear-gradient(to right, #BF953F, #FCF6BA, #B38728, #FBF5B7, #AA771C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px !important;
        filter: drop-shadow(0 2px 2px rgba(0,0,0,0.3));
    }

    .luxury-subtitle {
        font-family: 'Roboto', sans-serif !important;
        color: #FFFFFF !important; /* CAMBIA A BLANCO PURO */
        font-size: 16px !important;
        font-weight: 800 !important; 
        letter-spacing: 3px !important;
        text-transform: uppercase !important;
        margin-top: 5px !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #05080d !important; /* Azul casi negro */
        border-right: 2px solid #D4AF37 !important;
    }

    /* --- ESTE ES EL CÓDIGO FINAL PARA EL SIDEBAR --- */
    
    /* Título 'NAVEGACIÓN' (Grande y Dorado) */
    div[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        font-size: 24px !important; 
        font-weight: 900 !important; 
        color: #D4AF37 !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        margin-bottom: 20px !important;
    }

    /* Opciones del menú (Grandes y Blancas para resaltar) */
    div[data-testid="stSidebar"] div[role="radiogroup"] label div p {
        font-size: 19px !important; 
        font-weight: 800 !important; 
        color: #FFFFFF !important; 
        padding: 5px 0px !important;
    }

    /* Color del círculo de selección en Dorado */
    div[data-testid="stSidebar"] div[role="radiogroup"] [data-baseweb="radio"] div {
        border-color: #D4AF37 !important;
        background-color: transparent !important;
    }
    
    /* El punto interno cuando está seleccionado */
    div[data-testid="stSidebar"] div[role="radiogroup"] [aria-checked="true"] div::after {
        background-color: #D4AF37 !important;
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
        
        # --- CÁLCULO HORA PERÚ (UTC-5) ---
        hora_peru = datetime.now(timezone(timedelta(hours=-5))).strftime("%d/%m/%Y %H:%M:%S")
        
        nuevo_log = {
            "Fecha/Hora": hora_peru,
            "Usuario": st.session_state.get('usuario', 'Sistema').upper(),
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
        
def mostrar_splash_salida():
    placeholder = st.empty()
    nombre = st.session_state.get('usuario', '').upper()
    
    with placeholder.container():
        st.markdown(f"""
            <div class="splash-overlay">
                <div style="width: 300px; height: 300px;">
                    <iframe src="https://tenor.com/embed/1281825661231862493" 
                            width="100%" height="100%" frameborder="0" allowfullscreen>
                    </iframe>
                </div>
                <h2 style="color:#D4AF37; margin-top:30px; font-family:'Playfair Display', serif;">
                    HASTA LUEGO ESTIMAD@ {nombre}...
                </h2>
                <p style="color:white; text-align:center;">Cerrando sesión de forma segura</p>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(3.0)
    
    # LIMPIEZA ANTES DE SALIR
    st.query_params.clear()
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    placeholder.empty()
    st.rerun() # Al volver, ya no habrá sidebar porque no hay sesión
    
# --- 4. GESTIÓN DE SESIÓN Y GITHUB ---
def check_login():
    # 1. DETECTAR SI ESTAMOS SALIENDO
    if st.session_state.get('saliendo'):
        mostrar_splash_salida()
        return False

    # 2. PERSISTENCIA F5
    q = st.query_params
    if 'logged_in' not in st.session_state:
        if "user" in q and "rol" in q:
            st.session_state.update({
                'logged_in': True, 'usuario': q["user"], 'rol': q["rol"], 'splash_visto': True
            })
        else:
            st.session_state.update({'logged_in': False, 'usuario': '', 'rol': ''})

    # 3. SI YA ESTÁ LOGUEADO (MANEJO DE SPLASH DE ENTRADA)
    if st.session_state['logged_in']:
        if not st.session_state.get('splash_visto'):
            # --- SOLUCIÓN AL ERROR: DEFINIR VARIABLE NOMBRE ---
            nombre = st.session_state.get('usuario', '').upper()
            
            placeholder = st.empty()
            with placeholder.container():
                st.markdown(f"""
                    <div class="splash-overlay">
                        <div style="width: 300px; height: 300px;">
                            <iframe src="https://tenor.com/embed/1281825661231862493" 
                                    width="100%" height="100%" frameborder="0" allowfullscreen>
                            </iframe>
                        </div>
                        <h2 style="color:#D4AF37; margin-top:30px; font-family:'Playfair Display', serif; letter-spacing:4px; text-transform:uppercase; font-size:22px;">
                            BIENVENID@ {nombre} AL SISTEMA DE PRÉSTAMOS...
                        </h2>
                    </div>
                """, unsafe_allow_html=True)
                time.sleep(3.8)
            st.session_state['splash_visto'] = True
            placeholder.empty()
            st.rerun()
        
        return True # Entra al portal

    # --- 4. PANTALLA DE LOGIN (REDiseño Exclusivo) ---
    st.write("") # Espaciado superior
    st.write("")
    c1, c2, c3 = st.columns([1, 1.8, 1])
    with c2:
        st.markdown(f"""
            <div class="login-container">
                <div style="font-size: 50px; margin-bottom: 10px;">🔒</div>
                <div class="login-title">Acceso Seguro</div>
                <div class="login-subtitle">GESTIÓN DE ACTIVOS & CRÉDITOS</div>
            </div>
        """, unsafe_allow_html=True)
        
        # El formulario ahora vive "encima" del contenedor transparente
        with st.form("login_form"):
            usuario = st.text_input("Usuario", placeholder="Ingrese su credencial")
            password = st.text_input("Contraseña", type="password", placeholder="••••••••")
            st.write("")
            submit_button = st.form_submit_button("INICIAR SESIÓN")

        if submit_button:
            creds = st.secrets["credenciales"]
            if usuario in creds and creds[usuario] == password:
                st.session_state.update({
                    'logged_in': True, 
                    'usuario': usuario,
                    'rol': 'Admin' if usuario in st.secrets["config"]["admins"] else 'Visor'
                })
                registrar_auditoria("INICIO DE SESIÓN", f"Acceso exitoso al portal")
                st.query_params["user"] = usuario
                st.query_params["rol"] = st.session_state['rol']
                st.rerun()
            else:
                st.error("Credenciales no autorizadas para este nivel de acceso.")
    
    # Footer sutil fuera del contenedor
    st.markdown("<p style='color: #444; font-size: 11px; margin-top: 50px;'>ANDRE VALQUI SYSTEM v2.0 | ENCRIPTACIÓN DE GRADO BANCARIO</p>", unsafe_allow_html=True)
    return False

def logout():
    registrar_auditoria("CIERRE DE SESIÓN", f"El usuario {st.session_state.get('usuario')} cerró su sesión")
    # Activamos el estado de salida para que check_login lo detecte
    st.session_state['saliendo'] = True
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
        st.markdown(f"<h2 style='text-align: center;'>👤 {st.session_state['usuario'].upper()}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #D4AF37;'>Perfil: {st.session_state['rol']}</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        # --- LÓGICA DE ACCESO BRUNOTAPIA ---
        opciones = ["📊 Dashboard General", "📂 Historial de Créditos"] # Opción nueva para todos
        user_actual = st.session_state.get('usuario', '').lower()
        
        if st.session_state['rol'] == 'Admin':
            opciones = ["📝 Nuevo Préstamo", "💸 Registrar Pago", "🛠️ Administrar Cartera", "📜 Auditoría"] + opciones
        elif user_actual == "brunotapia":
            opciones = ["📜 Auditoría"] + opciones
        
        menu = st.radio("Navegación", opciones)
        
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout()

    # --- LÓGICA DE PÁGINAS ---

    # 1. REGISTRAR NUEVO PRÉSTAMO
    if menu == "📝 Nuevo Préstamo":
        st.markdown("""<div class="header-box">
                    <div class="luxury-title">📝 Solicitud de Crédito</div>
                    <div class="luxury-subtitle">Ingrese los datos del nuevo cliente para la emisión del préstamo.</div>
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
                monto = st.number_input("Monto a Prestar (S/)", min_value=0.0, step=50.0)
                fecha_inicio = st.date_input("Fecha del Préstamo", datetime.now())
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
                # 1. Bloqueamos el botón y mostramos estado de carga
                st.session_state.guardando_prestamo = True 
                
                with st.status("Registrando en base de datos segura...", expanded=True) as status:
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
                        registrar_auditoria("CREACIÓN CRÉDITO", f"Préstamo de S/ {monto}", cliente=cliente)
                        status.update(label="✅ ¡Operación Guardada con Éxito!", state="complete", expanded=False)
                        st.balloons() # Efecto visual premium
                        time.sleep(2) # Tiempo suficiente para ver el mensaje
                        
                        # 2. Liberamos y reiniciamos
                        st.session_state.guardando_prestamo = False
                        st.rerun()
                    else:
                        st.session_state.guardando_prestamo = False
                        st.error("❌ Error al conectar con el servidor.")
            else:
                st.warning("⚠️ Complete Nombre y Monto.")

    # 2. CAJA Y PAGOS
    elif menu == "💸 Registrar Pago":
        st.markdown("""<div class="header-box">
                    <div class="luxury-title">💸 Gestión de Cobranza</div>
                    <div class="luxury-subtitle">Registre los ingresos de capital e intereses de la cartera activa.</div>
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

            # --- LÓGICA DE COLORES DINÁMICOS ---
            if dias_restantes <= 0:
                color_texto = "#943126"  # Rojo Oscuro (Mora/Hoy)
                txt_venc = "Vence HOY" if dias_restantes == 0 else f"Vencido hace {abs(dias_restantes)} días"
                flecha_dir = "inverse"
            elif dias_restantes <= 5:
                color_texto = "#5D4037"  # MARRÓN CHOCOLATE (Cercano)
                txt_venc = f"En {dias_restantes} días"
                flecha_dir = "off"       
            else:
                color_texto = "#145A32"  # Verde Oscuro (Al día)
                txt_venc = f"En {dias_restantes} días"
                flecha_dir = "normal"

            # Inyectamos CSS específico para centrar y dar color a la tarjeta de vencimiento
            st.markdown(f"""
                <style>
                /* Centrado general de métricas */
                [data-testid="stMetric"] {{
                    display: flex !important;
                    flex-direction: column !important;
                    align-items: center !important;
                    justify-content: center !important;
                    text-align: center !important;
                }}
                [data-testid="stMetricLabel"] {{ display: flex !important; justify-content: center !important; width: 100% !important; }}
                [data-testid="stMetricValue"] {{ display: flex !important; justify-content: center !important; width: 100% !important; }}
                [data-testid="stMetricDelta"] {{ display: flex !important; justify-content: center !important; width: 100% !important; }}

                /* Color dinámico SOLO para la métrica de vencimiento (la tercera en la fila) */
                [data-testid="stHorizontalBlock"] > div:nth-child(3) [data-testid="stMetricValue"] div {{
                    color: {color_texto} !important;
                }}
                [data-testid="stHorizontalBlock"] > div:nth-child(3) [data-testid="stMetricDelta"] div {{
                    color: {color_texto} !important;
                }}
                [data-testid="stHorizontalBlock"] > div:nth-child(3) [data-testid="stMetricDelta"] svg {{
                    fill: {color_texto} !important;
                }}
                </style>
            """, unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown(f"### 👤 {data['Cliente']}")
                
                c_info1, c_info2, c_info3 = st.columns(3)
                
                # Las dos primeras métricas (Negro Ejecutivo)
                c_info1.metric("Deuda Capital", f"S/ {data['Monto_Capital']:,.2f}")
                c_info2.metric("Cuota Interés", f"S/ {data['Pago_Mensual_Interes']:,.2f}")
                
                # La tercera métrica con color dinámico
                c_info3.metric(
                    label="Vencimiento", 
                    value=fecha_venc_dt.strftime("%d/%m/%Y"), 
                    delta=txt_venc, 
                    delta_color=flecha_dir
                )

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
                # Si la deuda es 0, mostramos un diseño especial de cancelación
                if nuevo_capital <= 0:
                    st.markdown(f"""
                    <div style="background-color:#D4EFDF; padding:15px; border-radius:10px; border:1px solid #27AE60; text-align: center;">
                        <h4 style="margin:0; color:#186A3B;">¡DEUDA CANCELADA!</h4>
                        <p style="margin:0; font-weight:bold;">El capital llega a S/ 0.00</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background-color:#EBF5FB; padding:15px; border-radius:10px; border:1px solid #AED6F1; text-align: center;">
                        <h4 style="margin:0; color:#1B4F72;">Nueva Deuda: S/ {nuevo_capital:,.2f}</h4>
                        <hr style="margin:10px 0;">
                        <p style="margin:0; font-weight:bold;">Próx. Vencimiento: {txt_fecha_nueva}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # --- BLOQUE NUEVO: NOTAS DE CIERRE ---
            nota_cierre = ""
            if nuevo_capital <= 0:
                st.write("")
                nota_cierre = st.text_area("📝 **Notas Finales de Cierre:**", 
                                         placeholder="Ej: Cliente canceló todo por adelantado. Muy puntual.",
                                         help="Estas notas se verán en el Historial de Créditos.")
            
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
                    data['Fecha_Finalizacion'] = datetime.now().strftime("%Y-%m-%d") 
                    
                    # SI ESCRIBIÓ ALGO EN LA NOTA, LO AGREGAMOS O REEMPLAZAMOS EN OBSERVACIONES
                    if nota_cierre:
                        data['Observaciones'] = nota_cierre
                    
                    msg_log = "Deuda Totalmente Cancelada"
                else:
                    msg_log = f"Pago registrado. Vence: {nueva_fecha_pago}"
                
                # --- GUARDADO Y AUDITORÍA ---
                if guardar_datos(datos, sha, f"Actualizacion {data['Cliente']} - {msg_log}"):
                    registrar_auditoria("COBRO", f"Pago Recibido: Interés S/ {pago_interes}, Capital S/ {pago_capital}", cliente=data['Cliente'])
                    st.success("✅ Cartera actualizada correctamente.")
                    time.sleep(2)
                    st.session_state.procesando_pago = False 
                    st.rerun()

    # 3. DASHBOARD GERENCIAL
    elif menu == "📊 Dashboard General":
        st.markdown("""<div class="header-box">
                <div class="luxury-title">📊 Resumen Estratégico</div>
                <div class="luxury-subtitle">Inteligencia de Datos, Control de Activos y Gestión de Cobranza.</div>
               </div>""", unsafe_allow_html=True)
        
        datos, _ = cargar_datos()
        
        if datos:
            df = pd.DataFrame(datos)
            df = df[df['Estado'] == 'Activo']
            hoy = datetime.now().date()
            
            # --- KPIs SUPERIORES ---
            k1, k2, k3 = st.columns(3)
            total = df['Monto_Capital'].sum()
            ganancia = df['Pago_Mensual_Interes'].sum()
            k1.metric("CAPITAL ACTIVO", f"S/ {total:,.2f}")
            k2.metric("FLUJO MENSUAL", f"S/ {ganancia:,.2f}")
            k3.metric("CLIENTES ACTIVOS", f"{len(df)}")

            st.write("")

            # --- SUBMÓDULOS DEL DASHBOARD ---
            tab1, tab2, tab3 = st.tabs(["🔔 ACCIONES DE COBRO PRIORITARIAS", "📲 CENTRO DE NOTIFICACIONES", "📋 CARTERA DE CLIENTES"])

            with tab1:
                st.markdown("### 🔔 ALERTAS DE COBRANZA")
                
                # Columnas para organizar las alertas visuales
                col_alert1, col_alert2 = st.columns([1, 1])
                
                avisos_hoy = []
                avisos_mora = []
                alertas_proximas = []
                
                for _, r in df.iterrows():
                    venc_dt = datetime.strptime(r['Fecha_Proximo_Pago'], "%Y-%m-%d").date()
                    dias = (venc_dt - hoy).days
                    
                    if dias < 0:
                        avisos_mora.append(f"<div class='alert-box alert-danger'>🚨 MORA: {r['Cliente']} (Hace {abs(dias)} días)</div>")
                    elif dias == 0:
                        avisos_hoy.append(f"<div class='alert-box alert-warning'>⚠️ COBRAR HOY: {r['Cliente']} - S/ {r['Pago_Mensual_Interes']:,.2f}</div>")
                    elif dias <= 5:
                        # COLOR MARRÓN PARA < 5 DÍAS
                        alertas_proximas.append(f"<div class='alert-box' style='background-color:#EFEBE9; color:#5D4037; border:1px solid #5D4037;'>🕒 PRÓXIMO: {r['Cliente']} (En {dias} días)</div>")

                with col_alert1:
                    if avisos_mora or avisos_hoy:
                        for a in avisos_mora: st.markdown(a, unsafe_allow_html=True)
                        for a in avisos_hoy: st.markdown(a, unsafe_allow_html=True)
                    else: st.success("✅ Todo al día para hoy.")

                with col_alert2:
                    if alertas_proximas:
                        for a in alertas_proximas: st.markdown(a, unsafe_allow_html=True)
                    else: st.caption("No hay vencimientos cercanos (< 5 días).")

            with tab2:
                st.markdown("### 📲 CENTRO DE NOTIFICACIONES PREMIUM")
                n1, n2, n3 = st.columns(3)
                vencidos_list, hoy_list, proximos_list = [], [], []
                
                for _, r in df.iterrows():
                    venc_f = datetime.strptime(r['Fecha_Proximo_Pago'], "%Y-%m-%d").date()
                    d_diff = (venc_f - hoy).days
                    info = {"nombre": r['Cliente'], "tel": r['Telefono'], "monto": r['Pago_Mensual_Interes'], "fecha": venc_f.strftime("%d/%m/%Y")}
                    
                    if d_diff < 0: vencidos_list.append(info)
                    elif d_diff == 0: hoy_list.append(info)
                    elif 0 < d_diff <= 3: proximos_list.append(info)
                
                with n1:
                    st.markdown("##### ⚠️ En Mora")
                    for c in vencidos_list:
                        link = generar_link_whatsapp(c['tel'], c['nombre'], c['monto'], c['fecha'], "mora")
                        st.markdown(f'<a href="{link}" target="_blank" class="wa-button">📲 Notificar {c["nombre"]}</a>', unsafe_allow_html=True)
                with n2:
                    st.markdown("##### 📅 Vencen Hoy")
                    for c in hoy_list:
                        link = generar_link_whatsapp(c['tel'], c['nombre'], c['monto'], c['fecha'], "hoy")
                        st.markdown(f'<a href="{link}" target="_blank" class="wa-button">📲 Notificar {c["nombre"]}</a>', unsafe_allow_html=True)
                with n3:
                    st.markdown("##### ⏳ Recordatorios")
                    for c in proximos_list:
                        link = generar_link_whatsapp(c['tel'], c['nombre'], c['monto'], c['fecha'], "recordatorio")
                        st.markdown(f'<a href="{link}" target="_blank" class="wa-button">📲 Notificar {c["nombre"]}</a>', unsafe_allow_html=True)

            with tab3:
                st.markdown("### 📋 CARTERA DE CLIENTES ACTIVA")
                df['Vence'] = pd.to_datetime(df['Fecha_Proximo_Pago']).dt.strftime('%d/%m/%Y')
                st.dataframe(df[["Cliente", "Telefono", "Monto_Capital", "Pago_Mensual_Interes", "Vence", "Observaciones"]], use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos registrados.")

   # 4. ADMINISTRACIÓN Y EDICIÓN (Módulo Nuevo)
    elif menu == "🛠️ Administrar Cartera":
        st.markdown("""<div class="header-box">
                    <div class="luxury-title">🛠️ Administración de Cartera</div>
                    <div class="luxury-subtitle">Control de Registros y Ajustes de Cartera</div>
                   </div>""", unsafe_allow_html=True)
        
        datos, sha = cargar_datos()
        
        if datos:
            # --- MEJORA: FILTRAR SOLO CLIENTES ACTIVOS ---
            lista_edicion = [
                f"{i} | {d['Cliente']} (Capital: S/ {d['Monto_Capital']})" 
                for i, d in enumerate(datos) 
                if d.get('Estado') == 'Activo'
            ]
            
            # Verificar si después de filtrar hay clientes para mostrar
            if lista_edicion:
                col_sel1, col_sel2 = st.columns([2, 1])
                with col_sel1:
                    seleccion_edit = st.selectbox("Seleccione el registro activo a modificar o eliminar:", lista_edicion)
                
                # Extraer el índice original
                idx_orig = int(seleccion_edit.split(" | ")[0])
                item = datos[idx_orig]

                st.markdown("---")
                
                # CREACIÓN DE TABS CENTRADOS Y GRANDES (Según tu estilo anterior)
                tab_edit, tab_del = st.tabs(["✏️ Editar Datos", "🗑️ Eliminar Registro"])

                with tab_edit:
                    with st.form(f"form_edit_{idx_orig}"):
                        st.markdown("### Modificar Información")
                        c_ed1, c_ed2 = st.columns(2)
                        
                        nuevo_nombre = c_ed1.text_input("Nombre del Cliente", value=item['Cliente'])
                        nuevo_dni = c_ed2.text_input("DNI / CE", value=item.get('DNI', ''))
                        
                        nuevo_cap = c_ed1.number_input("Deuda Capital Actual (S/)", value=float(item['Monto_Capital']), step=50.0)
                        nueva_fecha_venc = c_ed2.date_input("Próximo Vencimiento", value=datetime.strptime(item['Fecha_Proximo_Pago'], "%Y-%m-%d"))
                        
                        nueva_tasa = c_ed1.number_input("Tasa de Interés (%)", value=float(item['Tasa_Interes']))
                        nuevo_estado = c_ed2.selectbox("Estado del Crédito", ["Activo", "Pagado"], index=0 if item['Estado'] == "Activo" else 1)
                        
                        # --- CAMPO DE OBSERVACIONES ---
                        nueva_obs = st.text_area("Observaciones del Cliente", value=item.get('Observaciones', ''))

                        st.write("")
                        btn_save_edit = st.form_submit_button("💾 GUARDAR CAMBIOS")

                    if btn_save_edit:
                        # Recalcular interés basado en el nuevo capital
                        nuevo_interes = nuevo_cap * (nueva_tasa / 100)
                        
                        # Actualizar todos los campos en la lista de datos
                        datos[idx_orig].update({
                            "Cliente": nuevo_nombre,
                            "DNI": nuevo_dni,
                            "Monto_Capital": nuevo_cap,
                            "Fecha_Proximo_Pago": str(nueva_fecha_venc),
                            "Tasa_Interes": nueva_tasa,
                            "Pago_Mensual_Interes": nuevo_interes,
                            "Estado": nuevo_estado,
                            "Observaciones": nueva_obs 
                        })
                        
                        with st.status("Actualizando registro...", expanded=False) as status:
                            if guardar_datos(datos, sha, f"Edicion manual: {nuevo_nombre}"):
                                registrar_auditoria("EDICIÓN MANUAL", f"Ajuste de datos y observaciones", cliente=nuevo_nombre)
                                status.update(label="✅ Cambios aplicados correctamente.", state="complete")
                                time.sleep(2)
                                st.rerun()

                with tab_del:
                    st.warning(f"⚠️ **ATENCIÓN:** Está a punto de eliminar permanentemente el registro de **{item['Cliente']}**.")
                    st.write("Esta acción no se puede deshacer y se usa principalmente para corregir duplicados.")
                    
                    confirmar_borrado = st.text_input(f"Para confirmar, escriba el nombre del cliente ({item['Cliente']}):")
                    
                    if st.button("🗑️ ELIMINAR REGISTRO DEFINITIVAMENTE"):
                        if confirmar_borrado == item['Cliente']:
                            cliente_eliminado = item['Cliente']
                            cap_eliminado = item['Monto_Capital']
                            datos.pop(idx_orig)
                            
                            if guardar_datos(datos, sha, f"Eliminacion de registro: {cliente_eliminado}"):
                                registrar_auditoria(
                                    "ELIMINACIÓN DEFINITIVA", 
                                    f"BORRADO DE REGISTRO: Se eliminó préstamo de S/ {cap_eliminado:,.2f}.", 
                                    cliente=cliente_eliminado
                                )
                                st.success(f"🗑️ Registro de {cliente_eliminado} eliminado correctamente.")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error("❌ El nombre no coincide.")
            else:
                st.info("💡 No hay préstamos activos para administrar. Todos están en el Historial.")
        else:
            st.info("No hay datos registrados en el sistema.")

    # 5. HISTORIAL DE CRÉDITOS (Módulo Informativo con Búsqueda Inteligente)
    elif menu == "📂 Historial de Créditos":
        st.markdown("""<div class="header-box">
                        <div class="luxury-title">📂 Historial de Créditos</div>
                        <div class="luxury-subtitle">Registro de Préstamos Finalizados y Capital Recuperado</div>
                       </div>""", unsafe_allow_html=True)
        
        datos, _ = cargar_datos()
        # Filtramos solo los préstamos pagados
        historial = [d for d in datos if d.get('Estado') == 'Pagado']
        
        if historial:
            df_hist = pd.DataFrame(historial)
            
            # --- 1. BUSCADOR INTELIGENTE HISTÓRICO ---
            st.markdown("### 🔍 Buscador Inteligente de Historial")
            busqueda_h = st.text_input("", placeholder="🔍 Escriba el nombre del cliente, fecha, monto o nota para filtrar...", label_visibility="collapsed")
            
            if busqueda_h:
                # Filtrado universal en todas las columnas
                mask = df_hist.apply(lambda row: row.astype(str).str.contains(busqueda_h, case=False).any(), axis=1)
                df_hist = df_hist[mask]
                st.caption(f"✨ Se encontraron {len(df_hist)} registros que coinciden con la búsqueda.")

            st.write("")

            # --- 2. MÉTRICAS DE ÉXITO DINÁMICAS ---
            h1, h2, h3 = st.columns(3)
            # Intentamos obtener el capital inicial si existe, sino usamos el valor del préstamo guardado
            # (Para esto, es ideal que al crear el préstamo guardes 'Capital_Inicial')
            cap_recuperado = df_hist['Monto_Capital'].sum() 
            
            h1.metric("CRÉDITOS CERRADOS", f"{len(df_hist)}")
            h2.metric("CAPITAL FINALIZADO", "100% RECUPERADO")
            h3.metric("EFECTIVIDAD", "NIVEL ORO")

            st.write("")
            
            # --- 3. PREPARACIÓN DE DATOS PARA LA TABLA ---
            df_hist_view = df_hist.copy()
            # Formatear fechas
            df_hist_view['Inicio'] = pd.to_datetime(df_hist_view['Fecha_Prestamo']).dt.strftime('%d/%m/%Y')
            df_hist_view['Cierre'] = pd.to_datetime(df_hist_view.get('Fecha_Finalizacion', df_hist_view['Fecha_Proximo_Pago'])).dt.strftime('%d/%m/%Y')
            
            # Formatear montos y tasas para que se vean elegantes
            df_hist_view['Tasa %'] = df_hist_view['Tasa_Interes'].apply(lambda x: f"{x}%")

            # Selección de columnas importantes
            cols_to_show = ["Cliente", "Inicio", "Cierre", "Tasa %", "Observaciones"]
            
            st.markdown("### 📜 Detalle de Operaciones Finalizadas")
            st.dataframe(
                df_hist_view[cols_to_show],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Cliente": st.column_config.TextColumn("👤 Cliente", width="medium"),
                    "Inicio": st.column_config.TextColumn("📅 Fecha Inicio"),
                    "Cierre": st.column_config.TextColumn("✅ Fecha Cancelación"),
                    "Tasa %": st.column_config.TextColumn("📈 Interés"),
                    "Observaciones": st.column_config.TextColumn("📝 Notas Finales", width="large")
                }
            )
            
            # --- 4. CSS PARA NEGRITAS EN LAS CELDAS ---
            st.markdown("""
                <style>
                /* Forzar negritas en las celdas de la tabla de historial */
                div[data-testid="stDataFrame"] div[role="gridcell"] {
                    font-weight: 800 !important;
                    color: #1C1C1C !important;
                    font-size: 14px !important;
                }
                /* Borde dorado para la tabla */
                div[data-testid="stDataFrame"] {
                    border: 2px solid #D4AF37 !important;
                    border-radius: 15px !important;
                }
                </style>
            """, unsafe_allow_html=True)
            
            st.info("💡 Este módulo es de solo lectura. Registra los créditos que han completado su ciclo de pago satisfactoriamente.")
        else:
            st.info("Aún no hay préstamos marcados como 'Pagado' en el sistema.")

    # 6. AUDITORÍA
    elif menu == "📜 Auditoría":
        st.markdown("""<div class="header-box">
                        <div class="luxury-title">📜 Auditoría del Sistema</div>
                        <div class="luxury-subtitle">Registro histórico de movimientos y accesos con filtrado inteligente</div>
                       </div>""", unsafe_allow_html=True)
        
        logs, _ = cargar_datos("audit.json")
        
        if logs:
            df_audit = pd.DataFrame(logs)
            # Ordenar por el más reciente arriba
            df_audit = df_audit.iloc[::-1]

            # --- BUSCADOR INTELIGENTE ---
            st.markdown("### 🔍 Buscador en Tiempo Real")
            busqueda = st.text_input("", placeholder="🔍 Filtre por Usuario, Cliente, Operación, Fecha o Detalle...", label_visibility="collapsed")
            
            # Lógica de filtrado inteligente (Busca en todas las columnas)
            if busqueda:
                # Convertimos todo a string y buscamos la coincidencia sin importar mayúsculas/minúsculas
                mask = df_audit.apply(lambda row: row.astype(str).str.contains(busqueda, case=False).any(), axis=1)
                df_audit = df_audit[mask]
                st.caption(f"✨ Se encontraron {len(df_audit)} resultados para: '{busqueda}'")

            st.write("")

            # CONFIGURACIÓN DE VISUALIZACIÓN
            st.dataframe(
                df_audit,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Fecha/Hora": st.column_config.TextColumn("📅 Fecha/Hora", width="medium"),
                    "Usuario": st.column_config.TextColumn("👤 Usuario", width="small"),
                    "Perfil": st.column_config.TextColumn("🛡️ Perfil", width="small"),
                    "Operación": st.column_config.TextColumn("⚙️ Operación", width="medium"),
                    "Cliente Afectado": st.column_config.TextColumn("👤 Cliente", width="medium"),
                    "Detalle del Movimiento": st.column_config.TextColumn("📝 Detalle del Movimiento", width="large"),
                }
            )

            # CSS Adicional para centrar y estilizar la tabla de auditoría
            st.markdown("""
                <style>
                [data-testid="stDataFrame"] { 
                    border: 2px solid #D4AF37 !important; 
                    border-radius: 15px !important;
                }
                /* Negritas para los datos de la tabla */
                div[data-testid="stDataFrame"] div[role="gridcell"] {
                    font-weight: 700 !important;
                    color: #1C1C1C !important;
                }
                </style>
            """, unsafe_allow_html=True)
        else:
            st.info("No hay movimientos registrados en la plataforma.")












