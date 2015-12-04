#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
'''
	DSMM v0.8 - Dedicaded Server Minecraft Manager
	Author: Fabrimat
	Repository: https://github.com/Fabrimat/DSMM
'''

__author__ = "Fabrimat"
__license__ = "GPL"
__version__ = "0.8"
__maintainer__ = "Fabrimat"
__email__ = "lr.fabrizio@gmail.com"
__status__ = "Development"

from sys import exit
from os import name
#import logging
if name != "posix":
	exit("\nOS not supported.\n")
	#logging.error("%s not supported.", os.name)
from subprocess import call
from threading import Thread
from os import system
from time import sleep
try:
    from commands import getoutput
except:
    from subprocess import getoutput

# Third party
import yaml

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

# Screenutils library
# Repository: https://github.com/Christophe31/screenutils

def list_screens():
    """List all the existing screens and build a Screen instance for each
    """
    return [
                Screen(".".join(l.split(".")[1:]).split("\t")[0])
                for l in getoutput("screen -ls | grep -P '\t'").split('\n')
                if ".".join(l.split(".")[1:]).split("\t")[0]
            ]

class Screen(object):

    def __init__(self, name, initialize=False):
        self.name = name
        self._id = None
        self._status = None
        self.logs=None
        if initialize:
            self.initialize()

    @property
    def id(self):
        """return the identifier of the screen as string"""
        if not self._id:
            self._set_screen_infos()
        return self._id

    @property
    def status(self):
        """return the status of the screen as string"""
        self._set_screen_infos()
        return self._status

    @property
    def exists(self):
        """Tell if the screen session exists or not."""
        # Parse the screen -ls call, to find if the screen exists or not.
        # The screen -ls | grep name returns something like that:
        #  "	28062.G.Terminal	(Detached)"
        lines = getoutput("screen -ls | grep " + self.name).split('\n')
        return self.name in [".".join(l.split(".")[1:]).split("\t")[0]
                             for l in lines]

    def initialize(self):
        """initialize a screen, if does not exists yet"""
        if not self.exists:
            self._id=None
            # Detach the screen once attached, on a new tread.
            Thread(target=self._delayed_detach).start()
            # support Unicode (-U),
            # attach to a new/existing named screen (-R).
            system('screen -UR ' + self.name)

    def interrupt(self):
        """Insert CTRL+C in the screen session"""
        self._screen_commands("eval \"stuff \\003\"")

    def kill(self):
        """Kill the screen applications then close the screen"""
        self._screen_commands('quit')

    def detach(self):
        """detach the screen"""
        self._check_exists()
        system("screen -d " + self.name)

    def send_commands(self, *commands):
        """send commands to the active gnu-screen"""
        self._check_exists()
        for command in commands:
            self._screen_commands( 'stuff "' + command + '" ' ,
                                   'eval "stuff \\015"' )

    def add_user_access(self, unix_user_name):
        """allow to share your session with an other unix user"""
        self._screen_commands('multiuser on', 'acladd ' + unix_user_name)

    def _screen_commands(self, *commands):
        """allow to insert generic screen specific commands
        a glossary of the existing screen command in `man screen`"""
        self._check_exists()
        for command in commands:
            system('screen -x ' + self.name + ' -X ' + command)
            sleep(0.02)

    def _check_exists(self, message="Error code: 404"):
        """check whereas the screen exist. if not, raise an exception"""
        if not self.exists:
            raise ScreenNotFoundError(message)

    def _set_screen_infos(self):
        """set the screen information related parameters"""
        if self.exists:
            infos = getoutput("screen -ls | grep %s" % self.name).split('\t')[1:]
            self._id = infos[0].split('.')[0]
            if len(infos)==3:
                self._date = infos[1][1:-1]
                self._status = infos[2][1:-1]
            else:
                self._status = infos[1][1:-1]

    def _delayed_detach(self):
        sleep(0.5)
        self.detach()

    def __repr__(self):
        return "<%s '%s'>" % (self.__class__.__name__, self.name)

class ScreenNotFoundError(Exception):
    """raised when the screen does not exists"""

def ClearScreen():
	call('clear', shell = True)
	return

def ProgramInfo():
	print "DSMM v" + __version__ + " - Dedicaded Server Minecraft Manager by " + __author__
	return "Please enter the inputs and don't leave them empty."

def OptInputs():
	#The start function, choose what to do
	ClearScreen()
	print ProgramInfo(),"\n"
	print "Options:"
	print "1 - Start server."
	print "2 - Open a server console."
	print "3 - Send a command to a server."
	print "4 - Stop server."
	print "5 - Restart a server."
	print "6 - Kill a server."
	print "7 - Get server infos."
	print "8 - List all running servers."
	print "9 - Exit."
	Option = raw_input("\nInsert the option number: ")
	try:
		Option = int(Option)
	except:
		AppExit("Error. You entered an invalid value.")
	return Option

