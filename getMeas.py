#!/usr/bin/env python
import json
import sqlite3
import sys
import datetime

#first_arg = sys.argv[1]
#second_arg = sys.argv[2]

connection=0
curs=0


def AvgCalc_hour_ext(tableName,timeFrom,timeTo,overwrite=False):
    global connection,curs
    
    Log("AvgCalc_hour_ext - calculating AVGs...")
    
    try:
        connection=sqlite3.connect('/home/pi/main.db')#'/home/pi/main.db'
        curs=connection.cursor()
    
        AvgCalc_hour(tableName,timeFrom,timeTo,overwrite)
        connection.close()
        
    except Exception as inst:
        Log(type(inst))    # the exception instance
        Log(inst.args)     # arguments stored in .args
        Log(inst)
        
    Log("AvgCalc_hour_ext - calculating AVGs end")
    
    
#spocita prumery pro tabulku _hour pro casy od timeFrom do timeTo, prepise pokud je pozadavek
#pro hodiny timeFrom vcetne a timeTo ne vcetne
def AvgCalc_hour(tableName,timeFrom,timeTo,overwrite=False):
    global cursor,connection
    
    t = timeFrom
    t= t.replace(minute=0,second=0,microsecond=0)
    print("hour from "+str(t))
    
    while t<timeTo-datetime.timedelta(hours=1):
        t2 = t + datetime.timedelta(hours=1)
        
        curs.execute("SELECT COUNT(*) from {}_hour where time is ?;".format(tableName),(str(t),))
        data = curs.fetchall()
        
        exists= data[0][0]!=0
        
        if(exists and not overwrite):
            #print("skipping calculation of time for hour avg :"+str(t))
            t = t2
            continue
            
        
    
        curs.execute("SELECT * from {} where time BETWEEN ? AND ?;".format(tableName),(str(t),str(t2)))
        
        data = curs.fetchall()
        
        avg = 0
        min = 9999999
        max = 0
        validData=False
        validCnt = 0
        
        for i in range(len(data)):
            if(data[i][1]!=None):
                validData=True
                validCnt+=1
                avg += data[i][1]
                if data[i][1]<min:
                    min = data[i][1]
                if data[i][1]>max:
                    max=data[i][1]
        print(validData)
        if(validData):
            avg = avg / validCnt
            curs.execute("REPLACE INTO {}_hour (time,value,min,max) VALUES (?,?,?,?);".format(tableName),(str(t),str(avg),str(min),str(max)))
        
        if(not validData):
            print("not valid data")
            curs.execute("REPLACE INTO {}_hour (time,value,min,max) VALUES (?,null,null,null);".format(tableName),(str(t),))      
        #replace insert in hour table
        connection.commit()
        
        t = t2
        
def AvgCalc_day_ext(tableName,timeFrom,timeTo,overwrite=False):
    global connection,curs
    
    Log("AvgCalc_day_ext - calculating AVGs...")
    
    try:
        connection=sqlite3.connect('/home/pi/main.db')#'/home/pi/main.db'
        curs=connection.cursor()
        
        AvgCalc_day(tableName,timeFrom,timeTo,overwrite)
    
        connection.close()
    except Exception as inst:
        Log(type(inst))    # the exception instance
        Log(inst.args)     # arguments stored in .args
        Log(inst)
        
    Log("AvgCalc_day_ext - calculating AVGs end")
#spocita prumery pro tabulku _daypro casy timeFrom do timeTo
#pro dny timeFrom vcetne a timeTo ne vcetne
def AvgCalc_day(tableName,timeFrom,timeTo,overwrite=False):
    global curs,connection
    
    t = timeFrom
    t= t.replace(hour=0,minute=0,second=0,microsecond=0)
    print("day from "+str(t))
    
    while t<timeTo-datetime.timedelta(days=1):
        t2 = t + datetime.timedelta(days=1)
        
        curs.execute("SELECT COUNT(*) from {}_day where time is ?;".format(tableName),(str(t),))
        data = curs.fetchall()
        
        exists= data[0][0]!=0
        
        if(exists and not overwrite):
            #print("skipping calculation of time for day avg :"+str(t))
            t = t2
            continue
        
        AvgCalc_hour(tableName,t,t2,overwrite)
        
        curs.execute("SELECT * from {}_hour where time BETWEEN ? AND ?;".format(tableName),(str(t),str(t2)))
        data = curs.fetchall()
        
        avg = 0
        max = 0
        min = 99999999
        validData=False
        validCnt = 0
        
        for i in range(len(data)):
            if(data[i][1]!=None):
                validData=True
                validCnt+=1
                avg += data[i][1]
                if data[i][1]<min:
                    min = data [i][1]
                if data[i][1]>max:
                    max=data[i][1]
        
        if(validData):
            avg = avg / validCnt
            #replace insert in hour table
            curs.execute("REPLACE INTO {}_day (time,value,min,max) VALUES (?,?,?,?);".format(tableName),(str(t),str(avg),str(min),str(max)))
        
        if(not validData):
            curs.execute("REPLACE INTO {}_day (time,value,min,max) VALUES (?,null,null,null);".format(tableName),(str(t),))
            
        connection.commit()
        
        t = t2

