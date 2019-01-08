import paramiko
import sqlite3
from datetime import datetime
import time


class DataCollection:
    def __init__(self,ip):
        # Connect to array using private key
        #paramiko.util.log_to_file('/home/ed/Dev/ssh.log')
        key = paramiko.RSAKey.from_private_key_file('/home/ed/.ssh/id_rsa')
        conn = paramiko.SSHClient()
        conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conn.connect(hostname = ip, username = 'metrics', pkey = key)
#        now = datetime.now().strftime("%d-%m-%Y %H:%M")
        sql_conn = sqlite3.connect('/home/ed/Dev/dashboard.db', timeout=10)
        c = sql_conn.cursor()

        # Run command
        stdin, stdout, stderr = conn.exec_command('showsys -d')

        # Collect data from output
        while True:
            line = stdout.readline()
            if line != '':
                line = [splits for splits in line.split(':')]
                line = list(filter(None,line))
                if line[0].startswith('---'):
                    continue
                if line[0].startswith('System Name'): array=line[1].strip()
                if line[0].startswith('System Model'): model=line[1].strip()
                if line[0].startswith('Serial Number'): serial=line[1].strip()
                if line[0].startswith('Total Capacity'): totalcap=line[1]
                if line[0].startswith('Allocated Capacity'): alloccap=line[1]
                if line[0].startswith('Free Capacity'): freecap=line[1]
                if line[0].startswith('Failed Capacity'): failedcap=line[1]
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

        # Run command
        stdin, stdout, stderr = conn.exec_command('statcpu -t -iter 1')

        # Collect data from output
        while True:
            line = stdout.readline()
            if line != '':
                line = [splits for splits in line.split(' ')]
                line = list(filter(None,line))
                if line[0].startswith('node'):
                    continue
                if line[0].startswith('Id'):
                    continue
                if len(line) < 3:
                    continue
                cpunode = line[0]
                cpuidle = line[3]

            else:
                break

            c.execute(''' INSERT INTO cpu (array,cpunode,cpuidle,time)
            VALUES(?,?,?,?)''', (array,cpunode,cpuidle,now))
            sql_conn.commit()

        # Run command
        stdin, stdout, stderr = conn.exec_command('statvv -rw -iter 1')

        # Collect data from output
        while True:
            line = stdout.readline()
            if line != '':
                line = [splits for splits in line.split(' ')]
                line = list(filter(None,line))
                if len(line) > 11 or len(line) == 1:
                    continue
                if line[0].startswith('---'):
                    continue
                if line[1] == 'r':
                    arrayiopsread = line[2]
                    arraysvtread = line[6]

                if line[1] == 'w':
                    arrayiopswrite = line[2]
                    arraysvtwrite = line[6]

                if line[1] == 't':
                    arrayiopstotal = line[2]
                    arraysvttotal = line[6]
            else:
                break
        c.execute(''' INSERT INTO array_svt_iops (array,arrayiopsread,arrayiopswrite, arrayiopstotal, arraysvtread,arraysvtwrite, arraysvttotal, time)
        VALUES(?,?,?,?,?,?,?,?)''', (array,arrayiopsread,arrayiopswrite,arrayiopstotal,arraysvtread,arraysvtwrite,arraysvttotal,now))
        sql_conn.commit()

        # Run command
        stdin, stdout, stderr = conn.exec_command('statvv -d 10 -rw -iter 1')

        # Collect data from output
        while True:
            line = stdout.readline()
            if line != '':
                line = [splits for splits in line.split(' ')]
                line = list(filter(None,line))
                if len(line) != 13:
                    continue
                if line[0].startswith('VVname'):
                    continue
                lunname = line[0]
                lunrwt = line[1]
                luniops = line[4]
                lunsvt = line[9]

            else:
                break

            c.execute(''' INSERT INTO lun_svt_iops (array,lunname,lunrwt,luniops,lunsvt,time)
            VALUES(?,?,?,?,?,?)''', (array,lunname,lunrwt,luniops,lunsvt,now))
            sql_conn.commit()

        sql_conn.close
            
array_list = ['172.19.241.22', '172.19.225.61', '10.251.38.1',
            '10.251.38.5', '10.1.63.130', '10.1.63.132', '10.248.231.23',
            '10.248.231.24', '10.248.231.68', '142.71.40.232']

start_time = time.time()
now = datetime.now().strftime("%d-%m-%Y %H:%M")

for ip in array_list:
    DataCollection(ip)
f1=open('./runtime.txt', 'a+')
print(now, "--- datacollection: %s seconds ---" % (time.time() - start_time), file=f1)