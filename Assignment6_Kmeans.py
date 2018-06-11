import csv
import pylab
import pandas as pd
import numpy as np
import uuid
import sqlite3 as sql
from numpy import vstack,array
import math
from math import sin, cos, sqrt, atan2, radians
from datetime import datetime, timedelta
from scipy.cluster.vq import *
from flask import Flask,render_template,request,send_file
import sqlite3 as sqll
############################################################################################################################

app = Flask(__name__,template_folder="static")
conn = sql.connect('Assign2.db')
df = pd.read_csv("edata.csv")
df[['date', 'time']] = df['time'].str.split('T', expand=True)
df['time'] = df['time'].str.split('.').str[0]
df.to_sql('EarthQuake1', conn, if_exists='replace', index=False)
print(df)
##############################################################################################################################

@app.route('/')
def index():
  return render_template('index.html')

####################################----------KMEANS CLUSTERS----------##################################################


mylist = []
@app.route('/kmeans', methods=['GET', 'POST'])
def main():
    attribute1 = request.form['attribute1']
    attribute2 = request.form['attribute2']
    clusters = request.form['clusters']
    K_clusters = int(clusters)
    mylist = getdata(attribute1, attribute2)
    data = []
    cdist = []
    data = array(mylist)
    cent, pts = kmeans2(data, K_clusters)
    disCluster = []

    for i in range(len(cent)):
            x1 = cent[i][0]
            y1 = cent[i][1]
            x1 = float("{0:.3f}".format(x1))
            y1 = float("{0:.3f}".format(y1))

            for j in range(i+1,len(cent)):
                dc = {}
                x2 = cent[j][0]
                y2 = cent[j][1]
                x2 = float("{0:.3f}".format(x2))
                y2 = float("{0:.3f}".format(y2))
                dist = np.sqrt(((x1-x2)*(x1-x2)) + ((y1-y2)*(y1-y2)))
                cdist.append(dist)
                dc['dist'] = "Distance between cluster " + str(i) + " and cluster " + str(j) + " is: " + str(dist)
                disCluster.append(dc)
                # print (disCluster)
                # print ("Distance between cluster " + str(i) + " and cluster " + str(j) + " is: " + str(dist))

            # clr = ([1, 1, 0.0],[0.2,1,0.2],[1,0.2,0.2],[0.3,0.3,1],[0.0,1.0,1.0],[0.6, 0.6,0.1],[1.0,0.5,0.0],[1.0,	0.0, 1.0],[0.6,	0.2, 0.2],[0.1,0.6,0.6],[0.0,0.0,0.0],[0.8,1.0,1.0],[0.70,0.50,0.50],[0.5,0.5,0.5],[0.77,0.70,0.00])
    clr=('tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan')
    colors = ([(clr)[i] for i in pts])
    pylab.scatter(data[:, 0], data[:, 1], c=colors)
    pylab.scatter(cent[:, 0], cent[:, 1], marker='o', s=400, linewidths=3, c='none')
    pylab.scatter(cent[:, 0], cent[:, 1], marker='x', s=400, linewidths=3)
    pylab.savefig("static/clusters.png")


    return render_template('index.html',disCluster=disCluster)

