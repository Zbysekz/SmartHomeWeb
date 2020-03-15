#!/usr/bin/env python
import json
import sqlite3

import sys

#first_arg = sys.argv[1]
#second_arg = sys.argv[2]


def getVal(cursor,table,n):
    cursor.execute("SELECT value FROM {} order by time desc limit (?) ;".format(table),(n,))
    if n ==1:
        return cursor.fetchall()[0][0]
    else:
        return cursor.fetchall()
    

def getState():
    conn=sqlite3.connect('/home/pi/main.db')

    curs=conn.cursor()
    curs.execute("SELECT * FROM state;")
    
    a = curs.fetchall()[0]
    
    print(a)
    
    n = 0#normal
    
    if a[0]==1:
        n=1
    if a[1]==1:
        n=2
        
    js={'state':n}

    print(json.dumps(js))
    conn.close()

if __name__ == "__main__":
    
    getState()
    

    