import paramiko
import sqlite3
from datetime import datetime
import time


class DailyDataCollection:
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
            else:
                break

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
                if(line[1]).startswith('total'):
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


            # Check if the row exists before insert
            # Need to decide if we need to keep all entries or just the last one. 
#            c.execute(''' SELECT * FROM luns WHERE (array=? AND lunname=? AND lunsize=? AND lunused_perc=? AND luncompaction=? AND time=?)''',
#            (array,lunname,lunsize,lunused_perc,luncompaction,now))
#            entry = c.fetchone()

#            if entry is None: 
            c.execute(''' INSERT INTO luns (array, lunname, luncpg, lunsize, lunused_perc,luncompaction,time)
            VALUES(?,?,?,?,?,?,?)''', (array,lunname,luncpg,lunsize,lunused_perc,luncompaction,now))
            sql_conn.commit()


        # Run command
        stdin, stdout, stderr = conn.exec_command('showpd')

        # Collect data from output
        while True:
            line = stdout.readline()
            if line != '':
                line = [splits for splits in line.split(' ')]
                line = list(filter(None,line))
                if line[0].startswith('---'):
                    continue
                if line[0].startswith('Id'):
                    continue
                if len(line) < 6:
                    continue
                pdid = line[0]
                pdcagepos = line[1]
                pdtype = line[2]
                pdrpm =line[3]
                pdstate = line[4]
                pdtotal = line[5]
                pdfree = line[6]

            else:
                break

            # Check if the row exists before insert
            # Need to decide if we need to keep all entries or just the last one. 
#            c.execute(''' SELECT * FROM pd WHERE (array=? AND pdid=? AND pdcagepos=? AND pdtype=? AND pdrpm=? AND pdstate=? AND pdtotal=? AND pdfree=? and time=?)''',
#            (array,pdid,pdcagepos,pdtype,pdrpm,pdstate,pdtotal,pdfree,now))
#            entry = c.fetchone()

#            if entry is None: 
            c.execute(''' INSERT INTO pd (array,pdid,pdcagepos,pdtype,pdrpm,pdstate,pdtotal,pdfree,time)
            VALUES(?,?,?,?,?,?,?,?,?)''', (array,pdid,pdcagepos,pdtype,pdrpm,pdstate,pdtotal,pdfree,now))
            sql_conn.commit()


        # Run command
        stdin, stdout, stderr = conn.exec_command('showvlun -a -showcols VVName,HostName')

        # Collect data from output
        while True:
            line = stdout.readline()
            if line != '':
                line = [splits for splits in line.split(' ')]
                line = list(filter(None,line))
                if line[0].startswith('VVName') or line[0].startswith('HostName') or line[0].startswith('total') or len(line) < 2:
                    continue
                vvname = line[0]
                vvhostname = line[1]

            else:
                break
            c.execute(''' SELECT * FROM vlun WHERE (array=? AND vvname=? AND vvhostname=?)''',
            (array,vvname, vvhostname))
            entry = c.fetchone()

            if entry is None: 
                c.execute(''' INSERT INTO vlun (array,vvname,vvhostname)
                VALUES(?,?,?)''', (array,vvname,vvhostname))
                sql_conn.commit()

        sql_conn.close
            

array_list = ['172.19.241.22', '172.19.225.61', '10.251.38.1',
            '10.251.38.5', '10.1.63.130', '10.1.63.132', '10.248.231.23',
            '10.248.231.24', '10.248.231.68', '142.71.40.232']

start_time = time.time()
now = datetime.now().strftime("%d-%m-%Y %H:%M")


for ip in array_list:
    DailyDataCollection(ip)

f1=open('/home/ed/Dev/runtime.txt', 'a+')
print(now, "--- dailydatacollection: %s seconds ---" % (time.time() - start_time), file=f1)