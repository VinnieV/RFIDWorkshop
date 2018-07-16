#!/usr/bin/env python

import RPi.GPIO as GPIO
import signal
import os
import time
import MySQLdb
import sys
from pirc522 import RFID
from termcolor import colored

Buzzer = 11
connection=MySQLdb.connect(
    host='127.0.0.1',user='workshop',passwd='DELETED',db='workshop')
cursor=connection.cursor()


run = True
rdr = RFID()
util = rdr.util()
util.debug = True

textStart = '''##                       WTF Challenge (bonus)                        ##
##              Scan your badge to verify your identity!              ##'''

textWin = '''##                           ACCESS GRANTED                           ##
##                       SQLi on RFID badge O.o                       ##'''

textFail = '''##                           ACCESS DENIED                            ##
##                           Try harder...                            ##'''

from contextlib import contextmanager
import sys, os

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout

def end_read(signal,frame):
    global run
    print("\nCtrl+C captured, ending read.")
    run = False
    rdr.cleanup()
    sys.exit()

def fancyPrint(text,color):
    print(colored("########################################################################",color))
    for i in range(0,8):
         print(colored("##                                                                    ##",color)) 
    print(colored(text,color))
    for i in range(0,8):
         print(colored("##                                                                    ##",color)) 
    print(colored("########################################################################",color))


#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(Buzzer,GPIO.OUT)
#Buzz = GPIO.PWM(Buzzer, 440)
#Buzz.start(50)
#time.sleep(0.3)
#Buzz.stop()

signal.signal(signal.SIGINT, end_read)

while run:
    os.system('clear')
    
    fancyPrint(textStart,'cyan')
    rdr.wait_for_tag()

    (error, data) = rdr.request()
    #if not error:
        #print("\nDetected: " + format(data, "02x"))

    (error, uid) = rdr.anticoll()
    if not error:
        # Clear Screen 
	os.system('clear')
	# Select tag
	util.set_tag(uid)
	# Perform authentication to block 48
	util.auth(rdr.auth_a, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
        util.do_auth(48)

	# Read block 48
        (error,data) = rdr.read(48)
	strData = ""
	for item in data:
	    strData += str(unichr(item))
	strData = strData.rstrip("\x00")

	# SQL lookup
	sql='SELECT * FROM Employees WHERE CardNumber="' + strData + '"'
	cursor.execute(sql)
	result=cursor.fetchall()
	
	# Check access
    	os.system('clear')
	if len(result) > 0:
	    fancyPrint(textWin,'green')    
	else:
            fancyPrint(textFail,'red')    
	# De-authenticate	
	with suppress_stdout():
            util.deauth()

        time.sleep(3)