def ServerList():
	print "The avaiable server are:"
	for data in config["servers"]:
		print data
	return

def ErrorCheck(Option):
	#Check if the option is valid
	if Option < 1 and Option > 9:
		exit("Invalid Option")
	return


def InputServerName():
	#Insert the Server Name and validate it.
	InvName = True
	PrintHelp = False
	ServerName = "NULL"
	ScreenName = "NULL"
	while InvName == True:  # Loop for QuestClose
		ValidName = False
		ServerName = raw_input("Insert the server name: ")
		print ""
		if ServerName == "help" or ServerName == "Help":
			ServerList()
			PrintHelp = True
			InvName = True
		else:
			for data in config["Servers"]:
				if ServerName == data:  # Check if servername is valid
					ScreenName = Screen(ServerName)
					InvName = False
					break
				else:
					InvName = True
		if InvName == True and PrintHelp == False:
			print 'Invalid name. Type "help" for the list.'
	return ServerName

def GetServerInfo(ServerName):
	Name = config["Servers"][ServerName]["Name"]
	ScreenName = Screen(Name)
	Ram = config["Servers"][ServerName]["Ram"]
	FileName = config["Servers"][ServerName]["File_Name"]
	Directory = config["Servers"][ServerName]["Directory"]
	StopCommand = config["Servers"][ServerName]["Stop_Command"]
	Description = config["Servers"][ServerName]["Description"]
	ServerPort = config["Servers"][ServerName]["Port"]
	ServerIPListen = config["Servers"][ServerName]["Server_Ip"]
	return ServerName, ScreenName, Name, Ram, FileName, Directory, StopCommand, Description, ServerPort, ServerIPListen

def OptChoose(Option):
	if Option == 1:
		ServerName = InputServerName()
		ServerInfo = GetServerInfo(ServerName)
		ServerStart(ServerInfo[0], ServerInfo[1], ServerInfo[2], ServerInfo[3], ServerInfo[4], ServerInfo[5], ServerInfo[6], ServerInfo[8],  ServerInfo[9])
	elif Option == 2:
		ServerName = InputServerName()
		ServerInfo = GetServerInfo(ServerName)
		ServerConsole(ServerInfo[1], ServerInfo[2])
	elif Option == 3:
		ServerName = InputServerName()
		ServerInfo = GetServerInfo(ServerName)
		ServerCommand(ServerInfo[0], ServerInfo[1], ServerInfo[2], ServerInfo[3], ServerInfo[4], ServerInfo[5], ServerInfo[6], ServerInfo[8],  ServerInfo[9])
	elif Option == 4:
		ServerName = InputServerName()
		ServerInfo = GetServerInfo(ServerName)
		ServerStop(ServerInfo[0], ServerInfo[1], ServerInfo[2], ServerInfo[3], ServerInfo[4], ServerInfo[5], ServerInfo[6], True)
	elif Option == 5:
		ServerName = InputServerName()
		ServerInfo = GetServerInfo(ServerName)
		ServerRestart(ServerInfo[0], ServerInfo[1], ServerInfo[2], ServerInfo[3], ServerInfo[4], ServerInfo[5], ServerInfo[6], ServerInfo[8],  ServerInfo[9])
	elif Option == 6:
		ServerName = InputServerName()
		ServerInfo = GetServerInfo(ServerName)
		ServerKill(ServerInfo[0], ServerInfo[1], ServerInfo[2], ServerInfo[3], ServerInfo[4], ServerInfo[5])
	elif Option == 7:
		ServerName = InputServerName()
		ServerInfo = GetServerInfo(ServerName)
		SayHello(ServerInfo[0], ServerInfo[1], ServerInfo[2], ServerInfo[3], ServerInfo[4], ServerInfo[5],ServerInfo[6],ServerInfo[7], ServerInfo[8],  ServerInfo[9])
	elif Option == 8:
		ActServerList()
	elif Option == 9:
		AppExit()
	return

def ServerStart(ServerName, ScreenName, Name, Ram, FileName, Directory, StopCommand, ServerPort, ServerIPListen):
	if ScreenName.exists:
		while True: #Loop for QuestClose
			QuestClose=raw_input("The Screen is already active, would you like to stop it? (y/n) - ")
			if QuestClose == "y":
				ServerStop(ServerName, ScreenName, Name, Ram, FileName, Directory, StopCommand, False)
				break
			elif QuestClose == "n":
				AppExit()
			else:
				print "Invalid input."
	ScreenName = Screen(Name, True)
	ScreenName.send_commands("cd " + Directory)
	ScreenName.send_commands('java -Xmx' + Ram + ' -Xms' + Ram + ' -jar ' + FileName + ' -p ' + str(ServerPort) )
	ClearScreen()
	print"\nServer successfully started!\n"
	sleep(1)
	AppExit()
	return

