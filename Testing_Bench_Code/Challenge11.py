#!/usr/bin/env python

import RPi.GPIO as GPIO
import signal
import os
import time
import sys
from pirc522 import RFID
from termcolor import colored

Buzzer = 11

run = True
rdr = RFID()
util = rdr.util()
util.debug = True

textStart = '''##                         Vending Machine 1                          ##
##              Scan in order to buy the 100$ product!                ##'''

textWin = '''##                 You succesfully bought the product!                ##
##                                                                    ##'''

textFail = '''##                         NOT ENOUGH MONEY                           ##
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

def getDataFromRow(data,index):
        tmp = str(hex(data[index])[2:])
	if len(tmp) == 1:
	    tmp = "0" + tmp
	return tmp



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
        util.do_auth(40)
	
        # Read amount of money
        (error,data) = rdr.read(40)
	print data
        money = getDataFromRow(data,0) + getDataFromRow(data,1)
	print "Money (hex):"
	print money
	realMoney = int(money,16)
	print "Real money (hex):"
	print realMoney

    	os.system('clear')
	if realMoney >= 10000:	
	    fancyPrint(textWin,'green')    
	else:
            fancyPrint(textFail,'red')    
	
	# De-authenticate	
	with suppress_stdout():
            util.deauth()

        time.sleep(3)
