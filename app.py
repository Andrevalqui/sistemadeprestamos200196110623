import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime, timedelta, timezone
import calendar
import urllib.parse
from supabase import create_client

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="Sistema Financiero", 
    layout="wide", 
    page_icon="🏦",
    initial_sidebar_state="expanded"
)

# --- CONEXIÓN SUPABASE ---
@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

def cargar_datos(tabla_o_archivo="prestamos"):
    """
    Esta función reemplaza a la antigua de GitHub. 
    Mantiene el nombre para no romper tus 1590 líneas.
    """
    try:
        supabase = get_supabase()
        
        # Mapeo automático: si tu código pide "audit.json" o "auditoria", va a la tabla auditoria
        nombre_tabla = "prestamos"
        if "audit" in str(tabla_o_archivo).lower():
            nombre_tabla = "auditoria"
            
        response = supabase.table(nombre_tabla).select("*").execute()
        
        # Devolvemos (datos, None) para que el código 'datos, sha = cargar_datos()'
        # no falle al intentar desempaquetar dos valores.
        return response.data, None
    except Exception as e:
        st.error(f"Error de conexión con Supabase: {e}")
        return [], None

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Playfair+Display:wght@900&display=swap');

/* --- 1. ENCABEZADOS SIEMPRE CENTRADOS --- */
h1, h2, h3, h4, h5, h6, .stMarkdown {
    text-align: center !important;
    color: #D4AF37 !important;
    font-weight: 800 !important;
}

/* --- 2. CENTRADO DE ETIQUETAS (LABELS) SIN DEFORMAR CUADROS --- */
/* Cambiamos 'flex' por 'block' para que el texto se mueva pero el cuadro no */
[data-testid="stWidgetLabel"] {
    display: block !important;
    text-align: center !important;
    width: 100% !important;
}

[data-testid="stWidgetLabel"] p {
    text-align: center !important;
    color: #D4AF37 !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    margin-bottom: 8px !important;
}

/* --- 3. CORRECCIÓN PARA EL CHECKBOX (RENOVAR VENCIMIENTO) --- */
/* Esto centra el cuadrito y el texto de renovación perfectamente */
[data-testid="stCheckbox"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    width: 100% !important;
    margin: 10px 0 !important;
}

[data-testid="stCheckbox"] label p {
    font-size: 16px !important; /* Tamaño moderado para que no se vea gigante */
    color: #D4AF37 !important;
    font-weight: 700 !important;
}

/* --- 4. ASEGURAR QUE LOS CUADROS OCUPEN TODO EL ANCHO --- */
div[data-baseweb="input"] {
    width: 100% !important;
}

div[data-baseweb="input"] input {
    text-align: left !important; /* Texto del número a la izquierda */
}

/* --- SUBMÓDULOS (TABS) CENTRADOS Y GRANDES --- */
div[data-baseweb="tab-list"] {
    display: flex !important;
    justify-content: center !important;
    gap: 50px !important;
}

button[data-baseweb="tab"] {
    font-size: 22px !important; 
    font-weight: 900 !important; 
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

/* --- 6. BOTONES CON INVERSIÓN --- */
div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(90deg, #D4AF37 0%, #B8860B 100%) !important;
    color: #FFFFFF !important; 
    border: 1px solid #996515 !important;
    border-radius: 12px !important;
    font-weight: 900 !important;
    text-transform: uppercase !important;
    transition: all 0.4s ease-in-out !important;
    width: 100% !important;
}

div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
    background: #FFFFFF !important; 
    color: #B8860B !important;    
    border: 2px solid #D4AF37 !important;
}

//* --- DISEÑO DE LOGIN EXCLUSIVO: MIDNIGHT GOLD (RENOVADO) --- */

