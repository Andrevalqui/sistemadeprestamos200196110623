import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from supabase import create_client

# Configuración desde variables de entorno (Secretos de GitHub)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASS = os.environ.get("GMAIL_PASS")
RECEPTOR = os.environ.get("RECEPTOR")

def check_and_notify():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    response = supabase.table("prestamos").select("*").eq("Estado", "Activo").execute()
    prestamos = response.data
    
    hoy = datetime.now().date()
    alerta_clientes = []

    for p in prestamos:
        vencimiento = datetime.strptime(p['Fecha_Proximo_Pago'], "%Y-%m-%d").date()
        dias_faltantes = (vencimiento - hoy).days
        
        # --- CORRECCIÓN IMPORTANTE AQUÍ ---
        # Ahora incluirá todos los vencimientos de los próximos 5 días Y los que ya pasaron
        if dias_faltantes <= 5:
            alerta_clientes.append({
                "nombre": p['Cliente'],
                "monto": p['Pago_Mensual_Interes'],
                "dias": dias_faltantes,
                "fecha": vencimiento.strftime("%d/%m/%Y")
            })

    if alerta_clientes:
        enviar_correo(alerta_clientes)

def enviar_correo(clientes):
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = RECEPTOR
    msg['Subject'] = f"🏦 ALERTA DIARIA: {len(clientes)} Vencimientos Críticos"

    filas = ""
    # Ordenamos por urgencia (los más vencidos primero)
    clientes_ordenados = sorted(clientes, key=lambda x: x['dias'])
    
    for c in clientes_ordenados:
        estado_texto = ""
        color = ""
        if c['dias'] < 0:
            estado_texto = f"EN MORA ({abs(c['dias'])} días)"
            color = "background-color: #f5c6cb;" # Rojo suave
        elif c['dias'] == 0:
            estado_texto = "VENCE HOY"
            color = "background-color: #ffeeba;" # Amarillo suave
        else:
            estado_texto = f"En {c['dias']} días"
        
        filas += f"<tr style='{color}'><td>{c['nombre']}</td><td>S/ {c['monto']}</td><td>{c['fecha']}</td><td><b>{estado_texto}</b></td></tr>"

    html = f"""
    <html><body>
        <h2>Resumen de Vencimientos y Moras</h2>
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr style="background:#1a1a1a; color:gold;">
                <th>Cliente</th><th>Cuota</th><th>Fecha Límite</th><th>Estado</th>
            </tr>{filas}
        </table>
    </body></html>"""
    msg.attach(MIMEText(html, 'html'))
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)
    print("Correo enviado con éxito")
