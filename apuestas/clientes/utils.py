from django.core.mail import send_mail
from django.conf import settings

def enviar_email_registro(cliente):
    subject = 'Bienvenido a Apuestas'
    message = f'Hola {cliente.nombre}, gracias por registrarte.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [cliente.email]
    send_mail(subject, message, email_from, recipient_list)

def enviar_email_apuesta(cliente, apuesta):
    subject = 'Nueva Apuesta Realizada'
    message = f'Hola {cliente.nombre}, has realizado una nueva apuesta de {apuesta.monto}.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [cliente.email]
    send_mail(subject, message, email_from, recipient_list)
