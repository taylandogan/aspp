import socket
from sys import argv, stdout
from threading import Thread,Lock
from time import sleep, strftime

class Peer:
	# initialize the peer
	def __init__(self, serverPort, config, clientAddr, clientPort): 
		self.isPeerActive = 1
		conf = config.split(',')		
		self.id = int(conf[0])
		self.name = conf[1]
		self.connectTo = int(conf[2])	
		self.clientAddr = clientAddr
		self.clientPort = int(clientPort)
		self.serverAddr = '127.0.0.1'
		self.serverPort = int(serverPort)
		self.handlers 	= {'J': self.addPeer, 'L': self.removePeer, 'I': self.listPeers, 'C': self.isPeerLive}
		#self.fingerTable = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
		#self.listOfPeers = []
		#self.biggestPeer = 0

	# initialize the socket for incoming connections
	def initServer(self):
		self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.serverSocket.bind((self.serverAddr, self.serverPort))
		self.serverSocket.listen(1)
		#accept recv

	# Init socket and connect to another peer
	def connectToPeer(self, p):
		self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.clientSocket.connect((self.clientAddr, p))

	# connect to server peer, and send the message
	def sendMsg(self, p, message):
		self.connectToPeer(p)
		self.clientSocket.send(message)
		data = self.clientSocket.recv(1024)

		self.clientSocket.close()

		#print message[0], data

	# send another peer the join request
	def join(self, to, port):
		#sleep(1)
		if (self.id != self.connectTo): # else it is the 1st node
			self.connectTo = to
			self.clientPort = port
			message = 'J' + str(self.connectTo) + ',' + str(self.id) + ',' + self.name + ',' + str(self.serverPort)
			self.sendMsg(self.clientPort, message)
			
			#print 'J', self.id, self.clientPort, self.connectTo
		else:
			print 'JOIN:', self.id, 'at', strftime("%H:%M:%S")

	# send another peer the leave request
	def leave(self):
		#sleep(1)
		#if (self.id in self.listOfPeers):
		#	self.listOfPeers.remove(self.id) # HERE
		if self.id == self.connectTo:
			print 'LEAVE:', self.id, 'at', strftime("%H:%M:%S")
		else:
			message = 'L' + str(self.connectTo) + ',' + str(self.id) + ',' + self.name + ',' + str(self.clientPort)
			self.sendMsg(self.clientPort, message)

	# send another peer the list request
	def list(self):
		#sleep(1)
		#print self.id, self.connectTo, self.clientPort
		message = 'I' + str(self.id)
		self.sendMsg(self.clientPort, message)

	def checkPeerAlive(self):
		message = 'C' + str(self.clientPort) + str(1) + str(self.id)
		self.sendMsg(self.clientPort, message)		

	# handle the incoming requests
	def threadHandler(self):
		data = self.serverCon.recv(1024)
		self.serverCon.send('ACK') 
		#print 'thread Handler: ', data, self.id
		self.serverCon.close()

		self.handlers[data[0]]( data )

	def setSocket(self, id, port):
		self.id = id
		self.clientPort = port

	# print the finger table
	def printInfo(self):
		print self.id, self.connectTo, self.clientPort, self.serverPort
		#print self.id, self.fingerTable, self.listOfPeers
		#print self.id, 'is connecnted to', self.connectTo, 'whose port is', self.clientPort

	# add peer to the network
	def addPeer(self, msg):
		parsed = msg[1:].split(',')
		newNodeCt = int(parsed[0])
		newNodeId = int(parsed[1])
		newNodeN  = parsed[2]
		newNodeP  = int(parsed[3])

		#sleep(1)
		#self.listOfPeers.append(int(msg[2]))
		# update finger table
		#for i in range(1, len(self.fingerTable)+1):
		#	if ( (self.id + (2 ** (i-1)))%(int(msg[2])+1) == int(msg[2])):
		#		self.fingerTable[i] = int(msg[2])
		#		break

		if ( self.connectTo == newNodeCt ):
			self.connectTo = newNodeId
			self.clientPort = newNodeP
			print 'JOIN:', newNodeId, 'at', strftime("%H:%M:%S")
		else:
			self.sendMsg(self.clientPort, msg)
		

	# remove peer from the network
	def removePeer(self, msg):
		parsed = msg[1:].split(',')
		remNodeCt  = int(parsed[0])
		remNodeId  = int(parsed[1])
		remNodeN   = parsed[2]
		remNodeCtP = int(parsed[3])

		#if (int(msg[2]) in self.listOfPeers):
		#	self.listOfPeers.remove(int(msg[2]))

		if ( self.connectTo == remNodeId ):
			self.connectTo = remNodeCt
			self.clientPort = remNodeCtP
			# Adr is local host, no need to change
			print 'LEAVE:', remNodeId, 'at', strftime("%H:%M:%S")
		else:	
			self.sendMsg(self.clientPort, msg)

	# list all peers
	def listPeers(self, msg):
		parsed = msg[1:].split(',')
		sendee = int(parsed[0])

		#print self.id ,sendee

		if ( self.id == sendee ):
			# parse msg and print
			strOfPeers = msg[1:]
			listOfPeers = strOfPeers.split(',')
			stdout.write('LIST: ')
			stdout.write(','.join(listOfPeers))
			print ' at', strftime("%H:%M:%S")
		else: 
			newMsg = msg + ',' + str(self.id)
			#print 'PEERPEER', self.clientPort, self.connectTo, newMsg
			self.sendMsg(self.clientPort, newMsg)

		# finger table solution
		# if  (p+2^(e-1) > table[e-1]+1 
		#	switch to that node
		# else
		#	print table[e]

	#def isPeerLive(self, msg):
	#	port = int(msg[0:4])
	#	e = int(msg[4])
	#	root = int(msg[5:])

	#	# i many nodes away from the sendee, live or dead
	#	if (self.id > root):
	#		i = self.id - root
	#	else:
	#		i = self.id + self.biggestPeer - root

	#	while ( 2**e <= i and e < 6 ):
	#		# sendmessage to port
			# 	send e id and port
	#		self.sendMsg(port, response)
	#		e += 1

	#	if ( e < 6 ):
	#		newMsg = msg[0:4] + str(e) + msg[5:]
			# sendmessage to next peer
	#		self.sendMsg(port, newMsg)

	def set(self, id, port):
		self.id = id
		self.connectTo = id
		self.clientPort = port

	# main loop to accept incoming connections, runs as a seperate thread as long as the peer is alive
	def mainLoop(self):
		# initialize server socket, connenct server peer from client socket
		self.initServer()

		# main loop to accept connections
		while(self.isPeerActive):	# OR TIMEOUT???	
			self.serverCon, addr = self.serverSocket.accept()

			if (self.isPeerActive):
				t = Thread( target = self.threadHandler)
				t.start()
		#print 'mainloop Exits'

	# close socket if neccesary
	def terminateCon(self):
		self.isPeerActive = 0
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect( (self.serverAddr, self.serverPort))
		self.serverSocket.close()
		#print 'connection terminated'
		