def getLastData_hour(tableName,count,overwrite=False):
    timeTo = getTime()
    
    print(timeTo)
    diff = datetime.timedelta(hours = -count)

    timeFrom = timeTo + diff
    print(timeFrom)
    
    AvgCalc_hour(tableName,timeFrom,timeTo,overwrite)
    
    return getLastData(tableName+"_hour",count)
    

def getLastData_day(tableName,count,overwrite=False):
    timeTo = getTime()
    
    print(timeTo)
    diff = datetime.timedelta(days = -count)

    timeFrom = timeTo + diff
    print(timeFrom)
    
    AvgCalc_day(tableName,timeFrom,timeTo,overwrite)
    
    return getLastData(tableName+"_day",count)
    
    
def getLastData(tableName,count):
    global curs
    print(tableName)
    
    curs.execute("SELECT time,value,min,max FROM {} order by time desc limit ?;".format(tableName),(count,))
    
    return curs.fetchall()


def getVal(cursor,table,n):
    cursor.execute("SELECT value,time FROM {} order by time desc limit (?) ;".format(table),(n,))
    if n ==1:
        return cursor.fetchall()[0]
    else:
        return cursor.fetchall()
    
    
def getTime():
    from datetime import datetime
    return (datetime.now())

def getMetChargingDiff():
    cnt = 4#z kolika rozdilu delame prumer
    arr = getVal(curs,"m_met_u",cnt+1) 
    
    avg = 0
    for i in range(cnt):
        avg += arr[i][0] - arr[i+1][0]
        
    avg = avg/cnt
    
    return avg

#-----------------------------------------------------------for calling from web page
def getDayData(tableName,count,overwrite=False):
    print(overwrite)
    global connection,curs
    connection=sqlite3.connect('/home/pi/main.db')#'/home/pi/main.db'
    curs=connection.cursor()
    
    js=getLastData_day(tableName,count,overwrite)
    
    print(json.dumps(js))
    connection.close()

def getHourData(tableName,count,overwrite=False):
    global connection,curs
    connection=sqlite3.connect('/home/pi/main.db')#'/home/pi/main.db'
    curs=connection.cursor()
    
    js=getLastData_hour(tableName,count,overwrite)
    
    print(json.dumps(js))
    connection.close()
    
def getActualValues():
    global connection,curs
    connection=sqlite3.connect('/home/pi/main.db')
    curs=connection.cursor()

    js={'m_key_t':getVal(curs,"m_key_t",1),
        'm_key_rh':getVal(curs,"m_key_rh",1),
        'm_key_d':getVal(curs,"m_key_d",1),
        'm_key_g':getVal(curs,"m_key_g",1),
        'm_key_ga':getVal(curs,"m_key_ga",1),
        'm_met_t':getVal(curs,"m_met_t",1),
        'm_met_p':getVal(curs,"m_met_p",1),
        'm_met_u':getVal(curs,"m_met_u",1)+(getMetChargingDiff(),)
        }
    
    Log("Requested actual values")

    print(json.dumps(js))
    connection.close()

def Log(s):
    #print("LOGGED:"+str(s)) do not print, this script is callled by webpage

    dateStr=getTime().strftime('%Y-%m-%d %H:%M:%S')
    with open("getMeas.log","a") as file:
        file.write(dateStr+" >> "+str(s)+"\n")

#==============================================================================

def test():
    global connection,curs
    connection=sqlite3.connect('/home/pi/main.db')#'/home/pi/main.db'
    curs=connection.cursor()
    
    curs.execute("INSERT INTO test values ('uuu','Nazdar');")
    connection.commit()
    connection.close()
    print("hmm")
    try:
        with open('/var/www/temp','w') as f:
            f.write(str(getTime())+"   \n")
    except:
        print("Unexpected error:", sys.exc_info()[0])
        
if __name__ == "__main__":
    
    if(len(sys.argv)>1):
        if('actual' in sys.argv[1]):
            getActualValues()
        elif('day' in sys.argv[1]):
            getDayData(sys.argv[2],int(sys.argv[3]));
        elif('hour' in sys.argv[1]):
            getHourData(sys.argv[2],int(sys.argv[3]));
        elif('test' in sys.argv[1]):
            test();
        elif('recalc' in sys.argv[1]):
            getDayData(sys.argv[2],int(sys.argv[3]),True);
    else:
        #getLongValues("m_key_t",20)
        getHourData("m_key_t",30)


    