def getdata(attr1,attr2):
    con = sql.connect("Assign2.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT * FROM EarthQuake1')
    rows = cur.fetchall()
    for row in rows:
        pair = []
        if row[attr1] == "":
            row[attr1] = 0
        if row[attr2] == "":
            row[attr2] = 0
        x = float(row[attr1])
        y = float(row[attr2])
        pair.append(x)
        pair.append(y)
        mylist.append(pair)
    return mylist

@app.route('/show', methods=['GET', 'POST'])
def show():
  return render_template('show.html')

####################################----------KMEANS CLUSTERS----------##################################################

@app.route('/GreatMag', methods=['POST'])
def GreatMag():
    GreatMag = request.form['GreatMag']
    con = sqll.connect("Assign2.db")
    con.row_factory = sqll.Row
    cur = con.cursor()
    cur.execute('SELECT mag FROM EarthQuake1 where mag > ?', (GreatMag,))
    # cur.execute('SELECT * FROM EarthQuake')

    rows = cur.fetchall()
    count = 0
    for row in rows:
        count = count + 1
        # magnitude.append("mag:" + row[0])
    # return vehicleName
    return render_template('index.html', counter=count, rows=rows)
#########################################################################################################################

@app.route('/BetMag', methods=['POST'])
def BetMag():
    StartMag = request.form['StartMag']
    EndMag = request.form['EndMag']
    StartDate = request.form['StartDate']
    EndDate = request.form['EndDate']
    con = sqll.connect("Assign2.db")
    con.row_factory = sqll.Row
    cur = con.cursor()
    cur.execute('SELECT date,mag FROM EarthQuake1 where mag between ? and ? AND date between date(?)and date(?)',
                (StartMag, EndMag, StartDate, EndDate))
    # cur.execute('SELECT time FROM EarthQuake where mag ? AND time LIKE \''+StartDate+'%\'',(StartMag,))
    rows = cur.fetchall()
    return render_template('index.html', rows=rows)

########################################################################################################################
@app.route('/DayMag', methods=['POST'])
def DayMag():
    DayMag = request.form['DayMag']
    con = sqll.connect("Assign2.db")
    con.row_factory = sqll.Row
    cur1 = con.cursor()
    cur2= con.cursor()
    cur1.execute('SELECT mag FROM EarthQuake1 where mag > ? and time between time(?)and time(?)',
                (DayMag, '23:00:00', '23:59:59'))
    rows1 = cur1.fetchall()
    cur2.execute('SELECT mag FROM EarthQuake1 where mag > ? and time between time(?)and time(?)',
                [DayMag, '00:00:00', '00:59:59'])
    rows2 = cur2.fetchall()
    count1 = 0
    count2 = 0

    for row in rows1:
        count1 = count1 + 1
    for row in rows2:
        count2 = count2 + 1


    if count1 > count2:
        msg = str(count1)+"Earthquake occurs mostly at night"
        # msg= "count1"+str(count1)
    else:
        msg = str(count2)+" Earthquakes occurs mostly during day"
        # msg = "count2"+str(count2)

    return render_template('index.html', msg=msg)
########################################################################################################################

@app.route('/radius', methods=['POST'])
def radius():
        LatCoord = request.form['LatCoord']
        LongCoord = request.form['LongCoord']
        # LatCoord_rad=deg2rad(LatCoord)
        # LongCoord_rad=deg2rad(LongCoord)
        Dist = request.form['Dist']
        con = sqll.connect("Assign2.db")
        con.row_factory = sqll.Row
        cur = con.cursor()
        cur.execute('SELECT * FROM EarthQuake1')
        rows = cur.fetchall()
        ct = 0
        for row in rows:
            pair = []
            x = float(row["latitude"])
            y = float(row["longitude"])
            R = 6373.0

            lat1 = radians(float(LatCoord))
            lon1 = radians(float(LongCoord))
            lat2 = radians(x)
            lon2 = radians(y)

            dlon = lon2 - lon1
            dlat = lat2 - lat1

            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))

            distance = R * c
            if distance <= float(Dist):
                ct += 1

        # rows = cur.fetchall()
        return render_template('index.html', count=ct)
#######################################################################################################################
@app.route('/PrevDays', methods=['POST'])
def PrevDays():
    PrevDays = request.form['PrevDays']
    d = datetime.today() - timedelta(days=4)
    con = sqll.connect("Assign2.db")
    con.row_factory = sqll.Row
    cur = con.cursor()
    cur.execute('SELECT mag FROM EarthQuake1 where mag > ? and date between ? and ?', (PrevDays,d,datetime.today()))

    rows = cur.fetchall()

    return render_template('index.html',rows=rows)
##############################################################################################################################
if __name__ == "__main__":
    app.run(debug=True,port=6010)