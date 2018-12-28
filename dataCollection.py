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

        c.execute('''INSERT INTO array (date, array, model, serial, version, patches, totalcap, alloccap, freecap, failedcap) 
        VALUES(?,?,?,?,?,?,?,?,?,?)''', (now, array, model, serial, version, patches, totalcap, alloccap, freecap, failedcap))
        sql_conn.commit()


        # Run command
        stdin, stdout, stderr = conn.exec_command('showhost -d')

        #Collect data from output
        while True:
            line = stdout.readline()
            if line != '':
                line = [splits for splits in line.split(' ')]
                line = list(filter(None,line))
                if line[0].startswith('Id'):
                    continue
                if(line[0]).startswith('--'):
                    continue
                else:
                    hostname = line[1]
                    persona = line[2]
                    wwn = line[3]
                    snp = line[4]
            else:
                break
            # Check if the row exists before insert
            c.execute(''' SELECT * FROM hosts WHERE (array=? AND hostname=? and persona=? AND wwn=? AND snp=?)''',
            (array,hostname,persona,wwn,snp))
            entry = c.fetchone()

            if entry is None:            
                c.execute(''' INSERT OR IGNORE INTO hosts (array, hostname, persona, wwn, snp)
                VALUES(?,?,?,?,?)''', (array,hostname,persona,wwn,snp))
                sql_conn.commit()


        # Run command
        stdin, stdout, stderr = conn.exec_command('shownode')

        #Collect data from output
        while True:
            line = stdout.readline()
            if line != '':
                line = [splits for splits in line.split(' ')]
                line = list(filter(None,line))
                if line[0].startswith('Control'):
                    continue
                if line[0].startswith('Node'):
                    continue
                else:
                    nodename = line[1]
                    state = line[2]
                    led = line[6]
            else:
                break  
            c.execute(''' INSERT INTO node (array, nodename, state, led, time)
            VALUES(?,?,?,?,?)''', (array,nodename,state,led,now))
            sql_conn.commit()
        

        # Run command
        stdin, stdout, stderr = conn.exec_command('showalert -oneline')

        #Collect data from output
        while True:
            line = stdout.readline()
            if line != '':
                line = [splits for splits in line.split(' ')]
                line = list(filter(None,line))
                if line[0].startswith('Id'):
                    continue
                if line[0].startswith('---'):
                    continue
                if len(line) < 4:
                    continue
                alertid = line[0]
                alertstate = line[1]
                alerttime = ' '.join(line[3:5])
                severity = line[6]
                message = ' '.join(line[7:])
            else:
                break

            # Check if the row exists before insert
            c.execute(''' SELECT * FROM alert WHERE (array=? AND alertid=? AND alertstate=? AND alerttime=? AND severity=? AND message=?)''',
            (array,alertid,alertstate,alerttime,severity,message))
            entry = c.fetchone()

            if entry is None: 
                c.execute(''' INSERT INTO alert (array, alertid, alertstate, alerttime, severity, message)
                VALUES(?,?,?,?,?,?)''', (array,alertid,alertstate,alerttime,severity,message))
                sql_conn.commit()

        sql_conn.close
            

DataCollection('10.248.231.68')