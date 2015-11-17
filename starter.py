#!/usr/bin/env python2
'''
    DSMM v0.0 - Dedicaded Server Minecraft Manager
    Author: Fabrimat
    Repository: https://github.com/Fabrimat/DSMM
'''

import sys
import os
if os.name != "posix":
    sys.exit("\nOS not supported.\n")
    logging.error("%s not supported.", os.name)
# import subprocess
# from subprocess import Popen
import time
from screenutils import list_screens, Screen
from ConfigParser import SafeConfigParser, RawConfigParser
import ConfigParser
# import logging

parser = SafeConfigParser()
parser.read('config.ini')

def ClearScreen():
    #Clear the screen only if the OS is Posix (Linux)
    if os.name == "posix":
        subprocess.call('clear', shell = True)


def OptInputs():
    #The start function, choose what to do
    print "Options:"
    print "1 - Start server."
    print "2 - Open a server console."
    print "3 - Send a command to a server."
    print "4 - Stop server."
    print "5 - Restart a server."
    print "6 - Kill a server."
    print "7 - Edit server RAM."
    print "8 - Exit."
    Option = input("Insert the option number: ")
    return Option


def ErrorCheck(Option):
    #Check if the option is valid
    if Option < 1 and Option > 8:
        sys.exit("Invalid Option")


def InputServerName():
    #Insert the Server Name and validate it.
    InvName = True
    ServerName = "NULL"
    ScreenName = "NULL"
    while InvName == True:  # Loop for QuestClose
        ValidName = False
        ServerName = raw_input("Insert the server name:")
        if ServerName == "help" or ServerName == "Help":
            ServerList()
        else:
            for section_name in parser.sections():
                if ServerName == section_name:
                    ValidName = True
                if ValidName == True:  # Check if servername is valid
            	    ScreenName = Screen(ServerName)
                    InvName = False
                    break
                else:
                    print section_name
                    InvName = True
        if InvName == True:
            print 'Invalid name. Type "help" for the list.'
    return ServerName

def GetServerInfo(ServerName):
    RawConfigParser = ConfigParser.ConfigParser()
    ScreenName = Screen(ServerName)
    Name = RawConfigParser.get(ServerName, "name")
    Ram = RawConfigParser.get(ServerName, "ram")
    FileName = RawConfigParser.get(ServerName, "filename")
    Directory = RawConfigParser.get(ServerName, "directory")
    return ServerName, ScreenName, Name, Ram, FileName, Directory

def OptChoose(Option):
    if Option == 1:
        ServerName = InputServerName()
        ServerInfo = GetServerInfo(ServerName)
        ServerStart(ServerInfo[0], ServerInfo[1], ServerInfo[2], ServerInfo[3], ServerInfo[4], ServerInfo[5])
    elif Option == 2:
        ServerName = InputServerName()
        ServerInfo = GetServerInfo(ServerName)
        ServerConsole(ServerInfo[0], ServerInfo[1], ServerInfo[2], ServerInfo[3], ServerInfo[4], ServerInfo[5])
    elif Option == 3:
        ServerName = InputServerName()
        ServerInfo = GetServerInfo(ServerName)
        ServerCommand(ServerInfo[0], ServerInfo[1], ServerInfo[2], ServerInfo[3], ServerInfo[4], ServerInfo[5])
    elif Option == 4:
        ServerName = InputServerName()
        ServerInfo = GetServerInfo(ServerName)
        ServerStop(ServerInfo[0], ServerInfo[1], ServerInfo[2], ServerInfo[3], ServerInfo[4], ServerInfo[5])
    elif Option == 5:
        ServerName = InputServerName()
        ServerInfo = GetServerInfo(ServerName)
        ServerRestart(ServerInfo[0], ServerInfo[1], ServerInfo[2], ServerInfo[3], ServerInfo[4], ServerInfo[5])
    elif Option == 6:
        ServerName = InputServerName()
        ServerInfo = GetServerInfo(ServerName)
        ServerKill(ServerInfo[0], ServerInfo[1], ServerInfo[2], ServerInfo[3], ServerInfo[4], ServerInfo[5])
    elif Option == 7:
        ServerName = InputServerName()
        ServerInfo = GetServerInfo(ServerName)
        ServerEditRam(ServerInfo[0], ServerInfo[1], ServerInfo[2], ServerInfo[3], ServerInfo[4], ServerInfo[5])
    elif Option == 8:
        AppExit()

def ServerStart(ServerName, ScreenName, Name, Ram, FileName, Directory):
    if ScreenName.exists:
        while True: #Loop for QuestClose
            QuestClose=raw_input("The Screen is already active, would you like to stop it? (y/n) - ")
            if QuestClose == "y":
                ServerStop(ServerName, ScreenName, Name, Ram, FileName, Directory)
                break
    	    elif QuestClose == "n":
                OptInputs()
            else:
                print "Invalid input."
	ScreenName = Screen(ServerName, True)
	Datas = GetDatas(ServerName)
	ScreenName.send_commands("cd %s",Directory)
	ScreenName.send_commands("java -Xmx%s -Xms%s -jar %s nogui -o true", Ram, Ram, FileName)
	sys.exit()

def ServerConsole(ServerName, ScreenName, Name, Ram, FileName, Directory):
    print "ServerConsole"

def ServerCommand(ServerName, ScreenName, Name, Ram, FileName, Directory):
    if ScreenName.exists:
        while True: #Loop for QuestClose
            QuestClose=raw_input("The Screen is not active, would you like to start it? (y/n) - ")
            if QuestClose == "y":
                ServerStart(ServerName, ScreenName, Name, Ram, FileName, Directory)
                break
    	    elif QuestClose == "n":
                OptInputs()
            else:
                print "Invalid input."


def ServerStop(ServerName, ScreenName, Name, Ram, FileName, Directory):
	ScreenName.send_commands("stop")
	ScreenName.send_commands("end")
	print"Sending the command..."
	time.sleep(5)
	ScreenName.send_commands("exit")
	print"Trying to close the screen..."
	time.sleep(5)
	if ScreenName.exists:
		QuestKill = raw_input('The screen is not responding, would you like to kill it? (y/n) - ')
		if QuestKill == "y":
			ServerKill(ServerName, ScreenName)
			print"Killing screen..."
			time.sleep(5)
			if ScreenName.exists:
    				sys.exit('The screen is not responding, please open it and kill it manually with "CTRL+A and K".')
        else:
            OptInputs()

def ServerRestart(ServerName, ScreenName, Name, Ram, FileName, Directory):
    ServerStop(ServerName, ScreenName, Name, Ram, FileName, Directory)
    ServerStart(ServerName, ScreenName, Name, Ram, FileName, Directory)

def ServerKill(ServerName, ScreenName, Name, Ram, FileName, Directory):
    print "ServerKill"

def ServerEditRam(ServerName, ScreenName, Name, Ram, FileName, Directory):
    print "hi"

def AppExit():
    print "AppExit"

def main():
    Option = OptInputs()
    OptChoose(Option)

main()
