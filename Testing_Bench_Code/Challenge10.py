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

textStart = '''##                            Magic Mifare                            ##
##              Scan your badge to verify your identity!              ##'''

textWin = '''##                           ACCESS GRANTED                           ##
##                     Welcome employee AB62FC19!                     ##'''

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


GPIO.setmode(GPIO.BOARD)
GPIO.setup(Buzzer,GPIO.OUT)
Buzz = GPIO.PWM(Buzzer, 440)
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
        os.system('clear')
	if str(uid[0]) == "171" and str(uid[1]) == "98" and str(uid[2]) == "252" and str(uid[3]) == "25":
	    fancyPrint(textWin,'green')    
	    Buzz = GPIO.PWM(Buzzer, 500)
	    Buzz.start(50)
	    time.sleep(0.3)
	    Buzz.stop()
	else:
            fancyPrint(textFail,'red')    
	    Buzz = GPIO.PWM(Buzzer, 100)
	    Buzz.start(50)
	    time.sleep(0.3)
	    Buzz.stop()
	
	with suppress_stdout():
            util.deauth()

        time.sleep(3)
