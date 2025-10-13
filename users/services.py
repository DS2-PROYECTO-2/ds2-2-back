from django.core.mail import send_mail
from django.conf import settings

def send_password_reset_email(user, reset_url: str) -> str:
    """
    Envía email de restablecimiento de contraseña
    En desarrollo, también devuelve el enlace para mostrar en consola
    """
    subject = '[DS2] Restablece tu contraseña'
    text = (
        f"Hola {user.get_full_name() or user.username},\n\n"
        f"Recibimos una solicitud para restablecer tu contraseña.\n"
        f"Puedes hacerlo en el siguiente enlace (expira en 2 horas):\n{reset_url}\n\n"
        f"Si no solicitaste esto, ignora este mensaje.\n"
    )
    html = f"""
<!doctype html>
<html>
  <body style="font-family:Segoe UI,Arial,sans-serif;background:#f6f7f9;padding:24px;">
    <div style="max-width:560px;margin:0 auto;background:#ffffff;border-radius:12px;box-shadow:0 6px 24px rgba(0,0,0,.08);overflow:hidden;">
      <div style="padding:20px 24px;border-bottom:1px solid #eef2f7;">
        <h2 style="margin:0;color:#111827;">Restablecer contraseña</h2>
        <p style="margin:6px 0 0;color:#6b7280;">El enlace expira en 2 horas</p>
      </div>
      <div style="padding:20px 24px;">
        <p style="margin:0 0 16px;color:#111827;">Hola {user.get_full_name() or user.username}, haz clic en el botón para restablecer tu contraseña:</p>
        <a href="{reset_url}" style="text-decoration:none;background:#2563eb;color:#ffffff;padding:10px 16px;border-radius:8px;display:inline-block;">Restablecer contraseña</a>
        <p style="margin:16px 0 0;color:#6b7280;font-size:13px;">Si no solicitaste esto, ignora este mensaje.</p>
      </div>
    </div>
    <p style="text-align:center;color:#9ca3af;font-size:12px;margin-top:16px;">DS2 • Notificación automática</p>
  </body>
</html>
"""
    send_mail(
        subject=subject,
        message=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html,
        fail_silently=False,
    )
    
    # En desarrollo, devolver el enlace para mostrar en consola
    return reset_url