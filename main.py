import argparse
import os
import subprocess
import time
import schedule
import paramiko
import zipfile

class BackupManager:
    def __init__(self, db_host, db_user, db_pass, db_name, backup_path, remote_host, remote_user, remote_pass, remote_backup_path, remote_port):
        self.DB_HOST = db_host
        self.DB_USER = db_user
        self.DB_PASS = db_pass
        self.DB_NAME = db_name
        self.BACKUP_PATH = backup_path
        self.REMOTE_HOST = remote_host
        self.REMOTE_USER = remote_user
        self.REMOTE_PASS = remote_pass
        self.REMOTE_BACKUP_PATH = remote_backup_path
        self.REMOTE_PORT = remote_port

    def zip_file(self, source, destination):
        try:
            with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(source, os.path.basename(source))
                print(f"Arquivo zip criado com sucesso em {destination}")
                return destination
        except Exception as error:
            print(f"Erro ao criar o arquivo ZIP: {str(error)}")
            return None

    def ssh_send_file(self, source, destination):
        transport = paramiko.Transport((self.REMOTE_HOST, 22))
        try:
            transport.connect(username=self.REMOTE_USER, password=self.REMOTE_PASS)
            sftp = paramiko.SFTPClient.from_transport(transport)

            try:
                sftp.put(source, destination)
                print(f"Arquivo '{source}' enviado com sucesso para '{destination}' no servidor '{self.REMOTE_HOST}'.")
            except FileNotFoundError:
                print(f"Erro: O caminho especificado '{destination}' não está correto ou não existe.")
            except Exception as error:
                print(f"Erro ao enviar o arquivo: {str(error)}")
            finally:
                sftp.close()
        except Exception as error:
            print(f"Erro ao conectar ao servidor remoto: {str(error)}")
        finally:
            transport.close()

    def perform_backup(self, zip_locally=True):
        timestamp = time.strftime('%Y-%m-%d-%H-%M-%S')
        backup_file = f"{self.DB_NAME}_{timestamp}.backup_postgresql"
        local_backup_path = os.path.join(self.BACKUP_PATH, backup_file)
        remote_backup_path = os.path.join(self.REMOTE_BACKUP_PATH, backup_file)

        os.environ['PGPASSWORD'] = self.DB_PASS
        backup_command = f"pg_dump -U {self.DB_USER} -h {self.DB_HOST} -d {self.DB_NAME} --format custom --blobs -F c > {local_backup_path}"

        print(f"Início do backup em: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            os.system(backup_command)

            if zip_locally:
                zip_path = self.zip_file(local_backup_path, f"{local_backup_path}.zip")
                local_backup_path = f"{local_backup_path}.zip"

                if zip_path:
                    self.ssh_send_file(local_backup_path, remote_backup_path)
                    print(f"Backup transferido: {self.REMOTE_HOST}:{remote_backup_path}")
                    print(f"Backup realizado às {time.strftime('%H:%M:%S')}")
                    print(f'Backup compactado com sucesso em {zip_path}')
            else:
                self.ssh_send_file(local_backup_path, remote_backup_path)
                print(f"Backup transferido: {self.REMOTE_HOST}:{remote_backup_path}")
                print(f"Backup realizado às {time.strftime('%H:%M:%S')}")
        except Exception as error:
            print(f"Erro ao transferir o backup: {str(error)}")

def schedule_backup(db_host, db_user, db_pass, db_name, backup_path, remote_host, remote_user, remote_pass, remote_backup_path, remote_port, zip_locally, scheduled_time):
    backup_manager = BackupManager(
        db_host, db_user, db_pass, db_name,
        backup_path, remote_host, remote_user,
        remote_pass, remote_backup_path, remote_port
    )

    schedule.every().day.at(scheduled_time).do(
        backup_manager.perform_backup, zip_locally)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script Python para realizar backups automáticos do PostgreSQL.")

    parser.add_argument('-t', '--scheduled_time', help='Horário para agendamento dos backups (formato HH:MM).')
    parser.add_argument('-H', '--DB_HOST', help='Endereço IP ou nome do host do banco de dados PostgreSQL.')
    parser.add_argument('-U', '--DB_USER', help='Nome de usuário do banco de dados PostgreSQL.')
    parser.add_argument('-P', '--DB_PASS', help='Senha associada ao usuário do banco de dados PostgreSQL.')
    parser.add_argument('-N', '--DB_NAME', help='Nome do banco de dados PostgreSQL.')
    parser.add_argument('-B', '--BACKUP_PATH', help='Caminho local onde o backup será armazenado.')
    parser.add_argument('-R', '--REMOTE_HOST', help='Endereço IP ou nome do host do servidor remoto.')
    parser.add_argument('-r', '--REMOTE_USER', help='Nome de usuário para autenticação no servidor remoto.')
    parser.add_argument('-p', '--REMOTE_PASS', help='Senha associada ao usuário do servidor remoto.')
    parser.add_argument('-b', '--REMOTE_BACKUP_PATH', help='Caminho no servidor remoto onde o backup será armazenado.')
    parser.add_argument('-C', '--REMOTE_PORT', help='Porta SSH do servidor remoto.')
    parser.add_argument('-z', '--zip_locally', action='store_true', help='Zipar o backup localmente.')

    args = parser.parse_args()

    if not all(vars(args).values()):
        print("Todos os parâmetros necessários são obrigatórios. Execute o script com -h para ver a descrição dos parâmetros.")
        sys.exit(1)

    schedule_backup(
        args.DB_HOST, args.DB_USER, args.DB_PASS, args.DB_NAME,
        args.BACKUP_PATH, args.REMOTE_HOST, args.REMOTE_USER,
        args.REMOTE_PASS, args.REMOTE_BACKUP_PATH, args.REMOTE_PORT,
        args.zip_locally, args.scheduled_time
    )
