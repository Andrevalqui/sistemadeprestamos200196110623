import os
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from supabase import create_client

# Forzar que los mensajes se vean en tiempo real en GitHub
def print_log(msg):
    print(msg)
    sys.stdout.flush()

# Leer variables
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASS = os.environ.get("GMAIL_PASS")
RECEPTOR = os.environ.get("RECEPTOR")

def check_and_notify():
    try:
        print_log("--- INICIANDO PROCESO DE NOTIFICACIÓN ---")
        
        if not SUPABASE_URL or not SUPABASE_KEY:
            print_log("❌ ERROR: Faltan las credenciales de Supabase en GitHub Secrets.")
            return

        print_log("Conectando a Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Consultar solo los préstamos activos
        response = supabase.table("prestamos").select("*").eq("Estado", "Activo").execute()
        prestamos = response.data
        
        print_log(f"Conexión exitosa. Se encontraron {len(prestamos)} préstamos activos.")
        
        hoy = datetime.now().date()
        alerta_clientes = []

        for p in prestamos:
            v_pago = p.get('Fecha_Proximo_Pago')
            if not v_pago: continue
            
            vencimiento = datetime.strptime(str(v_pago), "%Y-%m-%d").date()
            dias = (vencimiento - hoy).days
            
            print_log(f"Revisando: {p['Cliente']} | Vence en: {dias} días")

            if dias <= 5:
                alerta_clientes.append({
                    "nombre": p['Cliente'],
                    "monto": p['Pago_Mensual_Interes'],
                    "dias": dias,
                    "fecha": vencimiento.strftime("%d/%m/%Y")
                })

        if alerta_clientes:
            print_log(f"Preparando envío de correo para {len(alerta_clientes)} deudores...")
            enviar_correo(alerta_clientes)
        else:
            print_log("✅ No hay clientes para notificar hoy.")

    except Exception as e:
        print_log(f"❌ ERROR CRÍTICO DURANTE LA EJECUCIÓN: {str(e)}")

def enviar_correo(clientes):
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = RECEPTOR
        msg['Subject'] = f"🏦 ALERTA: {len(clientes)} Vencimientos Críticos"

        filas = ""
        # Ordenamos: primero los que tienen más días de mora
        for c in sorted(clientes, key=lambda x: x['dias']):
            color = "#E74C3C" if c['dias'] < 0 else "#F39C12" if c['dias'] == 0 else "#2C3E50"
            estado = f"MORA ({abs(c['dias'])} días)" if c['dias'] < 0 else "VENCE HOY" if c['dias'] == 0 else f"Faltan {c['dias']} días"
            
            filas += f"""
            <tr style='border-bottom: 1px solid #ddd;'>
                <td style='padding:8px;'>{c['nombre']}</td>
                <td style='padding:8px;'>S/ {c['monto']:,.2f}</td>
                <td style='padding:8px;'>{c['fecha']}</td>
                <td style='padding:8px; color:{color}; font-weight:bold;'>{estado}</td>
            </tr>"""

        html = f"""
        <html><body>
            <h2 style='color:#D4AF37;'>Reporte Automático de Cobranza</h2>
            <table border='1' style='border-collapse: collapse; width: 100%; font-family: sans-serif;'>
                <tr style='background-color: #1a1a1a; color: white;'>
                    <th>Cliente</th><th>Cuota</th><th>Fecha</th><th>Estado</th>
                </tr>
                {filas}
            </table>
            <p style='font-size: 11px; color: grey;'>Enviado desde Sistema Valqui v2.0</p>
        </body></html>"""
        
        msg.attach(MIMEText(html, 'html'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASS)
            server.send_message(msg)
        print_log("✅ ¡Correo enviado con éxito!")
        
    except Exception as e:
        print_log(f"❌ Error al enviar el correo: {str(e)}")

if __name__ == "__main__":
    check_and_notify()
