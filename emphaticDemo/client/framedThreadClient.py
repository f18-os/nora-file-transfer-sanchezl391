#! /usr/bin/env python3

# Echo client program
import sys
sys.path.append('../')
import socket, re
import params
from framedSock import FramedStreamSock
from threading import Thread
import time

try:
    serverHost = sys.argv[0]
    serverPort = int(sys.argv[1])
    inputFileName = sys.argv[2]
except IndexError:
    serverHost = "127.0.0.1"
    serverPort = int("50001")
    inputFileName = "test.txt"    

debug = 0

class ClientThread(Thread):
    def __init__(self, serverHost, serverPort, debug):
        Thread.__init__(self, daemon=False)
        self.serverHost, self.serverPort, self.debug = serverHost, serverPort, debug
        self.start()
    def run(self):
        s = None    
        for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
                s = socket.socket(af, socktype, proto)
            except socket.error as msg: 
                print(" error: %s" % msg)
                s = None
                continue
            try:
                print("attempting to connect to %s" % repr(sa))
                s.connect(sa)
            except socket.error as msg:
                print(" error: %s" % msg)
                s.close()
                s = None
                continue
            break

        if s is None:
            print('could not open socket')
            sys.exit(1)

        fs = FramedStreamSock(s, debug=debug)

        try:
            f = open(inputFileName, "r")
            originalMssg = f.read(100) # read 100 bytes from file at a time
            if(not len(originalMssg)):
                print("The file you are trying to transfer is empty. Cancelling transfer.")
            else:
                mssg = inputFileName + ' ' + originalMssg
                print('will send: ' + mssg)
                mssgBytes = mssg.encode()
                while True: # Send bytes in 100 byte pieces until there is no more to send
                    if mssg == '':
                        break
                    print('sending mssg now')
                    fs.sendmsg(mssgBytes) # send mssg
                    print("received:", fs.receivemsg())
                    mssg = f.read(100)
                    mssgBytes = mssg.encode()

                f.close()
        except FileNotFoundError:
            print('Error. You did not specify a file to transfer or it wasnt found')

for i in range(1):    
# for i in range(1):
    ClientThread(serverHost, serverPort, debug)

