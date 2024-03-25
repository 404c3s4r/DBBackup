<h1 align="center">DBBackup</h1>

The initial intention was to automate the backup process in a company that used a Debian system and had a PostgreSQL database running an Alterdata database, which employees used. It was necessary to perform a backup daily, from Monday to Sunday, after business hours. Over time, I will be adding new functionalities, such as backup status via email, malware checking on the server running the database, backup redundancy, and other features aimed at ensuring that the backup is done securely and efficiently.

## How to Use?

Clone the repository
```bash
  git clone https://github.com/robertocoliver/backup_postgresql_linux
```

Navigate to the directory:
```bash
  cd backup_postgresql_linux
```
# Usage
Run:
```sh
main.py -h
```
This command will display the tool's help.

```yaml
-t [backup_time]: Specifies the time for the backup;
-H [database_host]: Defines the IP address or hostname of the PostgreSQL database;
-U [database_user]: Specifies the username of the PostgreSQL database;
-P [database_password]: Sets the password for the PostgreSQL database user;
-N [database_name]: Specifies the name of the PostgreSQL database to be backed up;
-B [local_backup_path]: Specifies the local directory where the backups will be stored;
-R [remote_host]: Indicates the IP address or hostname of the remote server;
-r [remote_user]: Specifies the username for authentication on the remote server;
-p [remote_password]: Sets the password associated with the remote server user;
-b "[remote_server_path]": Specifies the path on the remote server where the backups will be stored;
-C [ssh_port]: Specifies the SSH port of the remote server;
-z: Flag to indicate whether to zip the backup locally.

```
Example:
```bash
python3 main.py -t [backup_time] -H [database_host] -U [database_user] -P [database_password] -N [database_name] -B [local_backup_path] -R [remote_host] -r [remote_user] -p [remote_password] -b "[remote_server_path]" -C [ssh_port] 
```
## Future Improvements

- Compressed backup file sent to a remote server.
- Integrity check: Implementation of a mechanism to verify the backup data integrity.
- Generation of a hash output after the backup process and comparison with the backup file received on the remote server.
- RAID 1 implemented for data replication between two disks.
- RAID 0 used to optimize performance by distributing data blocks among multiple disks.
- RAID 5 employed for distributed and redundant data storage.
- Functionality implemented to send backup status notifications via email or WhatsApp.
- Failover mechanism implemented: If the database is deleted or any issues occur, the code automatically retrieves the latest backup from the remote server to create a new database.
- Malware checking on the server running the database

## Technology Used:
- **Python** 

## License
[MIT](https://choosealicense.com/licenses/mit/)

## 🔗 My portfolio
[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/robertocoliver/)
[![portfolio](https://img.shields.io/badge/my_portfolio-000?style=for-the-badge&logo=ko-fi&logoColor=white)](https://medium.com/@robertocoliver)

#### Legal Disclaimer
> As this is "freeware" software, the user who utilizes it does not share responsibility with the author. Therefore, the author is exempt from any liability for any damage resulting from the use or misuse of the tool. If you do not agree, do not use the tool.

> This tool is intended for backup purposes only and is provided "as is", without warranties of any kind, express or implied. The use of this tool is at the user's own risk. The author assumes no responsibility for losses or damages resulting from the use of this tool.
