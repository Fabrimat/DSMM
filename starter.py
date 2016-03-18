#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
	DSMM v2.0 - Dedicaded Server Minecraft Manager
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
            raise ScreenNotFoundError(message)

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

class ScreenNotFoundError(Exception):
    @Override
    def __init__(self, value):
        self.value = value
    @Override
    def __str__(self):
        return repr(self.value)

class Server(object):

    configVersion = config["ConfigInfo"]["Version"]

    avaiableServers = config["Servers"]

    def __init__(self, name, initialize = True):
        self.id = config["Servers"][name]["ID"]
        self.name = config["Servers"][name]["Name"]
        self.minRam = config["Servers"][name]["MinRAM"]
        self.maxRam = config["Servers"][name]["MaxRAM"]
        self.fileName = config["Servers"][name]["FileName"]
        self.directory = config["Servers"][name]["Directory"]
        self.stopCommands = config["Servers"][name]["StopCommands"]
        self.description = config["Servers"][name]["Description"]
        self.serverIp = config["Servers"][name]["IP"]
        self.port = config["Servers"][name]["Port"]
        self.runningInfo = serverStatus.lookup("{0}:{1}".format(self.serverIp,self.port))
        if initialize:
            self.screen = self._initialize
        else:
            self.screen = None
        return

    def checkStatus(self):
        # 0 = NOT RUNNING , 1 = INITILIZED, 2 = RUNNING
        retValue = 0
        if os.path.isfile("DSMMFiles/{0}{1}.sdat".format(self.name,self.id)):
            tempFile = os.open("DSMMFiles/{0}{1}.sdat", "r")
            contentFile = tempFile.read()
            tempFile.close()
            # Screen:Server:Checked
            contentFile.split(":")
            contentFile = int(contentFile)
            if contentFile[0] is 1:
                if contentFile[1] is 1:
                    try:
                        self.runningInfo.status()
                        retValue =  2
                    except
                        raise ServerError("The remote server is not responding.")
                else:
                    if self.screen.exist():
                        retValue =  1
                    else:
                        raise DsmmError("Screen should exist? Try to fix it!")
            else:
                try:
                    self.runningInfo.status()
                    raise DsmmError("Server shouldn't be running!")
                except
                    DsmmError("There shoudn't be the file!")
        else:
            if self.screen.exist():
                try:
                    self.runningInfo.status()
                    raise DsmmError("The Screen and the Server are running without the file?")
                except
                    raise DsmmError("The Screen is running without the file?")
            else:
                try:
                    self.runningInfo.status()
                    raise DsmmError("The Server is running without the file?")
                except
                    retValue = 0
        return retValue

    def _checkRunning(self, goal):
        startCheckingTime = 0
        while serverStarted < 120:
            sleep(0.5)
            if self.checkStatus is goal:
                startCheckingTime = 121
            startCheckingTime += 1
        if startCheckingTime is 121:
            retValue = True
        else:
            retValue =  False
        return retValue

    def start(self, checkStarted = False):
        preServerStatus = self.checkStatus
        if preServerStatus == 3:
            self.screen.send_commands("cd %s".format(self.directory))
        	self.screen.send_commands('java -Xms {0} -Xmx {1} -jar {2} -p {3} -ip {4}'.format(
                self.minRam, self.maxRam, self.fileName, self.port, self.serverIp))
            if checkStarted:
                serverIsRunning = self._checkRunning(1)
                tempFile = os.open("DSMMFiles/{0}{1}.sdat", 'w+'.format(self.name,self.id))
                if serverIsRunning:
                    tempFile.write("1:1:1")
                    print "Started"
                else:
                    tempFile.write("1:1:0")
                    print "Something gone wrong"
                tempFile.close()

    def _initialize(self):
        tempFile = os.open("DSMMFiles/{0}{1}.sdat", 'w+'.format(self.name,self.id))
        serverScreen = Screen(self.name, True)
        if serverScreen.exist:
            tempFile.write("1:0:1")
        else:
            DsmmError("Could not initialize!")
        tempFile.close()
        return serverScreen

    def stop(self, checkStopped = False):
        preServerStatus = self.checkStatus
        if preServerStatus is 0:
            print "Server is not running."
        else if preServerStatus is 1:
            self.screen.sendCommands("exit")
        else if preServerStatus is 2:
            print "Stopping..."
            for value in self.stopCommands:
                self.screen.sendCommands(value)
                sleep(0.3)
            if checkStopped:
                serverIsRunning = self._checkRunning(0)
                if not serverIsRunning:
                    os.remove("DSMMFiles/{0}{1}.sdat".format(self.name,self.id))
                    self.screen = None
                    print "Stopped"
                else:
                    tempFile = os.open("DSMMFiles/{0}{1}.sdat", 'w+'.format(self.name,self.id))
                    tempFile.write("0:0:0")
                    tempFile.close()
                    print "Something gone wrong"

def spinningCursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

def printCursor():
    spinner = spinningCursor()
    while True:
        stdout.write(spinner.next())
        stdout.flush()
        sleep(0.1)
        stdout.write('\b')

def checkDir():
    if not os.chdir("DSMMFiles"):
        os.mkdir("DSMMFiles")

def clearScreen():
	call('clear', shell = True)
	return

def programInfo():
	print "DSMM v" + str(__version__) + " - Dedicaded Server Minecraft Manager by " + __author__
	return "Please enter the inputs and don't leave them empty."

def optInputs():
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
        print "9 - Fix"
    	print "10 - Exit."
    	Option = raw_input("\nInsert the option number: ")
    	try:
    		Option = int(Option)
            repeatLoop = False
    	except:
    		print "Error. You entered an invalid value."
            repeatLoop = True
	return Option

# def startAllServers():
#     for value in avaiableServers:
#         if selServer is None:
#             if os.path.isfile("DSMMFiles/%s%i.sdat".format(value.name,value.id)):
#                 try:
#                     value.runningInfo.ping()
#                     raise ServerError("Server is already running")
#                 except
#                     raise ServerError("Server seems died.")
#             loopServer = Server(value)
#             start(loopServer.name)
#         else:
#             raise DsmmError("selServer must be None.")
