import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailSender:
    def __init__(self, remetente, senha, servidor_smtp='smtp.office365.com', porta_smtp=587):
        self.remetente = remetente
        self.senha = senha
        self.servidor_smtp = servidor_smtp
        self.porta_smtp = porta_smtp

    def enviar_email(self, destinatario, assunto, corpo):
        # Configuração do e-mail
        mensagem = MIMEMultipart()
        mensagem["From"] = self.remetente
        mensagem["To"] = destinatario
        mensagem["Subject"] = assunto
        mensagem.attach(MIMEText(corpo, "plain"))

        # Conecta-se ao servidor SMTP e envia o e-mail
        with smtplib.SMTP(self.servidor_smtp, self.porta_smtp) as servidor:
            servidor.starttls()  # Habilita a criptografia TLS
            servidor.login(self.remetente, self.senha)
            servidor.send_message(mensagem)
