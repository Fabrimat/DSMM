+#!/usr/bin/env python2
+#import logging
+import sys
+import subprocess
+import os
+from subprocess import Popen
+import time
+from screenutils import list_screens, Screen
+ 
+serverlist = ["bungee","lobby","vanilla","plotcreative"]
+filelist=["BungeeCord","spigot","spigot","spigot"]
+ramlist=["512M","1024M","5120M","2048M"]
+ 
+def cls():
+    if os.name == "posix":
+        subprocess.call('clear', shell=True)
+ 
+def servergetlist():
+        cls()
+        print "List of avaiable servers:\n"
+        for i in range(len(serverlist)):
+                print serverlist[i]
+        print ""
+ 
+def inputs():
+    #Ask for inputs
+	print "Server starter script"
+	print 'Please enter the inputs or type "help" to see the list of the servers.\n'
+	servername=raw_input("Insert the server name - ")
+	if servername=="help" or servername=="Help":
+		servergetlist()
+		servername=inputs()
+	return servername
+
+def getdatas(servername):
+	svalue=serverlist.index(servername)
+	getram=ramlist[svalue]
+	getfile=filelist[svalue]
+	return getram, getfile
+
+
+def screenactions(servername):
+	if servername in serverlist:
+		screenname = Screen(servername)
+		if screenname.exists:
+			closing=raw_input("The Screen is already active, would you like to stop it? (y/n) - ")
+			if closing=="y":
+				closecommand=raw_input("Insert the stop command. - ")
+				screenname.send_commands(closecommand)
+				print"Sending the command..."
+				time.sleep(5)
+				if screenname.exists:
+					print('The screen is not responding, please open it and kill it manually with "CTRL+A and K".')
+					sys.exit()
+			else:
+				main()
+		screenname = Screen(servername, True)
+		datas=getdatas(servername)
+		screenname.send_commands("cd /home/denagon/"+servername)
+		screenname.send_commands("java -Xmx"+datas[0]+" -Xms"+datas[0]+" -jar /home/denagon/"+servername+"/"+datas[1]+".jar -o true")
+		sys.exit()
+	else:
+		sys.exit('Invalid name. Type "help" for the list.')
+
+def main():
+	cls()
+	servername=inputs()
+	screenactions(servername)
+	sys.exit()
+
+if __name__ == "__main__":
+	main()
