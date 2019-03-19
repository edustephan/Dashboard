import paramiko
import sqlite3
from datetime import datetime


class DataCollection:
    def __init__(self,ip):
        # Connect to array using private key
        paramiko.util.log_to_file('/home/ed/Dev/ssh.log')
        key = paramiko.RSAKey.from_private_key_file('/home/ed/.ssh/id_rsa')
        conn = paramiko.SSHClient()
        conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conn.connect(hostname = ip, username = 'metrics', pkey = key)
        now = datetime.now().strftime("%d-%m-%Y %H:%M")
        sql_conn = sqlite3.connect('/home/ed/Dev/dashboard.db', timeout=10)
        c = sql_conn.cursor()

        # Run command
        stdin, stdout, stderr = conn.exec_command('showvv -showcols Name,UsrCPG,VSize_MB,Usr_Used_Perc,Compaction')

        # Collect data from output
        while True:
            line = stdout.readline()
            if line != '':
                line = [splits for splits in line.split(' ')]
                line = list(filter(None,line))
                if line[0].startswith('Name'):
                    continue
                if line[0].startswith('---'):
                    continue
                if line[0].startswith('total'):
                    continue
                lunname = line[0]
                luncpg = line[1]
                lunsize = line[2]
                lunused_perc = line[3]
                luncompaction = line[4]
            else:
                break

            print(lunname)
            print(luncpg)
            print(lunsize)
            print(lunused_perc)
            print(luncompaction)




#DataCollection('10.248.231.68')
DataCollection('142.71.40.232')