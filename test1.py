from Peer import Peer
from time import strftime, sleep
from threading import Thread

if __name__ == "__main__":
	#print "test1"

	p = 5060

	nodeA = Peer(5060, "1, A, 1", "127.0.0.1", 5060)

	tA = Thread( target = nodeA.mainLoop )
	tA.start()

	try:
		# A joins
		nodeA.join(0, 0)
		sleep(1)
		nodeA.list()
		sleep(1)
		nodeA.leave()
		sleep(1)

	except Exception as inst:
		print inst.args

	finally: 
		nodeA.terminateCon()
		