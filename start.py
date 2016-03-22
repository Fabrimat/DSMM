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
import sys
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
configVersion = config["ProgramSettings"]["Version"]
avaiableServers = config["Servers"]
checkRunningTime = config["ProgramSettings"]["CheckRunningTime"]

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
        self._checkExists()
        for command in commands:
            self._screenCommands( 'stuff "' + command + '" ' ,
                                   'eval "stuff \\015"' )

    def openConsole(self):
        self._checkExists()
        system("screen  -U -r " + self.name)

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

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Server(object):

    def __init__(self, name, initialize = False):
        self.id = config["Servers"][name]["ID"]
        self.name = name
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
            self._initialize()
            if not self.checkRunning(2):
                raise DsmmError("Unable to initialize")
        else:
            self.screen = Screen(self.name)
        return

    def checkStatus(self):
        # 0 = NOT RUNNING , 1 = INITILIZED, 2 = RUNNING
        retValue = 0
        if os.path.isfile("DSMMFiles/{0}-{1}.sdat".format(self.name,self.id)):
            tempFile = open("DSMMFiles/{0}-{1}.sdat".format(self.name,self.id), "r")
            contentFile = tempFile.read()
            tempFile.close()
            # Screen:Server:Checked:(Init=0,Start=1,Stop=2,Kill=3)
            contentFile = contentFile.split(":")
            i = 0
            for value in contentFile:
                contentFile[i]  = int(value)
                i += 1
            #contentFile = int(contentFile)
            if contentFile[0] is 1:
                if contentFile[1] is 1:
                    try:
                        self.runningInfo.status()
                        retValue =  1
                    except:
                        raise ServerError("The remote server is not responding.")
                else:
                    if self.screen.exists:
                        retValue =  2
                    else:
                        raise DsmmError("Screen should exist? Try to fix it!")
            else:
                try:
                    self.runningInfo.status()
                    raise DsmmError("Server shouldn't be running!")
                except:
                    DsmmError("There shoudn't be the file!")
        else:
            if self.screen.exists:
                try:
                    self.runningInfo.status()
                    raise DsmmError("The Screen and the Server are running without the file?")
                except:
                    raise DsmmError("The Screen is running without the file?")
            else:
                try:
                    self.runningInfo.status()
                    raise DsmmError("The Server is running without the file?")
                except:
                    retValue = 0
        return retValue

    def checkRunning(self, goal):
        print "Checking the server Status"
        print "Press Ctrl+C to interrupt."
        print "This may take a while"
        # try:
        goalCheckingTime = 0
        # dots = 0
        try:
            while goalCheckingTime < checkRunningTime*2:
                # if dots < 3:
                #     sys.stdout.write(".")
                #     sys.stdout.flush()
                # else:
                #     sys.stdout.write('\b\b\b')
                #     dots = 0
                sys.stdout.write(".")
                sys.stdout.flush()
                sleep(0.5)
                if self.checkStatus() is goal:
                    goalCheckingTime = (checkRunningTime*2)+1
                else:
                    goalCheckingTime += 1
            if goalCheckingTime is (checkRunningTime*2)+1:
                retValue = True
            else:
                retValue =  False
        except KeyboardInterrupt:
            retValue = False
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        # except KeyboardInterrupt:
        #     print "You interrupted the process."
        #     retValue = False
        # except:
        #     print "Unexpected error:", sys.exc_info()[0]
        #     raise
        return retValue

    def start(self, checkStarted = False):
        retValue = False
        preServerStatus = self.checkStatus()
        if preServerStatus is not 1:
            if preServerStatus is 0:
                self.initialize()
            if preServerStatus is 2:
                self.screen.sendCommands("cd %s".format(self.directory))
                self.screen.sendCommands('java -Xms {0} -Xmx {1} -jar {2} -p {3} -ip {4}'.format(
                    self.minRam, self.maxRam, self.fileName, self.port, self.serverIp))
                if checkStarted:
                    serverIsRunning = self.checkRunning(1)
                    tempFile = open("DSMMFiles/{0}-{1}.sdat".format(self.name,self.id), 'w+')
                    if serverIsRunning:
                        tempFile.write("1:1:1:1")
                        print "Started"
                        retValue = True
                    else:
                        tempFile.write("1:1:0:1")
                        print "Something gone wrong"
                        retValue =  False
                    tempFile.close()
        else:
            print "Server is already running."
            retValue = True
        return retValue

    def _initialize(self):
        tempFile = open("DSMMFiles/{0}-{1}.sdat".format(self.name,self.id), 'w+')
        self.screen = Screen(self.name, True)
        if self.screen.exists:
            tempFile.write("1:0:1:0")
        else:
            tempFile.write("1:0:0:0")
            DsmmError("Could not initialize!")
        tempFile.close()

    def stop(self, checkStopped = False):
        preServerStatus = self.checkStatus()
        if preServerStatus is 0:
            print "Server is not running."
        elif preServerStatus is 1:
            self.screen.sendCommands("exit")
        elif preServerStatus is 2:
            print "Stopping..."
            for value in self.stopCommands:
                self.screen.sendCommands(value)
                sleep(0.3)
            if checkStopped:
                serverIsRunning = self.checkRunning(0)
                if not serverIsRunning:
                    os.remove("DSMMFiles/{0}-{1}.sdat".format(self.name,self.id))
                    print "Stopped"
                    retValue =  True
                else:
                    tempFile = open("DSMMFiles/{0}-{1}.sdat".format(self.name,self.id), 'w+')
                    tempFile.write("0:0:0:2")
                    tempFile.close()
                    print "Something gone wrong"
                    retValue =  False
        return retValue

    def openConsole(self):
        if self.checkStatus() is not 0:
            self.screen.openConsole()
            retValue = True
        else:
            retValue = False
        return retValue


    def kill(self):
        if self.screen.exist():
            self.screen.kill()
            sleep(1.0)
            self.screen.sendCommands("exit")
            try:
                self.checkStatus()
                retValue = True
            except ServerError:
                tempFile = open("DSMMFiles/{0}-{1}.sdat".format(self.name,self.id), 'w+')
                tempFile.write("0:0:0:3")
                tempFile.close()
                print "Something gone wrong"
                retValue = False
                raise DsmmError("Error while killing.. Fix the Server sdat!")
            except DsmmError:
                os.remove("DSMMFiles/{0}-{1}.sdat".format(self.name,self.id))
                pass
        if self.screen.exist():
            retValue = False
            DsmmError("The screen was not killed?")
        return retValue

    def getInfo(self):
        print "Name:", self.name
        print "ID:", self.id
        print "Minimum RAM:", self.minRam
        print "Maximum RAM:", self.maxRam
        print "Filename:", self.fileName
        print "Directory:", self.directory
        print "Stop Commands:"
        for value in self.stopCommands:
            print " -", value
        print "IP:", self.serverIp
        print "Port:", self.port
        try:
            tempInfo = self.runningInfo.status()
            tempStatus = True
        except:
            tempStatus = False
        if tempStatus is True:
            print "Status: Online"
            print "Players:", tempStatus.players.online
        else:
            print "Status: Offline"
            if self.screen.exists:
                print "Screen: Present"
            else:
                print "Screen: Absent"
        if os.path.isfile("DSMMFiles/{0}-{1}.sdat".format(self.name,self.id)):
            tempFile = open("DSMMFiles/{0}-{1}.sdat", "r")
            contentFile = tempFile.read()
            tempFile.close()
            print "File: Present"
            print "File Content:", contentFile
        else:
            print "File: Absent"


    def restart(self):
        print "Trying to stop..."
        stopped = self.stop()
        if stopped is False:
            print "Trying to kill..."
            killed = self.kill()
        sleep(1.0)
        print "Trying to start..."
        self.start()

