#!/usr/bin/env python
import json
import sqlite3


def getEvents(cursor):
    
    cursor.execute("SELECT * FROM events order by time desc limit 10 ;")
    data = curs.fetchall()
    print("data")
    print(data)
    
    for i in range(len(data)):
        data[i] = data[i] + (getDescription(data[i][1],data[i][2]),)
    
    return data

def getDescription(id,id2):
    if(id==0 and id2==0):return "Keyboard - zapnutí"
    if(id==1 and id2==0):return "Admin PIN"
    if(id==1 and id2==1):return "Unlock PIN"
    if(id==1 and id2==2):return "Špatný PIN"
    if(id==2 and id2==0):return "Unlock RFID"
    if(id==2 and id2==1):return "Špatný RFID"
    if(id==2 and id2==2):return "Read Error RFID"
    if(id==3 and id2==0):return "-"
    if(id==3 and id2==1):return "-"
    if(id==3 and id2==2):return "LOCK"
    if(id==3 and id2==3):return "Keyboard - výpadek napájení"
    if(id==3 and id2==4):return "Otevřeny dveře a zamknuto"
    if(id==10 and id2==0):return "Plynový alarm"
    if(id==10 and id2==2):return "Alarm dveře"
    return ""

conn=sqlite3.connect('/home/pi/main.db')

curs=conn.cursor()

evJs={}
cnt=0
for ev in getEvents(curs):
    evJs[cnt]=ev
    cnt+=1
    
print(json.dumps(evJs))

conn.close()



    