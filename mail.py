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

# Exemplo de uso
if __name__ == "__main__":
    remetente = "seu_email@hotmail.com"  # Preencha com seu e-mail
    senha = "sua_senha"  # Preencha com sua senha
    destinatario = "destinatario@hotmail.com"  # Preencha com o destinatário do e-mail
    assunto = "Assunto do e-mail"
    corpo = "Corpo do e-mail"

    sender = EmailSender(remetente, senha)
    print("Enviando e-mail para", destinatario, "...")
    sender.enviar_email(destinatario, assunto, corpo)
    print("E-mail enviado!")