def ServerConsole(ScreenName, Name):
	if ScreenName.exists:
		ScreenName.detach()
		system('screen -U -r ' + Name)
		exit()
	else:
		print "The Screen is not running. Check if it's running with this user, otherwise start it."
		raw_input("Press enter to continue...")
		AppExit()
	return

def ServerCommand(ServerName, ScreenName, Name, Ram, FileName, Directory, StopCommand, ServerPort, ServerIPListen):
	if not ScreenName.exists:
		print "The Screen is not running. Check if it's running with this user, otherwise start it."
		raw_input("Press enter to continue...")
		AppExit()
	#AppExit("Server Command to complete.")
	SendCommand = raw_input("Insert the commnd to send: ")
	ScreenName.send_commands(SendCommand)
	sleep(0.4)
	QuestOpen = raw_input("Command sent. Would you like to open the screen? (y/n) - ")
	if QuestOpen == "y":
		ServerConsole(ScreenName, Name)
	elif QuestOpen == "n":
		AppExit()
	else:
		AppExit("Error. You entered an invalid value.")
	return

def ServerStop(ServerName, ScreenName, Name, Ram, FileName, Directory, StopCommand, ExitValue):
	if ScreenName.exists:
		ScreenName.send_commands(StopCommand)
		print"Sending the command..."
		sleep(5)
		ScreenName.send_commands("exit")
		sleep(0.5)
		if ScreenName.exists:
			ScreenName.send_commands("exit")
		print"Trying to close the screen..."
		sleep(4.5)
		if ScreenName.exists:
			QuestOK = raw_input('The screen is not responding, would you like to open it or kill it? (o/k) - ')
			if QuestOK == "o":
				ServerConsole(ServerName, ScreenName, Name, Ram, FileName, Directory)
			elif QuestOK == "k":
				ServerKill(ServerName, ScreenName, Name, Ram, FileName, Directory)
			else:
				print "Invalid input."
				raw_input("Press enter to continue...")
				AppExit("Error. You entered an invalid value.")
		else:
			print"Screen successfully closed!"
			sleep(2)
			if ExitValue == True:
				AppExit()
	else:
		print "The Screen is not running."
		raw_input("Press enter to continue...")
		AppExit()

def ServerRestart(ServerName, ScreenName, Name, Ram, FileName, Directory, StopCommand, ServerPort, ServerIPListen):
	ServerStop(ServerName, ScreenName, Name, Ram, FileName, Directory, StopCommand, False)
	ServerStart(ServerName, ScreenName, Name, Ram, FileName, Directory, StopCommand, ServerPort, ServerIPListen)
	return

def ServerKill(ServerName, ScreenName, Name, Ram, FileName, Directory):
	ScreenName.interrupt()
	sleep(1)
	ScreenName.kill()
	if ScreenName.exists:
		print "Impossible to kill the screen, kill it manually."
		print 'To kill it press "CTRL+A" and then "K".'
		raw_input("Press Enter to open the screen...")
		ServerConsole(ServerName, ScreenName, Name, Ram, FileName, Directory)
	print "Screen killed successfully!"
	AppExit()
	return

def SayHello(ServerName, ScreenName, Name, Ram, FileName, Directory, StopCommand, Description, ServerPort, ServerIPListen):
	print "\nHello user, here you are the informations of the server you selected:\n"
	print "Name: ", ServerName
	print "Ram : ", Ram
	print "Filename: ", FileName
	print "Directory: ", Directory
	print "StopCommand: ", StopCommand
	print "Description: ", Description
	print "IP: ", ServerIPListen
	print "Port: ", ServerPort
	AppExit()

def ActServerList():
	ServerListCount = 0
	for data in list_screens():
		screenlist = str(data)
		for data in config["Servers"]:
			listname = config["Servers"][data]["name"]
			ListServerCheck = "'" + listname + "'"
			if ListServerCheck in screenlist:
				ServerListCount = ServerListCount + 1
	if ServerListCount == 0:
		print "There are 0 servers running."
	else:
		print "There are " + str(ServerListCount) + " server running:\n"
	ServerListCount = 0
	for data in list_screens():
		screenlist = str(data)
		for data in config["Servers"]:
			listname = config["Servers"][data]["Name"]
			ListServerCheck = "'" + listname + "'"
			if ListServerCheck in screenlist:
				ServerListCount = ServerListCount + 1
				print str(ServerListCount) + " - " + listname
	AppExit()
	return

def AppExit(ExitError=None):
	if ExitError is not None:
		print "\n" + ExitError
		exit("\nExiting..")
	else:
		print "\nExiting.."
		exit()
	return

def main():
	try:
		Option = OptInputs()
		OptChoose(Option)
	except KeyboardInterrupt:
		exit("\n You pressed Ctrl+C")

if __name__ == "__main__":
	main()
