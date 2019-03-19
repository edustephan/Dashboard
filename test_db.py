import sqlite3
import time
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from dateutil import parser
from matplotlib import style
style.use('fivethirtyeight')


conn = sqlite3.connect('dashboard.db')
c = conn.cursor()



def read_from_db():
    c.execute('select arrayiopsread, time from array_svt_iops WHERE array = "RCH3PAR01"')
    data = c.fetchall()

    dates = []
    values = []

    for row in data:
        dates.append(parser.parse(row[1]))
        values.append(row[0])

    plt.plot_date(dates,values,'-')
    plt.show()

read_from_db()
c.close
conn.close()