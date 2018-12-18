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

        # Run command
        stdin, stdout, stderr = conn.exec_command('showsys -d')

        # Collect data from output
        while True:
            line = stdout.readline()
            if line != '':
                if line.startswith('System Name'):
                    array = (line.split(':'))
                    array = (array[1].strip())
                if line.startswith('System Model'):
                    model = (line.split(':'))
                    model = (model[1].strip())
                if line.startswith('Serial Number'):
                    serial = (line.split(':'))
                    serial = (serial[1].strip())
                if line.startswith('Total Capacity'):
                    totalcap = (line.split(':'))
                    totalcap = (totalcap[1].strip())
                if line.startswith('Allocated Capacity'):
                    alloccap = (line.split(':'))
                    alloccap = (alloccap[1].strip())
                if line.startswith('Free Capacity'):
                    freecap = (line.split(':'))
                    freecap = (freecap[1].strip())
                if line.startswith('Failed Capacity'):
                    failedcap = (line.split(':'))
                    failedcap = (failedcap[1].strip())
            else:
                break

        # Run command
        stdin, stdout, stderr = conn.exec_command('showversion')

        #Collect data from output
        while True:
            line = stdout.readline()
            if line != '':
                if line.startswith('Release'):
                    version = (line.split("Release version"))
                    version = (version[1].strip())
                if line.startswith('Patches'):
                    patches = (line.split(':'))
                    patches = (patches[1].strip())
            else:
                break
        now = datetime.now().strftime("%d-%m-%Y %H:%M")
        conn = sqlite3.connect('/home/ed/Dev/dashboard')
        c = conn.cursor()
        c.execute('''INSERT INTO array (date, array, model, serial, version, patches, totalcap, alloccap, freecap, failedcap) 
        VALUES(?,?,?,?,?,?,?,?,?,?)''', (now, array, model, serial, version, patches, totalcap, alloccap, freecap, failedcap))
        conn.commit()
        conn.close

DataCollection('10.248.231.68')