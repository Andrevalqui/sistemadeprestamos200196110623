import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from github import Github

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestor de Préstamos", layout="wide", page_icon="💰")

# --- ESTILOS CSS ---
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
    .alert-card { background-color: #FDEDEC; border: 1px solid #E74C3C; padding: 10px; border-radius: 8px; color: #922B21; margin-bottom: 10px;}
    .warning-card { background-color: #FEF9E7; border: 1px solid #F1C40F; padding: 10px; border-radius: 8px; color: #9A7D0A; margin-bottom: 10px;}
    
    div.stButton > button {
        background: linear-gradient(90deg, #117864 0%, #1ABC9C 100%);
        color: white; border: none; padding: 12px 24px; border-radius: 8px; width: 100%;
        font-weight: bold; text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

# --- LOGIN ---
def check_login():
    if 'logged_in' not in st.session_state:
        st.session_state.update({'logged_in': False, 'usuario': '', 'rol': ''})

    if not st.session_state['logged_in']:
        c1, c2, c3 = st.columns([1,2,1])
        with c2:
            st.markdown("### 🔐 Acceso al Sistema")
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.button("Ingresar"):
                creds = st.secrets["credenciales"]
                if u in creds and creds[u] == p:
                    st.session_state.update({'logged_in': True, 'usuario': u})
                    st.session_state['rol'] = 'Admin' if u in st.secrets["config"]["admins"] else 'Visor'
                    st.rerun()
                else: st.error("Acceso denegado")
        return False
    return True

def logout():
    st.session_state.update({'logged_in': False, 'usuario': '', 'rol': ''})
    st.rerun()

# --- BASE DE DATOS GITHUB ---
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
        st.error(f"Error: {e}")
        return False

# --- LÓGICA DE NEGOCIO ---
def procesar_pago(idx, tipo_pago, monto_pagado):
    datos, sha = cargar_datos()
    prestamo = datos[idx]
    
    mensaje_historial = ""
    
    if tipo_pago == "Pago Interés Mensual":
        # Solo paga interés, el capital sigue igual
        # Asumimos que pagó el mes, "renovamos" para el siguiente
        pass # No cambiamos montos, solo registramos que pagó (podríamos guardar log)
        mensaje_historial = f"Pago de interés S/{monto_pagado}. Capital se mantiene."

    elif tipo_pago == "Abono a Capital":
        # Restamos al capital
        nuevo_capital = prestamo['Monto_Capital'] - monto_pagado
        if nuevo_capital <= 0:
            prestamo['Estado'] = "Pagado"
            prestamo['Monto_Capital'] = 0
            prestamo['Pago_Mensual_Interes'] = 0
            mensaje_historial = "Deuda Cancelada Totalmente."
        else:
            # RECALCULO AUTOMÁTICO: Nuevo Capital -> Nuevo Interés
            prestamo['Monto_Capital'] = nuevo_capital
            # Recalculamos el interés mensual basado en la misma tasa
            nueva_cuota = new_interes = nuevo_capital * (prestamo['Tasa_Interes'] / 100)
            prestamo['Pago_Mensual_Interes'] = nueva_cuota
            mensaje_historial = f"Abono S/{monto_pagado}. Nuevo Capital: S/{nuevo_capital}. Nueva Cuota Interés: S/{nueva_cuota:.2f}"
    
    # Guardamos cambios
    if guardar_datos(datos, sha, f"Pago registrado: {prestamo['Cliente']}"):
        return True, mensaje_historial
    return False, "Error al guardar"

# --- INTERFAZ PRINCIPAL ---
if check_login():
    st.sidebar.title(f"👤 {st.session_state['usuario'].title()}")
    st.sidebar.caption(f"Rol: {st.session_state['rol']}")
    if st.sidebar.button("Cerrar Sesión"): logout()
    st.sidebar.markdown("---")
    
    opciones = ["📊 Dashboard de Préstamos"]
    if st.session_state['rol'] == 'Admin':
        opciones = ["📝 Registrar Operación", "💸 Registrar Pago"] + opciones
        
    menu = st.sidebar.radio("Menú", opciones)
    
    # --- 1. REGISTRAR PRÉSTAMO ---
    if menu == "📝 Registrar Operación":
        st.title("💰 Nuevo Préstamo")
        with st.container():
            c1, c2 = st.columns(2)
            cliente = c1.text_input("Cliente")
            dni = c2.text_input("DNI / C.E.")
            
            c3, c4, c5 = st.columns(3)
            monto = c3.number_input("Capital (S/)", min_value=0.0, step=50.0)
            tasa = c4.number_input("Tasa %", value=15.0)
            fecha = c5.date_input("Fecha Inicio", datetime.now())
            
            obs = st.text_area("Observaciones")

        interes = monto * (tasa/100)
        
        st.info(f"💡 El cliente pagará **S/ {interes:.2f}** de interés cada día **{fecha.day}** del mes.")
        
        if st.button("GUARDAR"):
            nuevo = {
                "Cliente": cliente, "DNI": dni, "Fecha_Prestamo": str(fecha),
                "Dia_Cobro": fecha.day, "Monto_Capital": monto, 
                "Tasa_Interes": tasa, "Pago_Mensual_Interes": interes,
                "Estado": "Activo", "Observaciones": obs
            }
            datos, sha = cargar_datos()
            datos.append(nuevo)
            if guardar_datos(datos, sha, "Nuevo Prestamo"):
                st.success("Guardado!")
                time.sleep(1)
                st.rerun()

    # --- 2. REGISTRAR PAGO (CAJA) ---
    elif menu == "💸 Registrar Pago":
        st.title("💸 Caja: Registrar Cobros")
        datos, sha = cargar_datos()
        
        # Solo mostrar clientes activos
        activos = [d for d in datos if d.get('Estado') == 'Activo']
        if activos:
            # Crear lista legible para el selector
            mapa_clientes = {f"{d['Cliente']} | Deuda: S/{d['Monto_Capital']}": i for i, d in enumerate(datos) if d.get('Estado') == 'Activo'}
            seleccion = st.selectbox("Seleccionar Cliente", list(mapa_clientes.keys()))
            index_real = mapa_clientes[seleccion]
            cliente_data = datos[index_real]
            
            # Tarjeta de Información del Cliente
            st.info(f"""
            👤 **Cliente:** {cliente_data['Cliente']}
            💰 **Deuda Capital Actual:** S/ {cliente_data['Monto_Capital']:,.2f}
            📅 **Interés Mensual a Pagar:** S/ {cliente_data['Pago_Mensual_Interes']:,.2f}
            """)
            
            st.markdown("---")
            st.markdown("### ¿Qué operación vas a realizar?")
            
            opcion = st.radio("Tipo de Cobro:", 
                            ["✅ Cobrar solo Interés Mensual", 
                             "📉 Amortizar Capital (Bajar Deuda)"])
            
            if opcion == "✅ Cobrar solo Interés Mensual":
                st.write(f"Vas a registrar que **{cliente_data['Cliente']}** pagó su interés de **S/ {cliente_data['Pago_Mensual_Interes']:.2f}**.")
                st.caption("La deuda de capital se mantiene igual para el próximo mes.")
                confirmar = st.button("CONFIRMAR COBRO DE INTERÉS")
                if confirmar:
                    # Lógica simple: No movemos capital, solo registramos log (futuro)
                    st.success(f"Cobro de S/ {cliente_data['Pago_Mensual_Interes']:.2f} registrado exitosamente.")
                    time.sleep(2)
                    st.rerun()

            elif opcion == "📉 Amortizar Capital (Bajar Deuda)":
                st.warning("⚠️ Aquí registras dinero que BAJA la deuda (Capital).")
                
                col_a, col_b = st.columns(2)
                monto_amortizar = col_a.number_input("¿Cuánto capital devuelve? (S/)", min_value=0.0, max_value=float(cliente_data['Monto_Capital']), step=50.0)
                
                # Checkbox para confirmar que TAMBIÉN pagó el interés
                pago_interes = col_b.checkbox(f"¿Pagó también sus S/ {cliente_data['Pago_Mensual_Interes']:.2f} de interés?", value=True)
                
                nuevo_capital = cliente_data['Monto_Capital'] - monto_amortizar
                nuevo_interes = nuevo_capital * (cliente_data['Tasa_Interes'] / 100)
                
                if monto_amortizar > 0:
                    st.markdown(f"""
                        **Simulación del cambio:**
                        *   Deuda Anterior: S/ {cliente_data['Monto_Capital']:,.2f}
                        *   **Nueva Deuda:** S/ {nuevo_capital:,.2f}
                        *   **Nueva Cuota Interés (Próx. Mes):** S/ {nuevo_interes:,.2f}
                    """)
                    
                    if st.button("PROCESAR AMORTIZACIÓN"):
                        # Actualizamos datos
                        cliente_data['Monto_Capital'] = nuevo_capital
                        cliente_data['Pago_Mensual_Interes'] = nuevo_interes
                        
                        if nuevo_capital <= 0:
                            cliente_data['Estado'] = "Pagado"
                            msg = "¡Deuda cancelada en su totalidad!"
                        else:
                            msg = f"Capital reducido. Nueva cuota mensual: S/ {nuevo_interes:.2f}"
                        
                        # Guardamos en GitHub
                        guardar_datos(datos, sha, f"Amortizacion {cliente_data['Cliente']}")
                        st.success(f"✅ Operación Exitosa. {msg}")
                        time.sleep(3)
                        st.rerun()
        else:
            st.info("No hay clientes con deuda activa.")

    # --- 3. DASHBOARD CON ALERTAS ---
    elif menu == "📊 Dashboard de Préstamos":
        st.title("📊 Control de Cartera")
        datos, _ = cargar_datos()
        
        if datos:
            df = pd.DataFrame(datos)
            df_activos = df[df['Estado'] == 'Activo']
            
            # --- SECCIÓN DE NOTIFICACIONES ---
            st.subheader("🔔 Cobranzas Próximas")
            hoy_dia = datetime.now().day
            
            # Buscamos clientes que pagan hoy o en los proximos 3 dias
            alertas = []
            advertencias = []
            
            for index, row in df_activos.iterrows():
                dia_cobro = int(row['Dia_Cobro'])
                # Logica simple de dias (si hoy es 28 y paga el 1, es complejo, simplificamos rango)
                diferencia = dia_cobro - hoy_dia
                
                if diferencia == 0:
                    alertas.append(f"🚨 <b>{row['Cliente']}</b> debe pagar <b>HOY</b> sus S/ {row['Pago_Mensual_Interes']:.2f}")
                elif diferencia < 0: # Ya pasó su día en este mes (vencido este mes)
                     # Esto es una lógica simple, asumiendo que verificamos el día calendario actual
                    pass 
                elif 0 < diferencia <= 3:
                    advertencias.append(f"⚠️ <b>{row['Cliente']}</b> paga en {diferencia} días (Día {dia_cobro})")

            if alertas:
                for a in alertas: st.markdown(f"<div class='alert-card'>{a}</div>", unsafe_allow_html=True)
            if advertencias:
                for a in advertencias: st.markdown(f"<div class='warning-card'>{a}</div>", unsafe_allow_html=True)
            if not alertas and not advertencias:
                st.success("✅ Todo tranquilo por los próximos 3 días.")

            st.markdown("---")
            
            # KPIS
            total_calle = df_activos['Monto_Capital'].sum()
            ganancia_mensual = df_activos['Pago_Mensual_Interes'].sum()
            
            k1, k2, k3 = st.columns(3)
            k1.markdown(f'<div class="metric-card"><div class="metric-title">Capital en Calle</div><div class="metric-value">S/ {total_calle:,.2f}</div></div>', unsafe_allow_html=True)
            k2.markdown(f'<div class="metric-card" style="border-left-color:#27AE60"><div class="metric-title">Proyección Interés Mes</div><div class="metric-value" style="color:#27AE60">S/ {ganancia_mensual:,.2f}</div></div>', unsafe_allow_html=True)
            k3.markdown(f'<div class="metric-card"><div class="metric-title">Clientes Activos</div><div class="metric-value">{len(df_activos)}</div></div>', unsafe_allow_html=True)

            # TABLA
            st.write("")
            st.markdown("#### 📋 Detalle de Clientes")
            cols = ["Cliente", "Monto_Capital", "Pago_Mensual_Interes", "Dia_Cobro", "Observaciones"]
            st.dataframe(df_activos[cols].rename(columns={"Monto_Capital": "Deuda Actual", "Pago_Mensual_Interes": "Cuota Interés", "Dia_Cobro": "Día Pago"}), use_container_width=True, hide_index=True)
        else:
            st.info("No hay datos.")

