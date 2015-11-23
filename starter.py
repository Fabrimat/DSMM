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
import subprocess
# from subprocess import Popen
import time
from screenutils import list_screens, Screen #Install required
import yaml #Install required
# import logging

#Import the config
config = yaml.load(open('config.yml', 'r'))

def ClearScreen():
	subprocess.call('clear', shell = True)
	return


def OptInputs():
	#The start function, choose what to do
	ClearScreen()
	print "Options:"
	print "1 - Start server."
	print "2 - Open a server console."
	print "3 - Send a command to a server."
	print "4 - Stop server."
	print "5 - Restart a server."
	print "6 - Kill a server."
	print "7 - Edit server RAM."
	print "8 - List all running terminals."
	print "9 - Exit."
	Option = input("Insert the option number: ")
	return Option


def ErrorCheck(Option):
	#Check if the option is valid
	if Option < 1 and Option > 9:
		sys.exit("Invalid Option")
	return


def InputServerName():
	#Insert the Server Name and validate it.
	InvName = True
	ServerName = "NULL"
	ScreenName = "NULL"
	while InvName == True:  # Loop for QuestClose
		ValidName = False
		ServerName = raw_input("Insert the server name: ")
		if ServerName == "help" or ServerName == "Help":
			ServerList()
		else:
			for config["servers"] in config:
				if ServerName == data:
					ValidName = True
				if ValidName == True:  # Check if servername is valid
					ScreenName = Screen(ServerName)
					InvName = False
					break
				else:
					print data
					InvName = True
		if InvName == True:
			print 'Invalid name. Type "help" for the list.'
	return ServerName

def GetServerInfo(ServerName):
	ScreenName = Screen(ServerName)
	Name = config["servers"][ServerName]["name"]
	Ram = config["servers"][ServerName]["ram"]
	FileName = config["servers"][ServerName]["filename"]
	Directory = config["servers"][ServerName]["directory"]
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
		ActScreenList()
	elif Option == 9:
		AppExit()
	return

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
	ScreenName.send_commands("cd " + Directory)
	ScreenName.send_commands('java -Xmx' + Ram + ' -Xms' + Ram + ' -jar ' + FileName + ' nogui -o true')
	AppExit()
	return

def ServerConsole(ServerName, ScreenName, Name, Ram, FileName, Directory):
	if ScreenName.exists:
		ScreenName.detach()
		os.system('screen -r vanilla')
		sys.exit()
	else:
		print "The Screen is not running. Check if it's running with this user, otherwise start it."
		raw_input("Press enter to continue...")
		OptInputs()
	return


def ServerCommand(ServerName, ScreenName, Name, Ram, FileName, Directory):
	if ScreenName.exists:
		while True: #Loop for QuestClose
			QuestClose = raw_input("The Screen is not active, would you like to start it? (y/n) - ")
			if QuestClose == "y":
				ServerStart(ServerName, ScreenName, Name, Ram, FileName, Directory)
				break
			elif QuestClose == "n":
				OptInputs()
			else:
				print "Invalid input."
	return


def ServerStop(ServerName, ScreenName, Name, Ram, FileName, Directory):
	if ScreenName.exists:
		ScreenName.send_commands("stop")
		ScreenName.send_commands("end")
		print"Sending the command..."
		time.sleep(5)
		ScreenName.send_commands("exit")
		print"Trying to close the screen..."
		time.sleep(5)
		if ScreenName.exists:
			QuestOK = raw_input('The screen is not responding, would you like to open it or kill it? (o/k) - ')
			if QuestOK == "o":
				ServerConsole(ServerName, ScreenName, Name, Ram, FileName, Directory)
			elif QuestOK == "k":
				ServerKill(ServerName, ScreenName, Name, Ram, FileName, Directory)
			else:
				print "Invalid input."
				raw_input("Press enter to continue...")
				OptInputs()
		else:
			print"Screen successfully closed!"
			time.sleep(2)
			AppExit()
	else:
		print "The Screen is not running."
		raw_input("Press enter to continue...")
		AppExit()
	return

def ServerRestart(ServerName, ScreenName, Name, Ram, FileName, Directory):
	ServerStop(ServerName, ScreenName, Name, Ram, FileName, Directory)
	ServerStart(ServerName, ScreenName, Name, Ram, FileName, Directory)
	return

def ServerKill(ServerName, ScreenName, Name, Ram, FileName, Directory):
	print "ServerKill"

def ServerEditRam(ServerName, ScreenName, Name, Ram, FileName, Directory):
	print "hi"

def ActScreenList():
	screenutils.list_screens()
	return

def AppExit():
	print "AppExit"

def main():
	Option = OptInputs()
	OptChoose(Option)

if __name__ == "__main__":
	main()
