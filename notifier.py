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
    
    # Consultar préstamos activos
    response = supabase.table("prestamos").select("*").eq("estado", "Activo").execute()
    prestamos = response.data
    
    hoy = datetime.now().date()
    alerta_clientes = []

    for p in prestamos:
        vencimiento = datetime.strptime(p['fecha_proximo_pago'], "%Y-%m-%d").date()
        dias_faltantes = (vencimiento - hoy).days
        
        # Filtro: de 0 a 5 días
        if 0 <= dias_faltantes <= 5:
            alerta_clientes.append({
                "nombre": p['cliente'],
                "monto": p['pago_mensual_interes'],
                "dias": dias_faltantes,
                "fecha": vencimiento.strftime("%d/%m/%Y")
            })

    if alerta_clientes:
        enviar_correo(alerta_clientes)

def enviar_correo(clientes):
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = RECEPTOR
    msg['Subject'] = f"⚠️ ALERTA DIARIA: {len(clientes)} Vencimientos Próximos"

    filas = ""
    for c in clientes:
        filas += f"<tr><td>{c['nombre']}</td><td>S/ {c['monto']}</td><td>{c['fecha']}</td><td><b>{c['dias']} días</b></td></tr>"

    html = f"""
    <html>
    <body>
        <h2>Resumen de Vencimientos (Próximos 5 días)</h2>
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr style="background:#1a1a1a; color:gold;">
                <th>Cliente</th><th>Interés</th><th>Fecha</th><th>Faltan</th>
            </tr>
            {filas}
        </table>
    </body>
    </html>
    """
    msg.attach(MIMEText(html, 'html'))
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)
    print("Correo enviado con éxito")

if __name__ == "__main__":
    check_and_notify()
