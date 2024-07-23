import argparse
import os
import subprocess
import time
import schedule
import paramiko
from zipfile import ZipFile, ZIP_DEFLATED
import sys

class BackupManager:
    def __init__(self, db_host, db_user, db_pass, db_name, bkup_path, rmt_host, rmt_user, rmt_pass, rmt_bkup_path, rmt_port):
        self.DB_HOST = db_host
        self.DB_USER = db_user
        self.DB_PASS = db_pass
        self.DB_NAME = db_name
        self.BKUP_PATH = bkup_path
        self.RMT_HOST = rmt_host
        self.RMT_USER = rmt_user
        self.RMT_PASS = rmt_pass
        self.RMT_BKUP_PATH = rmt_bkup_path
        self.RMT_PORT = rmt_port

    def ssh_send_file(self, src, dest, usr, pwd):
        transport = paramiko.Transport((self.RMT_HOST, 22))
        try:
            transport.connect(username=usr, password=pwd)
            sftp = paramiko.SFTPClient.from_transport(transport)

            try:
                sftp.put(src, dest)
                print(f"File '{src}' sent successfully to '{dest}' on server '{self.RMT_HOST}'.")
            except FileNotFoundError:
                print(f"Error: The specified path '{dest}' is incorrect or does not exist.")
            except Exception as error:
                print(f"Error sending file: {str(error)}")
            finally:
                sftp.close()
        except Exception as error:
            print(f"Error connecting to remote server: {str(error)}")
        finally:
            transport.close()

    def delete_old_bkups(self):
        try:
            transport = paramiko.Transport((self.RMT_HOST, 22))
            transport.connect(username=self.RMT_USER, password=self.RMT_PASS)
            sftp = paramiko.SFTPClient.from_transport(transport)
            
            files = sftp.listdir(self.RMT_BKUP_PATH)
            thirty_days_ago = time.time() - (30 * 24 * 60 * 60)

            for file in files:
                filepath = os.path.join(self.RMT_BKUP_PATH, file)
                file_stats = sftp.stat(filepath)
                if file_stats.st_mtime < thirty_days_ago:
                    sftp.remove(filepath)
                    print(f"Old backup '{file}' removed from remote server.")

            sftp.close()
            transport.close()
        except Exception as error:
            print(f"Error deleting old backups: {str(error)}")

    def delete_local_bkup(self, bkup_path):
        try:
            subprocess.run(["rm", "-rf", bkup_path])
            print(f"Local backup '{bkup_path}' deleted successfully.")
        except Exception as error:
            print(f"Error deleting local backup: {str(error)}")

    def perform_bkup(self, zip_locally=True):
        timestamp = time.strftime('%Y-%m-%d-%H-%M-%S')
        bkup_file = f"{self.DB_NAME}_{timestamp}.bkup_psql"
        local_bkup_path = os.path.join(self.BKUP_PATH, bkup_file)
        remote_bkup_path = os.path.join(self.RMT_BKUP_PATH, bkup_file)
        
        os.environ['PGPASSWORD'] = self.DB_PASS
        bkup_cmd = f"pg_dump -U {self.DB_USER} -h {self.DB_HOST} -d {self.DB_NAME} --role 'ALTERDATA_GROUP_ALTERDATA_PACK' --clean --verbose --format custom --blobs -F c -E utf8 {local_bkup_path}"

        print(f"Backup started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            os.system(bkup_cmd)

            if zip_locally:
                semextensao = bkup_file.split('.')[0]
                nomezip = os.path.join(self.BKUP_PATH, semextensao + '.zip')
                with ZipFile(nomezip, "w", compression=ZIP_DEFLATED) as arquivozip:
                    arquivozip.write(local_bkup_path, bkup_file)

                file_to_send = nomezip
            else:
                file_to_send = local_bkup_path

            self.ssh_send_file(file_to_send, remote_bkup_path, self.RMT_USER, self.RMT_PASS)
            print(f"Backup transferred to remote server: {self.RMT_HOST}:{remote_bkup_path}")
            print(f"Backup completed at {time.strftime('%H:%M:%S')}")

            self.delete_old_bkups()
            self.delete_local_bkup(local_bkup_path)
            if zip_locally:
                self.delete_local_bkup(file_to_send)
                print(f"Local backup '{file_to_send}' deleted successfully.")
            else:
                self.delete_local_bkup(local_bkup_path)
                print(f"Local backup '{local_bkup_path}' deleted successfully.")

        except Exception as error:
            print(f"Error performing backup: {str(error)}")

def schedule_bkup(db_host, db_user, db_pass, db_name, bkup_path, rmt_host, rmt_user, rmt_pass, rmt_bkup_path, rmt_port, scheduled_time, zip_locally):
    bkup_mgr = BackupManager(
        db_host, db_user, db_pass, db_name,
        bkup_path, rmt_host, rmt_user,
        rmt_pass, rmt_bkup_path, rmt_port
    )

    schedule.every().day.at(scheduled_time).do(
        bkup_mgr.perform_bkup, zip_locally)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python script to perform automatic backups of PostgreSQL.")

    parser.add_argument('-t', '--scheduled_time', help='Time for scheduling backups (format HH:MM).')
    parser.add_argument('-H', '--DB_HOST', help='IP address or hostname of the PostgreSQL database.')
    parser.add_argument('-U', '--DB_USER', help='Username of the PostgreSQL database.')
    parser.add_argument('-P', '--DB_PASS', help='Password associated with the PostgreSQL database user.')
    parser.add_argument('-N', '--DB_NAME', help='Name of the PostgreSQL database.')
    parser.add_argument('-B', '--BKUP_PATH', help='Local path where the backup will be stored.')
    parser.add_argument('-R', '--RMT_HOST', help='IP address or hostname of the remote server.')
    parser.add_argument('-r', '--RMT_USER', help='Username for authentication on the remote server.')
    parser.add_argument('-p', '--RMT_PASS', help='Password associated with the remote server user.')
    parser.add_argument('-b', '--RMT_BKUP_PATH', help='Path on the remote server where the backup will be stored.')
    parser.add_argument('-C', '--RMT_PORT', help='SSH port of the remote server.')
    parser.add_argument('-z', '--ZIP_LOCALLY', action='store_true', help='Flag to indicate whether to zip the backup locally.')

    args = parser.parse_args()

    if not all(vars(args).values()):
        print("All necessary parameters are mandatory. Run the script with -h to see parameter descriptions.")
        sys.exit(1)

    schedule_bkup(
        args.DB_HOST, args.DB_USER, args.DB_PASS, args.DB_NAME,
        args.BKUP_PATH, args.RMT_HOST, args.RMT_USER,
        args.RMT_PASS, args.RMT_BKUP_PATH, args.RMT_PORT,
        args.scheduled_time, args.ZIP_LOCALLY
    )