class DsmmError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class ServerError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def checkDir():
    if not os.chdir("DSMMFiles"):
        os.mkdir("DSMMFiles")

def clearScreen():
    call('clear', shell = True)
    return

def programInfo():
    return "DSMM v" + str(__version__) + " - Dedicaded Server Minecraft Manager by " + __author__

def optInputs():
    #The start function, choose what to do
    repeatLoop = True
    while repeatLoop is True:
        clearScreen()
        print "Please enter the inputs and don't leave them empty.\n"
        print "Options:"
        print "1 - Start"
        print "2 - Open Console"
        print "3 - Send Command"
        print "4 - Stop"
        print "5 - Restart"
        print "6 - Kill"
        print "7 - Get infos."
        print "8 - Servers status."
        print "9 - Fix"
        print "10 - Show License"
        print "11 - Exit."
        option = raw_input("\nInsert the option number: ")
        try:
            option = int(option)
            if option > 0 and option < 12:
                repeatLoop = False
            else:
                print "Error. You entered an invalid value."
                repeatLoop = True
        except ValueError:
            print "Error. You entered an invalid value."
            repeatLoop = True
    return option

def optionSwitch(option):
    if option is 1: # Start
        valueServer = chooseServer()
        tempServer = Server(valueServer, True)
        tempServer.start(True)
    elif option is 2: # Open Console
        valueServer = chooseServer()
        tempServer = Server(valueServer)
        tempServer.openConsole()
    elif option is 3: # Send Command
        valueServer = chooseServer()
        tempServer = Server(valueServer)
        tempServer.screen.sendCommands()
    elif option is 4: # Stop
        valueServer = chooseServer()
        tempServer = Server(valueServer)
        tempServer.stop()
    elif option is 5: # Restart
        valueServer = chooseServer()
        tempServer = Server(valueServer)
        tempServer.restart()
    elif option is 6: # Kill
        valueServer = chooseServer()
        tempServer = Server(valueServer)
        tempServer.kill()
    elif option is 7: # Get Info
        valueServer = chooseServer()
        tempServer = Server(valueServer)
        tempServer.getInfo()
    elif option is 8: # Status
        statusServers()
    elif option is 9: # Fixing tool
        print "The fixing tool is not implemented yet"
    elif option is 10: # License
        print "The License is not implemented yet"
    elif option is 11: # Exit
        appExit()
    else:
        raise DsmmError("Invalid value")
    raw_input("Press enter to continue...")


