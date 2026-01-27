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
        msg['Subject'] = f"🏦 REPORTE EJECUTIVO: {len(clientes)} Vencimientos Detectados"

        filas = ""
        # Ordenamos: primero los que tienen más días de mora
        for c in sorted(clientes, key=lambda x: x['dias']):
            # Colores gerenciales según gravedad
            color_fondo = "#FDEDEC" if c['dias'] < 0 else "#FEF9E7" if c['dias'] == 0 else "#F4F6F7"
            color_texto = "#C0392B" if c['dias'] < 0 else "#9A7D0A" if c['dias'] == 0 else "#2C3E50"
            estado = f"MORA ({abs(c['dias'])} días)" if c['dias'] < 0 else "VENCE HOY" if c['dias'] == 0 else f"Faltan {c['dias']} días"
            
            filas += f"""
            <tr style="background-color: {color_fondo};">
                <td style="padding: 15px; border-bottom: 1px solid #ddd; font-weight: bold; color: #1C1C1C;">{c['nombre']}</td>
                <td style="padding: 15px; border-bottom: 1px solid #ddd; text-align: center; color: #1C1C1C;">S/ {c['monto']:,.2f}</td>
                <td style="padding: 15px; border-bottom: 1px solid #ddd; text-align: center; color: #1C1C1C;">{c['fecha']}</td>
                <td style="padding: 15px; border-bottom: 1px solid #ddd; text-align: center; color: {color_texto}; font-weight: 900; text-transform: uppercase; font-size: 12px;">{estado}</td>
            </tr>"""

        html = f"""
        <html>
        <body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: 'Segoe UI', Arial, sans-serif;">
            <table align="center" border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #ffffff; border-radius: 15px; overflow: hidden; margin-top: 40px; margin-bottom: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.1);">
                <!-- HEADER LUXURY -->
                <tr>
                    <td align="center" style="background: linear-gradient(135deg, #1a1a1a 0%, #333333 100%); padding: 40px 20px; border-bottom: 4px solid #D4AF37;">
                        <img src="https://cdn-icons-png.flaticon.com/512/2489/2489756.png" width="60" style="filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5)); margin-bottom: 15px;">
                        <h1 style="color: #D4AF37; margin: 0; text-transform: uppercase; letter-spacing: 4px; font-size: 24px; font-weight: 900;">Reporte de Cobranza</h1>
                        <p style="color: #ffffff; margin-top: 5px; opacity: 0.8; font-size: 13px; text-transform: uppercase; letter-spacing: 2px;">Gestión de Activos & Créditos</p>
                    </td>
                </tr>
                
                <!-- CONTENT -->
                <tr>
                    <td style="padding: 30px;">
                        <p style="color: #2C3E50; font-size: 16px; margin-bottom: 25px;">Estimado Administrador,<br><br>Se ha realizado un escaneo automático del sistema y se han detectado <b>{len(clientes)}</b> vencimientos que requieren atención inmediata:</p>
                        
                        <table width="100%" border="0" cellpadding="0" cellspacing="0" style="border-collapse: collapse;">
                            <thead>
                                <tr style="background-color: #1a1a1a;">
                                    <th style="color: #D4AF37; padding: 12px; font-size: 12px; text-align: left; text-transform: uppercase;">Cliente</th>
                                    <th style="color: #D4AF37; padding: 12px; font-size: 12px; text-align: center; text-transform: uppercase;">Cuota</th>
                                    <th style="color: #D4AF37; padding: 12px; font-size: 12px; text-align: center; text-transform: uppercase;">Vence</th>
                                    <th style="color: #D4AF37; padding: 12px; font-size: 12px; text-align: center; text-transform: uppercase;">Estado</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filas}
                            </tbody>
                        </table>
                        
                        <div style="margin-top: 30px; padding: 20px; background-color: #FDFEFE; border: 1px dashed #D4AF37; border-radius: 10px; text-align: center;">
                            <p style="color: #2C3E50; font-size: 14px; margin: 0;">Para gestionar estos pagos, acceda al portal administrativo:</p>
                            <p style="margin-top: 15px;">
                                <a href="https://sistemadeprestamos200196110623-tehmek4ykvshbumtmyzcjx.streamlit.app/" style="background: linear-gradient(90deg, #D4AF37 0%, #B8860B 100%); color: #ffffff; text-decoration: none; padding: 12px 30px; border-radius: 8px; font-weight: bold; text-transform: uppercase; font-size: 13px; display: inline-block; box-shadow: 0 4px 15px rgba(212,175,55,0.3);">Abrir Sistema Financiero</a>
                            </p>
                        </div>
                    </td>
                </tr>
                
                <!-- FOOTER -->
                <tr>
                    <td align="center" style="padding: 20px; background-color: #f9f9f9; border-top: 1px solid #eee;">
                        <p style="color: #999; font-size: 11px; margin: 0;">ESTE ES UN MENSAJE AUTOMÁTICO GENERADO POR<br><b>ANDRE VALQUI SYSTEM v2.0 | ENCRIPTACIÓN DE GRADO BANCARIO</b></p>
                        <p style="color: #999; font-size: 10px; margin-top: 5px;">© {datetime.now().year} Todos los derechos reservados.</p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASS)
            server.send_message(msg)
        print_log("✅ ¡Correo Ejecutivo enviado con éxito!")
        
    except Exception as e:
        print_log(f"❌ Error al enviar el correo: {str(e)}")check_and_notify()

if __name__ == "__main__":
    check_and_notify()
