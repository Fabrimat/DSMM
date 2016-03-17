#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
	DSMM v0.8 - Dedicaded Server Minecraft Manager
	Author: Fabrimat
	Repository: https://github.com/Fabrimat/DSMM
'''

__author__ = "Fabrimat"
__license__ = "GPL"
__version__ = "2.0"
__maintainer__ = "Fabrimat"
__email__ = "lr.fabrizio@gmail.com"
__status__ = "Development"

from sys import exit as sExit
from os import name as osName
#import logging
if osName != "posix":
	exit("\nOS not supported.\n")
	#logging.error("%s not supported.", os.name)
from subprocess import call
from threading import Thread as thread
from os import system
import os.path
from time import sleep
try:
    from commands import getoutput as getOutput
except:
    from subprocess import getoutput as getOutput

# Third party
import yaml
from mcstatus import MinecraftServer as serverStatus

#Import the config
config = yaml.load(open('config.yml', 'r'))

# Console colors
W = '\033[0m'    # (normal)
R = '\033[31m'   # red
G = '\033[32m'   # green
O = '\033[33m'   # orange
B = '\033[34m'   # blue
P = '\033[35m'   # purple
C = '\033[36m'   # cyan
GR = '\033[37m'  # gray
T = '\033[93m'   # tan

def list_screens():
    """List all the existing screens and build a Screen instance for each
    """
    return [
                Screen(".".join(l.split(".")[1:]).split("\t")[0])
                for l in getoutput("screen -ls | grep -P '\t'").split('\n')
                if ".".join(l.split(".")[1:]).split("\t")[0]
            ]

class Screen(object):

    def __init__(self, name, initialize = False):
        self.name = name
        self._id = None
        self._status = None
        self.logs=None
        if initialize:
            self.initialize()

    @property
    def id(self):
        if not self._id:
            self._setScreenInfos()
        return self._id

    @property
    def status(self):
        self._setScreenInfos()
        return self._status

    @property
    def exists(self):
        lines = getOutput("screen -ls | grep " + self.name).split('\n')
        return self.name in [".".join(l.split(".")[1:]).split("\t")[0]
                             for l in lines]

    def initialize(self):
        """initialize a screen, if does not exists yet"""
        if not self.exists:
            self._id = None
            thread(target=self._delayedDetach).start()
            system('screen -UR ' + self.name)

    def interrupt(self):
        """Insert CTRL+C in the screen session"""
        self._screenCommands("eval \"stuff \\003\"")

    def kill(self):
        self._screenCommands('quit')

    def detach(self):
        self._checkExists()
        system("screen -d " + self.name)

    def sendCommands(self, *commands):
        self._check_exists()
        for command in commands:
            self._screenCommands( 'stuff "' + command + '" ' ,
                                   'eval "stuff \\015"' )

    def openConsole(self):
        self._checkExists()
        system("screen -r " + self.name)

    def addUserAccess(self, unixUserName):
        self._screenCommands('multiuser on', 'acladd ' + unixUserName)

    def _screenCommands(self, *commands):
        self._checkExists()
        for command in commands:
            system('screen -x ' + self.name + ' -X ' + command)
            sleep(0.02)

    def _checkExists(self, message = "Error code: 404"):
        if not self.exists:
            raise screenNotFoundError(message)

    def _setScreenInfos(self):
        """set the screen information related parameters"""
        if self.exists:
            infos = getoutput("screen -ls | grep %s" % self.name).split('\t')[1:]
            self._id = infos[0].split('.')[0]
            if len(infos)==3:
                self._date = infos[1][1:-1]
                self._status = infos[2][1:-1]
            else:
                self._status = infos[1][1:-1]

    def _delayedDetach(self):
        sleep(0.5)
        self.detach()

    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self.name)

class screenNotFoundError(Exception):
    pass


class Server(object):

    configVersion =

    avaiableServers =

    def __init__(self, name, initialize = True):
        self.id = 
        self.name =
        self.ram =
        self.fileName =
        self.directory =
        self.stopCommand =
        self.description =
        self.serverIp =
        self.port =
        self.runningInfo = serverStatus.lookup("%s:%i".format(self.serverIp,self.port))
        if initialize:
            self._initialize
        return

    def checkStart(self, all = False, selServer = None):
        if all:
            for value in avaiableServers:
                if os.path.isfile("DSMMFiles/%s.sdat"):
                    try:
                        value.runningInfo.ping()
                    except 
                        raise serverError("Server is already running.")
                loopServer = Server(value)
                _start(loopServer.name)
        else:
            if selServer not None:
                selServer = Server(selServer)
                selServer._start
            else:
                raise dsmmError("selServer cannot be None.")

    def _start(self):




def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

def print_cursor():
    spinner = spinning_cursor()
    while True:
        stdout.write(spinner.next())
        stdout.flush()
        sleep(0.1)
        stdout.write('\b')

def ClearScreen():
	call('clear', shell = True)
	return

def ProgramInfo():
	print "DSMM v" + str(__version__) + " - Dedicaded Server Minecraft Manager by " + __author__
	return "Please enter the inputs and don't leave them empty."

def OptInputs():
	#The start function, choose what to do
    repeatLoop = True
    while errorLoop == True
    	ClearScreen()
    	print ProgramInfo(),"\n"
    	print "Options:"
    	print "1 - Start"
    	print "2 - Open Console"
    	print "3 - Send Command"
    	print "4 - Stop"
    	print "5 - Restart"
    	print "6 - Kill"
    	print "7 - Get infos."
    	print "8 - List all running servers."
    	print "9 - Exit."
    	Option = raw_input("\nInsert the option number: ")
    	try:
    		Option = int(Option)
            repeatLoop = False
    	except:
    		print "Error. You entered an invalid value."
            repeatLoop = True
	return Option