/* 1. Fondo General de la página (Más oscuro para que la tarjeta resalte) */
[data-testid="stAppViewRoot"] {
    background: radial-gradient(circle, #2c2c2c 0%, #000000 100%) !important;
}

/* 2. La Tarjeta de Login (Midnight Card) */
.login-container {
    /* Fondo negro profundo con brillo sutil */
    background: linear-gradient(145deg, #0a0a0a, #1a1a1a) !important;
    backdrop-filter: blur(15px);
    padding: 60px;
    
    /* BORDES DORADOS TIPO TARJETA VIP */
    border: 3px solid #D4AF37 !important; 
    border-radius: 35px !important;
    
    /* SOMBRA TRIPLE PARA PROFUNDIDAD */
    box-shadow: 
        0 30px 60px rgba(0,0,0,0.8), 
        0 0 20px rgba(212, 175, 55, 0.25),
        inset 0 0 10px rgba(212, 175, 55, 0.1) !important;
    
    text-align: center;
    max-width: 480px;
    margin: auto;
    margin-bottom: 50px !important;
    border-top: 5px solid #D4AF37 !important; /* Borde superior un poco más grueso para estilo */
}

/* 3. Imagen del Logo */
.login-icon {
    width: 200px; 
    margin-bottom: 10px;
    filter: drop-shadow(0px 8px 12px rgba(0,0,0,0.5));
}

/* 4. Título Elegante (Brisa el Milagro Style) */
.login-title {
    font-family: 'Dancing Script', cursive !important; 
    color: #D4AF37 !important;
    font-size: 65px !important;
    font-weight: 700 !important;
    text-transform: none !important; 
    margin-bottom: 5px !important;
    text-shadow: 2px 2px 10px rgba(0,0,0,0.9) !important;
}

.login-subtitle {
    color: #FFFFFF !important; /* Blanco para que se lea sobre negro */
    font-size: 13px !important;
    font-weight: 600 !important;
    margin-bottom: 30px;
    letter-spacing: 3px !important;
    text-transform: uppercase;
    opacity: 0.8;
}

/* 5. Etiquetas de Usuario y Contraseña (Grandes y Doradas) */
label p {
    color: #D4AF37 !important;
    font-weight: 800 !important;
    font-size: 22px !important;
    text-transform: uppercase;
    margin-bottom: 15px !important;
    margin-top: 25px !important;
    letter-spacing: 2px;
}

/* 6. Inputs (Personalizados para fondo negro) */
div[data-baseweb="input"] {
    background-color: rgba(255, 255, 255, 0.07) !important;
    border: 1px solid rgba(212, 175, 55, 0.4) !important;
    border-radius: 15px !important;
    color: white !important;
}

/* 7. CENTRADO Y ESTILO DEL BOTÓN (ACABADO ORO) */
div[data-testid="stFormSubmitButton"] {
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
    margin-top: 40px !important;
}

div[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(90deg, #D4AF37 0%, #B8860B 100%) !important;
    color: #000000 !important; /* Texto negro para contraste pro */
    border: 1px solid #C5A059 !important;
    padding: 18px 0px !important;
    border-radius: 15px !important;
    font-size: 22px !important; 
    font-weight: 900 !important;
    width: 85% !important;
    text-transform: uppercase;
    box-shadow: 0 10px 25px rgba(212, 175, 55, 0.3) !important;
    transition: all 0.4s ease-in-out !important;
}

div[data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-4px) scale(1.02) !important;
    background: #FFFFFF !important; 
    color: #B8860B !important;    
    border: 2px solid #D4AF37 !important;
    box-shadow: 0 15px 35px rgba(212, 175, 55, 0.5) !important;
}

/* 8. Estilo para el Pie de Página (Azul Brillante) */
.footer-login {
    color: #1A3ACD !important;
    font-size: 18px !important;
    font-weight: 900 !important;
    text-align: center !important;
    margin-top: 40px !important;
    text-shadow: 0px 0px 10px rgba(26, 58, 205, 0.2);
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
div.stButton > button, 
div[data-testid="stFormSubmitButton"] > button,
button[kind="secondaryFormSubmit"],
button[kind="primaryFormSubmit"] {
    background: linear-gradient(90deg, #D4AF37 0%, #B8860B 100%) !important;
    color: #FFFFFF !important; 
    border: 1px solid #996515 !important;
    border-radius: 12px !important; 
    font-weight: 900 !important; 
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    padding: 12px 24px !important;
    transition: all 0.4s ease-in-out !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
    width: 100% !important; 
    display: block !important;
}

/* --- EFECTO HOVER PARA TODOS LOS BOTONES --- */
div.stButton > button:hover, 
div[data-testid="stFormSubmitButton"] > button:hover,
button[kind="secondaryFormSubmit"]:hover,
button[kind="primaryFormSubmit"]:hover {
    background: #FFFFFF !important; 
    color: #B8860B !important;    
    border: 2px solid #D4AF37 !important; 
    transform: scale(1.02) !important;
    box-shadow: 0 8px 25px rgba(212, 175, 55, 0.4) !important;
}

/* --- CORRECCIÓN ADICIONAL PARA EL ICONO DEL DISKETTE --- */
div.stButton > button p, 
div[data-testid="stFormSubmitButton"] > button p {
    color: inherit !important; 
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

/* --- TABLAS DE DATOS ESTILO MINIMALISTA --- */
[data-testid="stDataFrame"] {
    background-color: transparent !important; 
    border: 1px solid rgba(212, 175, 55, 0.3) !important; /* Borde muy sutil */
    box-shadow: none !important;
    padding: 0px !important;
}

/* Encabezados de tabla */
div[data-testid="stDataFrame"] div[role="columnheader"] {
    background-color: #1a1a1a !important;
    color: #D4AF37 !important;
    font-weight: 700 !important;
    border-bottom: 1px solid #D4AF37 !important;
}

/* Celdas normales */
div[data-testid="stDataFrame"] div[role="gridcell"] {
    color: #E0E0E0 !important;
    background-color: transparent !important;
    font-size: 14px !important;
}

/* --- ALERTAS --- */
.alert-box {
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 10px;
    font-weight: 500;
    display: flex;
    align-items: center;
    justify-content: center; 
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

/* --- ACTUALIZACIÓN SPLASH SCREEN --- */
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
    background: linear-gradient(145deg, #0A0A0A, #1C1C1C); 
    border: 1px solid rgba(212, 175, 55, 0.4);
    padding: 40px 20px;
    border-radius: 20px;
    margin-bottom: 40px;
    box-shadow: 0 15px 35px rgba(0,0,0,0.8);
    text-align: center;
    position: relative;
    overflow: hidden;
}

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
    color: #FFFFFF !important; 
    font-size: 16px !important;
    font-weight: 800 !important; 
    letter-spacing: 3px !important;
    text-transform: uppercase !important;
    margin-top: 5px !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #05080d !important; 
    border-right: 2px solid #D4AF37 !important;
}

/* Título 'NAVEGACIÓN' */
div[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    font-size: 28px !important; 
    font-weight: 900 !important; 
    color: #D4AF37 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    margin-bottom: 20px !important;
}

/* Opciones del menú */
div[data-testid="stSidebar"] div[role="radiogroup"] label div p {
    font-size: 35px !important; 
    font-weight: 1000 !important; 
    color: #FFFFFF !important; 
    padding: 10px 0px !important;
    line-height: 1.2 !important;
}

/* Color del círculo de selección */
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
    """Suma 1 mes exacto manteniendo el mismo día (ej: 13/01 -> 13/02)"""
    fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d")
    mes_nuevo = fecha_dt.month + 1
    anio_nuevo = fecha_dt.year
    
    if mes_nuevo > 12:
        mes_nuevo = 1
        anio_nuevo += 1
    
    # Obtener el último día del mes destino (por si es 31 y pasamos a un mes de 30)
    _, ult_dia_mes = calendar.monthrange(anio_nuevo, mes_nuevo)
    
    # Si el día original es 31, pero el nuevo mes tiene 30, se pone 30.
    # Pero si es 13, se mantendrá 13.
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
        supabase = get_supabase()
        # Hora Perú UTC-5
        hora_peru = datetime.now(timezone(timedelta(hours=-5))).strftime("%Y-%m-%d %H:%M:%S")
        
        nuevo_log = {
            "Fecha/Hora": hora_peru,
            "Usuario": st.session_state.get('usuario', 'Sistema').upper(),
            "Perfil": st.session_state.get('rol', '-'),
            "Operación": accion,
            "Cliente Afectado": cliente,
            "Detalle del Movimiento": detalle
        }
        supabase.table("auditoria").insert(nuevo_log).execute()
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

    # 2. INICIALIZACIÓN DE ESTADO (YA NO LEEMOS LA URL POR SEGURIDAD)
    if 'logged_in' not in st.session_state:
        # Por defecto, nadie está logueado, sin importar qué diga el link
        st.session_state.update({'logged_in': False, 'usuario': '', 'rol': ''})

    # 3. SI YA ESTÁ LOGUEADO (VERIFICACIÓN DE SEGURIDAD Y TIMEOUT)
    if st.session_state['logged_in']:
        
        # --- CONTROL DE INACTIVIDAD (5 MINUTOS) ---
        if 'last_active' not in st.session_state:
            st.session_state['last_active'] = time.time()
        
        if (time.time() - st.session_state['last_active']) > (5 * 60): 
            st.session_state.clear()
            st.query_params.clear() # Limpiamos URL por seguridad
            placeholder = st.empty()
            with placeholder.container():
                st.warning("⚠️ SESIÓN EXPIRADA: Por seguridad, ingrese nuevamente.")
                time.sleep(3)
            placeholder.empty()
            st.rerun()
            return False
        else:
            st.session_state['last_active'] = time.time() 
        # ----------------------------------------------------------

        if not st.session_state.get('splash_visto'):
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
    st.write("") 
    st.write("")
    c1, c2, c3 = st.columns([1, 1.8, 1])
    with c2:
        st.markdown(f"""
            <div class="login-container">
                <img src="https://cdn-icons-png.flaticon.com/512/2489/2489756.png" class="login-icon">
                <div class="login-title">Sistema de Préstamos</div>
                <div class="login-subtitle">GESTIÓN DE ACTIVOS & CRÉDITOS</div>
            </div>
        """, unsafe_allow_html=True)
        
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
                    'rol': 'Admin' if usuario in st.secrets["config"]["admins"] else 'Visor',
                    'last_active': time.time()
                })
                # IMPORTANTE: Ya NO escribimos en la URL y limpiamos cualquier rastro
                st.query_params.clear() 
                
                registrar_auditoria("INICIO DE SESIÓN", f"Acceso exitoso al portal")
                st.rerun()
            else:
                st.error("Credenciales no autorizadas para este nivel de acceso.")
    
    st.markdown("<div style='text-align: center;'><p class='footer-login'>ANDRE VALQUI SYSTEM v2.0 | ENCRIPTACIÓN DE GRADO BANCARIO</p></div>", unsafe_allow_html=True)
    return False

def logout():
    registrar_auditoria("CIERRE DE SESIÓN", f"El usuario {st.session_state.get('usuario')} cerró su sesión")
    # Activamos el estado de salida para que check_login lo detecte
    st.session_state['saliendo'] = True
    st.rerun()
        
# --- 5. INTERFAZ PRINCIPAL ---
if check_login():
    # --- SIDEBAR (Menú Lateral) ---
    with st.sidebar:
        st.markdown(f"<h2 style='text-align: center;'>👤 {st.session_state['usuario'].upper()}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #D4AF37;'>Perfil: {st.session_state['rol']}</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        opciones = ["📊 Dashboard General", "📂 Historial de Créditos"]
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
                st.session_state.guardando_prestamo = True 
                with st.status("Registrando en base de datos segura (Supabase)...", expanded=True) as status:
                    nuevo = {
                        "Cliente": cliente, "DNI": dni, "Telefono": telefono,
                        "Fecha_Prestamo": str(fecha_inicio),
                        "Fecha_Proximo_Pago": prox_pago,
                        "Monto_Capital": monto, "Tasa_Interes": tasa,
                        "Pago_Mensual_Interes": interes, "Estado": "Activo",
                        "Observaciones": obs
                    }
                    
                    # GUARDADO DIRECTO EN SUPABASE
                    try:
                        get_supabase().table("prestamos").insert(nuevo).execute()
                        registrar_auditoria("CREACIÓN CRÉDITO", f"Préstamo de S/ {monto}", cliente=cliente)
                        status.update(label="✅ ¡Operación Guardada en Nube!", state="complete", expanded=False)
                        st.balloons()
                        time.sleep(2)
                        st.session_state.guardando_prestamo = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error DB: {e}")
                        st.session_state.guardando_prestamo = False
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
            col_sel1, col_sel2, col_sel3 = st.columns([1, 2, 1]) # 2 es el centro
        
            # --- TODA TU LÓGICA AHORA ESTÁ DENTRO DE ESTE 'IF' PARA EVITAR EL ERROR ---
            with col_sel2:
                seleccion = st.selectbox("BUSCAR CLIENTE", list(mapa.keys()))
                
                idx = mapa[seleccion]
                data = datos[idx]
                
                fecha_venc_dt = datetime.strptime(str(data['Fecha_Proximo_Pago']), "%Y-%m-%d").date()
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

               # Inyectamos CSS específico para centrar métricas y ARREGLAR el Checkbox/Inputs
                st.markdown(f"""
                    <style>
                    /* 1. Centrado de métricas (KPIs) */
                    [data-testid="stMetric"] {{
                        display: flex !important;
                        flex-direction: column !important;
                        align-items: center !important;
                        justify-content: center !important;
                        text-align: center !important;
                    }}
                    
                    [data-testid="stMetricLabel"], 
                    [data-testid="stMetricValue"], 
                    [data-testid="stMetricDelta"] {{
                        display: flex !important;
                        justify-content: center !important;
                        width: 100% !important;
                    }}

                    /* 2. FIX DEFINITIVO PARA EL CHECKBOX (RENOVAR VENCIMIENTO) */
                    [data-testid="stCheckbox"] {{
                        display: flex !important;
                        justify-content: center !important;
                        align-items: center !important;
                        gap: 8px !important;
                        width: 100% !important;
                        margin: 20px 0 !important;
                    }}

                    [data-testid="stCheckbox"] label p {{
                        font-size: 15px !important; 
                        color: #D4AF37 !important;
                        font-weight: 700 !important;
                        margin: 0 !important;
                        text-transform: uppercase;
                    }}

                    /* 3. FIX PARA INPUTS DE DINERO */
                    [data-testid="stNumberInput"] label {{
                        display: block !important;
                        text-align: center !important;
                        width: 100% !important;
                    }}

                    /* 4. Color dinámico para la fecha de vencimiento (Métrica 3) */
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
                    
                    c_info1.metric("Deuda Capital", f"S/ {data['Monto_Capital']:,.2f}")
                    c_info2.metric("Cuota Interés", f"S/ {data['Pago_Mensual_Interes']:,.2f}")
                    
                    c_info3.metric(
                        label="Vencimiento", 
                        value=fecha_venc_dt.strftime("%d/%m/%Y"), 
                        delta=txt_venc, 
                        delta_color=flecha_dir
                    )

                st.write("")
                st.markdown("---")

                col_izq, col_der = st.columns([1.3, 1], gap="large")

                with col_izq:
                    st.markdown("### 💰 Ingreso de Dinero")
                    st.caption("Ingresa los montos exactos que recibiste.")

                    pago_interes = st.number_input("1. ¿Cuánto pagó de INTERÉS?", 
                                                   min_value=0.0, value=float(data['Pago_Mensual_Interes']), step=10.0)
                    
                    pago_capital = st.number_input("2. ¿Cuánto pagó de CAPITAL?", 
                                                   min_value=0.0, value=0.0, step=50.0)

                    st.write("")
                    sugerir_renovar = (pago_interes >= (data['Pago_Mensual_Interes'] - 5))
                    renovar = st.checkbox("📅 **¿Renovar vencimiento al próximo mes?**", value=sugerir_renovar)

                    interes_pendiente = data['Pago_Mensual_Interes'] - pago_interes
                    nuevo_capital = data['Monto_Capital'] - pago_capital + interes_pendiente
                    nueva_cuota = nuevo_capital * (data['Tasa_Interes'] / 100)
                    
                    nueva_fecha_pago = data['Fecha_Proximo_Pago']
                    txt_fecha_nueva = "Se mantiene igual"
                    if renovar:
                        nueva_fecha_pago = sumar_un_mes(str(data['Fecha_Proximo_Pago']))
                        txt_fecha_nueva = datetime.strptime(nueva_fecha_pago, "%Y-%m-%d").strftime("%d/%m/%Y")
                    
                    nota_cierre = ""
                    if nuevo_capital <= 0:
                        st.write("")
                        nota_cierre = st.text_area("📝 **Notas Finales de Cierre:**", 
                                                 placeholder="Ej: Cliente canceló todo por adelantado. Muy puntual.",
                                                 help="Estas notas se verán en el Historial de Créditos.")

                    st.write("")
                    st.write("")
                    boton_guardar = st.button("💾 PROCESAR PAGO", use_container_width=True)

                with col_der:
                    st.markdown("### 📊 Simulación")
                    
                    if interes_pendiente > 0:
                        st.warning(f"⚠️ **Faltan S/ {interes_pendiente:,.2f}** de interés.")
                    else:
                        st.success("✅ Interés cubierto.")
                    
                    if pago_capital > 0:
                        st.info(f"📉 Capital baja S/ {pago_capital:,.2f}")

                    st.write("")

                    if nuevo_capital <= 0:
                        st.markdown(f"""
                        <div style="background-color:#D4EFDF; padding:20px; border-radius:10px; border:2px solid #27AE60; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <h3 style="margin:0; color:#186A3B;">¡DEUDA CANCELADA!</h3>
                            <p style="margin:5px 0; font-weight:bold; font-size:16px;">El capital llega S/ 0.00</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background-color:#EBF5FB; padding:20px; border-radius:10px; border:2px solid #AED6F1; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <p style="margin:0; color:#1B4F72; font-size:14px; text-transform: uppercase;">Nueva Deuda Capital</p>
                            <h2 style="margin:5px 0; color:#2874A6;">S/ {nuevo_capital:,.2f}</h2>
                            <hr style="margin:15px 0; border-color: rgba(0,0,0,0.1);">
                            <p style="margin:0; font-weight:bold; color:#1B4F72;">Próx. Vencimiento:</p>
                            <p style="margin:0; font-size:18px;">{txt_fecha_nueva}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                if boton_guardar:
                    upd_data = {}
                    if nuevo_capital <= 0:
                        upd_data = {
                            "Estado": "Pagado",
                            "Fecha_Finalizacion": datetime.now().strftime("%Y-%m-%d"),
                            "Observaciones": nota_cierre if nota_cierre else data['Observaciones']
                        }
                        msg_log = "Deuda Totalmente Cancelada"
                    else:
                        upd_data = {
                            "Monto_Capital": nuevo_capital,
                            "Pago_Mensual_Interes": nueva_cuota,
                            "Fecha_Proximo_Pago": nueva_fecha_pago
                        }
                        msg_log = f"Pago registrado. Vence: {nueva_fecha_pago}"
                    
                    try:
                        get_supabase().table("prestamos").update(upd_data).eq("id", data['id']).execute()
                        registrar_auditoria("COBRO", f"Pago Recibido: Interés S/ {pago_interes}, Capital S/ {pago_capital}", cliente=data['Cliente'])
                        st.success("✅ Cartera actualizada correctamente.")
                        time.sleep(2)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al actualizar: {e}")
        else:
            # ESTO SE MUESTRA SI NO HAY CLIENTES ACTIVOS
            st.info("💡 No hay préstamos activos para registrar pagos en este momento.")

    # 3. DASHBOARD GERENCIAL
    elif menu == "📊 Dashboard General":
        st.markdown("""<div class="header-box">
                <div class="luxury-title">📊 Resumen Estratégico</div>
                <div class="luxury-subtitle">Inteligencia de Datos, Control de Activos y Gestión de Cobranza.</div>
               </div>""", unsafe_allow_html=True)
        
        datos, sha = cargar_datos()
        logs_audit, _ = cargar_datos("auditoria")
        
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

            # --- SUBMÓDULOS DEL DASHBOARD (4 TABS) ---
            tab1, tab2, tab3, tab4 = st.tabs([
                "🔔 ACCIONES DE COBRO PRIORITARIAS", 
                "📲 CENTRO DE NOTIFICACIONES", 
                "📋 CARTERA DE CLIENTES",
                "🤝 INTERÉS MULTI-SOCIO"
            ])

            # --- TAB 1 (INTACTO) ---
            with tab1:
                st.markdown("### 🔔 ALERTAS DE COBRANZA")
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

            # --- TAB 2 (INTACTO) ---
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

            # --- TAB 3 (INTACTO) ---
            with tab3:
                st.markdown("### 📋 CARTERA DE CLIENTES ACTIVA")
                df['Vence'] = pd.to_datetime(df['Fecha_Proximo_Pago']).dt.strftime('%d/%m/%Y')
                df['% Interés'] = df['Tasa_Interes'].apply(lambda x: f"{x:.1f}%")
                st.dataframe(df[["Cliente", "Telefono", "Monto_Capital", "% Interés", "Pago_Mensual_Interes", "Vence", "Observaciones"]], use_container_width=True, hide_index=True)

            # --- TAB 4: LÓGICA MULTI-SOCIOS ESCALABLE ---
            with tab4:
                st.markdown("### 🤝 GESTIÓN MULTI-SOCIO")
                
                # 1. DEFINIR QUIÉNES SON LOS SOCIOS ACTIVOS
                # Intentamos sacar la lista de tus credenciales o usamos una lista base
                try:
                    usuarios_sistema = list(st.secrets["credenciales"].keys())
                    # Convertimos a formato Título (ej: brunotapia -> Bruno Tapia)
                    # Aquí puedes mapear nombres específicos si quieres
                    mapa_nombres = {
                        "brunotapia": "Bruno Tapia",
                        "pierajuarez": "Piera Juarez"
                    }
                    lista_nombres = [mapa_nombres.get(u, u.capitalize()) for u in usuarios_sistema]
                except:
                    lista_nombres = ["Bruno Tapia", "Piera Juarez"]

                with st.expander("⚙️ Seleccionar Socios Activos (Click aquí)", expanded=False):
                    st.info("Seleccione todos los socios que participan en la repartición de intereses.")
                    # Por defecto seleccionamos a los 2 principales
                    defaults = [n for n in lista_nombres if "Bruno" in n or "Piera" in n]
                    if not defaults: defaults = lista_nombres[:2]
                    
                    socios_seleccionados = st.multiselect("Socios:", lista_nombres, default=defaults)
                
                if not socios_seleccionados:
                    st.warning("⚠️ Seleccione al menos un socio para ver los cálculos.")
                    st.stop()

                # 2. CÁLCULO DE TOTALES (Iteración sobre datos)
                # Estructura para acumular: {'Bruno Tapia': 0.0, 'Piera Juarez': 0.0}
                acumulado = {s: 0.0 for s in socios_seleccionados}
                tabla_resumen = []
                opciones_clientes = []

                for i, d in enumerate(datos):
                    if d.get('Estado') == 'Activo':
                        tasa_cli = float(d.get('Tasa_Interes') or 0.0)
                        
                        # --- LÓGICA DE RECUPERACIÓN DE DATOS (COMPATIBILIDAD) ---
                        # Buscamos si ya tiene un diccionario de distribución guardado
                        distribucion = d.get('Distribucion_Socios') or {}
                        
                        # Si no existe (es dato antiguo) o faltan socios nuevos, recalculamos defaults
                        # Si es dato antiguo con 'Porc_Socio1', intentamos usarlo
                        if not distribucion:
                            if 'Porc_Socio1' in d and len(socios_seleccionados) == 2:
                                # Lógica compatible con lo anterior
                                p1 = float(d.get('Porc_Socio1') or 0.0)
                                p2 = tasa_cli - p1
                                # Asignamos al primero y segundo de la lista actual
                                distribucion = {socios_seleccionados[0]: p1, socios_seleccionados[1]: p2}
                            else:
                                # Si no hay datos previos o son más de 2 socios, dividimos equitativamente
                                distribucion = {}
                                for s in socios_seleccionados:
                                    if "Bruno" in s:
                                        distribucion[s] = 10.0
                                    elif "Piera" in s:
                                        distribucion[s] = 8.0
                                    else:
                                        distribucion[s] = tasa_cli / len(socios_seleccionados)
                        
                        # Guardamos datos calculados para la tabla visual
                        fila_tabla = {"Cliente": d['Cliente'], "Tasa Total": f"{tasa_cli}%"}
                        
                        for socio in socios_seleccionados:
                            pct = float(distribucion.get(socio, 0.0))
                            ganancia = d['Monto_Capital'] * (pct / 100)
                            
                            acumulado[socio] = acumulado.get(socio, 0.0) + ganancia
                            
                            fila_tabla[f"% {socio}"] = f"{pct:.1f}%"
                            fila_tabla[f"$ {socio}"] = ganancia # Valor numérico para config
                        
                        tabla_resumen.append(fila_tabla)
                        opciones_clientes.append(f"{i} | {d['Cliente']} (Tasa: {tasa_cli}%)")

                # --- NUEVA LÓGICA COMPLEMENTARIA PARA HISTORIAL ACUMULATIVO (SIN ELIMINAR TU LÓGICA) ---
                tabla_historial_acumulada = []
                acumulado_historico = {s: 0.0 for s in socios_seleccionados}

                if logs_audit:
                    df_audit_logs = pd.DataFrame(logs_audit)
                    # Filtramos solo los registros de COBRO (Pagos realizados)
                    pagos_reales = df_audit_logs[df_audit_logs['Operación'] == 'COBRO'].copy()
                    
                    for _, log in pagos_reales.iterrows():
                        cli_log = log['Cliente Afectado']
                        det = log['Detalle del Movimiento']
                        fecha_registro = log['Fecha/Hora']
                        
                        # Extraer el monto de interés del texto del log
                        try:
                            interes_pagado = float(det.split("Interés S/ ")[1].split(",")[0])
                        except:
                            interes_pagado = 0.0

                        # Buscar la distribución de socios que tiene el cliente
                        c_data = next((item for item in datos if item['Cliente'] == cli_log), None)
                        
                        if c_data and interes_pagado > 0:
                            dist = c_data.get('Distribucion_Socios') or {}
                            t_total = float(c_data.get('Tasa_Interes', 1))
                            
                            fila_hist = {
                                "Fecha de Pago": fecha_registro,
                                "Cliente": cli_log,
                                "Monto Recibido": interes_pagado
                            }
                            
                            for s in socios_seleccionados:
                                # Proporción: (Mi % / Tasa Total) * Lo que el cliente pagó realmente
                                p_socio = float(dist.get(s, t_total / len(socios_seleccionados)))
                                gan_socio = (p_socio / t_total) * interes_pagado
                                
                                # Actualizamos el acumulado con datos reales del historial
                                acumulado_historico[s] += gan_socio
                                fila_hist[f"$ {s}"] = gan_socio
                            
                            tabla_historial_acumulada.append(fila_hist)

                # Reemplazamos el 'acumulado' de tus tarjetas por el 'acumulado_historico'
                # para que las métricas superiores también sean acumulativas.
                acumulado = acumulado_historico

                # 3. TARJETAS DE TOTALES (DINÁMICAS PARA N SOCIOS)
                st.markdown("#### 🌍 GANANCIAS TOTALES ACUMULADAS")
                
                # Creamos tantas columnas como socios haya
                cols = st.columns(len(socios_seleccionados))
                colores = ["#2980B9", "#8E44AD", "#27AE60", "#D35400", "#C0392B"] # Lista de colores para rotar

                for idx, socio in enumerate(socios_seleccionados):
                    color_actual = colores[idx % len(colores)]
                    monto_total = acumulado[socio]
                    with cols[idx]:
                        st.markdown(f"""
                        <div class="metric-card" style="border-left: 6px solid {color_actual}; margin-bottom:10px;">
                            <div class="metric-title" style="color:{color_actual}; font-size:13px;">{socio.upper()}</div>
                            <div class="metric-value" style="font-size: 20px;">S/ {monto_total:,.2f}</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("---")

                # 4. ZONA DE EDICIÓN
                if opciones_clientes:
                    c_edit, c_view = st.columns([1, 2])
                    
                    with c_edit:
                        st.markdown("#### 🛠️ Configurar Repartición")
                        seleccion = st.selectbox("Cliente a editar:", opciones_clientes)
                        
                        if seleccion:
                            idx_real = int(seleccion.split(" | ")[0])
                            item_cli = datos[idx_real]
                            tasa_max = float(item_cli['Tasa_Interes'])
                            
                            st.info(f"💰 Tasa a repartir: **{tasa_max}%**")
                            
                            # Recuperamos la distribución actual de ese cliente
                            dist_actual_cli = item_cli.get('Distribucion_Socios') or {}
                            
                            nuevos_valores = {}
                            suma_actual = 0.0
                            
                            # Generamos un INPUT por cada socio
                            for s in socios_seleccionados:
                                estandar_socio = 10.0 if "Bruno" in s else (8.0 if "Piera" in s else tasa_max / 2)
                                
                                val_def = float(dist_actual_cli.get(s, estandar_socio))
                                
                                val = st.number_input(f"% para {s}", min_value=0.0, max_value=tasa_max, value=val_def, step=0.1, key=f"input_{s}")
                                nuevos_valores[s] = val
                                suma_actual += val
                            
                            # VALIDACIÓN MATEMÁTICA
                            diff = tasa_max - suma_actual
                            
                            st.write("")
                            if abs(diff) < 0.01: # Margen de error por decimales
                                st.success("✅ ¡La distribución es exacta!")
                                
                                # PREVISUALIZACIÓN DE DINERO (TARJETAS GRANDES POR CLIENTE)
                                st.markdown("##### 👤 Resultado Financiero:")
                                for idx, s in enumerate(socios_seleccionados):
                                    g = item_cli['Monto_Capital'] * (nuevos_valores[s] / 100)
                                    color_actual = colores[idx % len(colores)]
                                                                       
                                    st.markdown(f"""
                                    <div style="border-left: 4px solid {color_actual}; background-color: #1a1a1a; padding: 10px; margin-bottom: 5px; border-radius: 5px;">
                                        <span style="color:{color_actual}; font-weight:bold;">{s}:</span> 
                                        <span style="color:white; float:right;">S/ {g:,.2f}</span>
                                    </div>
                                    """, unsafe_allow_html=True)

                                # --- NUEVA LÓGICA DE GUARDADO EN SUPABASE ---
                                if st.button("💾 GUARDAR CAMBIOS"):
                                    try:
                                        # 1. Ejecutamos la actualización directamente en Supabase usando el ID
                                        # No necesitamos 'sha' ni manejar toda la lista de 'datos'
                                        get_supabase().table("prestamos").update({
                                            "Distribucion_Socios": nuevos_valores,
                                            "Porc_Socio1": list(nuevos_valores.values())[0]
                                        }).eq("id", item_cli['id']).execute()
                                        
                                        # 2. Registramos el movimiento en la nueva tabla de auditoría SQL
                                        registrar_auditoria("REPARTICIÓN SOCIOS", f"Ajuste de porcentajes de interés", cliente=item_cli['Cliente'])
                                        
                                        st.balloons()
                                        time.sleep(1)
                                        st.rerun()
                                        
                                    except Exception as e:
                                        st.error(f"❌ Error al actualizar en Supabase: {e}")

                            else:
                                if diff > 0:
                                    st.warning(f"⚠️ Faltan asignar **{diff:.1f}%** para llegar al {tasa_max}%.")
                                else:
                                    st.error(f"⛔ Te has pasado por **{abs(diff):.1f}%**. Ajusta los valores.")
                                
                                st.button("💾 GUARDAR (Bloqueado)", disabled=True)

                    with c_view:
                        st.markdown("#### 📊 Tabla de Detalle Histórico")
                        
                        if tabla_historial_acumulada:
                            # Creamos el DataFrame desde el historial acumulado
                            df_historial = pd.DataFrame(tabla_historial_acumulada)
                            # Ordenamos para ver lo último que se pagó arriba
                            df_historial = df_historial.iloc[::-1]

                            # Configuración dinámica de columnas (Respetando tu estilo)
                            col_config = {f"$ {s}": st.column_config.NumberColumn(f"Ganancia {s.split()[0]}", format="S/ %.2f") for s in socios_seleccionados}
                            col_config["Monto Recibido"] = st.column_config.NumberColumn("Total Interés", format="S/ %.2f")
                            col_config["Fecha de Pago"] = st.column_config.TextColumn("📅 Fecha de Pago")
                            
                            st.dataframe(
                                df_historial,
                                use_container_width=True,
                                hide_index=True,
                                column_config=col_config
                            )
                        else:
                            st.info("No se han registrado cobros en el historial aún.")
                else:
                    st.info("No hay clientes activos.")
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
            # --- FILTRAR SOLO CLIENTES ACTIVOS ---
            lista_edicion = [
                f"{i} | {d['Cliente']} (Capital: S/ {d['Monto_Capital']})" 
                for i, d in enumerate(datos) 
                if d.get('Estado') == 'Activo'
            ]
            
            # --- TODA LA LÓGICA DEBE IR DENTRO DE ESTE IF PARA EVITAR ERRORES ---
            if lista_edicion:
                col_sel1, col_sel2 = st.columns([2, 1])
                with col_sel1:
                    seleccion_edit = st.selectbox("Seleccione el registro activo a modificar o eliminar:", lista_edicion)
                
                # Extraer el índice original
                idx_orig = int(seleccion_edit.split(" | ")[0])
                item = datos[idx_orig]

                st.markdown("---")
                
                # TABS CENTRADOS Y GRANDES
                tab_edit, tab_del = st.tabs(["✏️ Editar Datos", "🗑️ Eliminar Registro"])

                with tab_edit:
                    with st.form(f"form_edit_{idx_orig}"):
                        st.markdown("### Modificar Información")
                        c_ed1, c_ed2 = st.columns(2)
                        
                        nuevo_nombre = c_ed1.text_input("Nombre del Cliente", value=item['Cliente'])
                        nuevo_dni = c_ed2.text_input("DNI / CE", value=item.get('DNI', ''))
                        nuevo_cap = c_ed1.number_input("Deuda Capital Actual (S/)", value=float(item['Monto_Capital']), step=50.0)
                        
                        # Convertir a string para asegurar compatibilidad con date_input
                        fecha_val = str(item['Fecha_Proximo_Pago'])
                        nueva_fecha_venc = c_ed2.date_input("Próximo Vencimiento", value=datetime.strptime(fecha_val, "%Y-%m-%d"))
                        
                        nueva_tasa = c_ed1.number_input("Tasa de Interés (%)", value=float(item['Tasa_Interes']))
                        nuevo_estado = c_ed2.selectbox("Estado del Crédito", ["Activo", "Pagado"], index=0 if item['Estado'] == "Activo" else 1)
                        nueva_obs = st.text_area("Observaciones del Cliente", value=item.get('Observaciones', ''))

                        st.write("")
                        btn_save_edit = st.form_submit_button("💾 GUARDAR CAMBIOS")

                    if btn_save_edit:
                        nuevo_interes = nuevo_cap * (nueva_tasa / 100)
                        upd = {
                            "Cliente": nuevo_nombre,
                            "DNI": nuevo_dni,
                            "Monto_Capital": nuevo_cap,
                            "Fecha_Proximo_Pago": str(nueva_fecha_venc),
                            "Tasa_Interes": nueva_tasa,
                            "Pago_Mensual_Interes": nuevo_interes,
                            "Estado": nuevo_estado,
                            "Observaciones": nueva_obs 
                        }
                        try:
                            get_supabase().table("prestamos").update(upd).eq("id", item['id']).execute()
                            registrar_auditoria("EDICIÓN MANUAL", f"Ajuste de datos", cliente=nuevo_nombre)
                            st.success("✅ Cambios aplicados correctamente.")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al actualizar: {e}")

                with tab_del:
                    st.warning(f"⚠️ **ATENCIÓN:** Está a punto de eliminar permanentemente el registro de **{item['Cliente']}**.")
                    st.write("Esta acción no se puede deshacer y se usa principalmente para corregir duplicados.")
                    
                    confirmar_borrado = st.text_input(f"Para confirmar, escriba el nombre del cliente ({item['Cliente']}):", key="del_confirm_box")
                    
                    if st.button("🗑️ ELIMINAR REGISTRO DEFINITIVAMENTE"):
                        if confirmar_borrado == item['Cliente']:
                            try:
                                get_supabase().table("prestamos").delete().eq("id", item['id']).execute()
                                registrar_auditoria(
                                    "ELIMINACIÓN DEFINITIVA", 
                                    f"BORRADO DE REGISTRO: Se eliminó préstamo de S/ {item['Monto_Capital']:,.2f}.", 
                                    cliente=item['Cliente']
                                )
                                st.success(f"🗑️ Registro de {item['Cliente']} eliminado correctamente.")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al eliminar: {e}")
                        else:
                            st.error("❌ El nombre no coincide.")
            else:
                st.info("💡 No hay préstamos activos para administrar en este momento.")
        else:
            st.info("📭 El sistema no contiene datos registrados en Supabase.")

    # 5. HISTORIAL DE CRÉDITOS (Módulo Informativo con Búsqueda Inteligente y Montos)
    elif menu == "📂 Historial de Créditos":
        st.markdown("""<div class="header-box">
                        <div class="luxury-title">📂 Historial de Créditos</div>
                        <div class="luxury-subtitle">Registro de Préstamos Finalizados y Capital Recuperado</div>
                       </div>""", unsafe_allow_html=True)
        
        datos, _ = cargar_datos("prestamos")
        # Filtramos solo los préstamos pagados
        historial = [d for d in datos if d.get('Estado') == 'Pagado']
        
        if historial:
            df_hist = pd.DataFrame(historial)
            
            # --- 1. BUSCADOR INTELIGENTE HISTÓRICO ---
            st.markdown("### 🔍 Buscador Inteligente de Historial")
            busqueda_h = st.text_input("", placeholder="🔍 Escriba el nombre del cliente, fecha, monto o nota para filtrar...", label_visibility="collapsed")
            
            if busqueda_h:
                mask = df_hist.apply(lambda row: row.astype(str).str.contains(busqueda_h, case=False).any(), axis=1)
                df_hist = df_hist[mask]
                st.caption(f"✨ Se encontraron {len(df_hist)} registros que coinciden con la búsqueda.")

            st.write("")

            # --- 2. MÉTRICAS DE ÉXITO DINÁMICAS ---
            h1, h2, h3 = st.columns(3)
            # Ahora el Capital Recuperado sumará los montos reales ya que no se ponen en 0
            cap_recuperado = df_hist['Monto_Capital'].sum()
            # Calculamos el total de intereses ganados sumando la columna correspondiente
            interes_ganado = df_hist['Pago_Mensual_Interes'].sum()
            
            h1.metric("CRÉDITOS CERRADOS", f"{len(df_hist)}")
            h2.metric("CAPITAL RECUPERADO", f"S/ {cap_recuperado:,.2f}")
            h3.metric("TOTAL INTERESES GANADOS", f"S/ {interes_ganado:,.2f}")

            st.write("")
            
            # --- 3. PREPARACIÓN DE DATOS PARA LA TABLA ---
            df_hist_view = df_hist.copy()
            # Formatear fechas
            df_hist_view['Inicio'] = pd.to_datetime(df_hist_view['Fecha_Prestamo']).dt.strftime('%d/%m/%Y')
            df_hist_view['Cierre'] = pd.to_datetime(df_hist_view.get('Fecha_Finalizacion', df_hist_view['Fecha_Proximo_Pago'])).dt.strftime('%d/%m/%Y')
            
            # --- SELECCIÓN DE COLUMNAS ACTUALIZADA (Agregamos Capital e Interés) ---
            cols_to_show = ["Cliente", "Monto_Capital", "Pago_Mensual_Interes", "Inicio", "Cierre", "Observaciones"]
            
            st.markdown("### 📜 Detalle de Operaciones Finalizadas")
            st.dataframe(
                df_hist_view[cols_to_show],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Cliente": st.column_config.TextColumn("👤 Cliente", width="medium"),
                    "Monto_Capital": st.column_config.NumberColumn("💰 Monto Prestado", format="S/ %.2f"),
                    "Pago_Mensual_Interes": st.column_config.NumberColumn("📈 Interés Mensual", format="S/ %.2f"),
                    "Inicio": st.column_config.TextColumn("📅 Fecha Inicio"),
                    "Cierre": st.column_config.TextColumn("✅ Fecha Cancelación"),
                    "Observaciones": st.column_config.TextColumn("📝 Notas Finales", width="large")
                }
            )
            
            # --- 4. CSS PARA NEGRITAS EN LAS CELDAS ---
            st.markdown("""
                <style>
                div[data-testid="stDataFrame"] div[role="gridcell"] {
                    font-weight: 800 !important;
                    color: #1C1C1C !important;
                    font-size: 14px !important;
                }
                div[data-testid="stDataFrame"] {
                    border: 3px solid #D4AF37 !important;
                    border-radius: 15px !important;
                }
                </style>
            """, unsafe_allow_html=True)
            
            st.info("💡 Este módulo registra los créditos que han completado su ciclo de pago satisfactoriamente con sus montos originales.")
        else:
            st.info("Aún no hay préstamos marcados como 'Pagado' en el sistema.")

    # 6. AUDITORÍA
    elif menu == "📜 Auditoría":
        st.markdown("""<div class="header-box">
                        <div class="luxury-title">📜 Auditoría del Sistema</div>
                        <div class="luxury-subtitle">Registro histórico de movimientos y accesos con filtrado inteligente</div>
                       </div>""", unsafe_allow_html=True)
        
        logs, _ = cargar_datos("auditoria")
        
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
                    display: flex !important;
                    text-align: center !important;
                    justify-content: center !important;
                    align-items: center !important;
                    color: #1C1C1C !important;
                }
                </style>
            """, unsafe_allow_html=True)
        else:
            st.info("No hay movimientos registrados en la plataforma.")