def loopAllServers(goal):
    retValue = 0
    for value in Server.avaiableServers:
        tempServer = Server(value)
        if tempServer.checkStatus() is not goal:
            if goal is 0:
                tempServer.stop()
            elif goal is 1:
                tempServer.start()
            elif goal is 2:
                Server(tempServer, True)
            else:
                DsmmError("Goal not valid")
    for value in avaiableServers:
        tempServer = Server(value)
        if not tempServer.checkRunning(goal):
            retValue += 1
    if reValue is not 0:
        #logging.error("{0} server are not in the correct state!".format(retValue))
        print "{0} servers are not in the correct state!".format(retValue)
    return retValue

def chooseServer(goal = None):
    repeatLoop = True
    while repeatLoop is True:
        counter = 1
        print "Choose the server:"
        for value in avaiableServers:
            print "{0} - {1}".format(counter, value)
            counter += 1
        print "{0} - All Servers".format(counter)

        option = raw_input("Insert the value: ")
        try:
            option = int(option)
            if option is counter:
                print "This option is not implemented yet."
                repeatLoop = True
            elif option > 0 and option < counter+1:
                repeatLoop = False
            else:
                repeatLoop = True
        except ValueError:
            print "Error. You entered an invalid value."
            repeatLoop = True
    if option is counter:
        if goal is not None:
            loopAllServers(goal)
        else:
            raise DsmmError("Goal cannot be None.")
    else:
        counter = 1
        for value in avaiableServers:
            if counter is option:
                retValue = value
                break
            else:
                counter += 1
    return retValue

def statusServers():
    print "Server \tStatus"
    for value in avaiableServers:
        tempServer = Server(value)
        tempStatus = tempServer.checkStatus()
        if tempStatus is 0:
            print "{0} \tOffline".format(value)
        elif tempStatus is 1:
            print "{0} \tOnline".format(value)
        elif tempStatus is 2:
            print "{0} \tInitialized".format(value)
        else:
            raise DsmmError("Status not valid.")

def appExit():
    print "\nExiting.."
    exit()

def main():
    while True:
        programInfo()
        option = optInputs()
        optionSwitch(option)

if __name__ == "__main__":
    main()
