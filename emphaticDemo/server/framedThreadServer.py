#! /usr/bin/env python3
import sys
sys.path.append("../") 
import os, socket, params, time
from threading import Thread
from framedSock import FramedStreamSock


try:
    listenPort = int(sys.argv[0])
except IndexError:
    listenPort = int("50001")
debug = 0

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)

acquiredLock=False

class ServerThread(Thread):
    requestCount = 0            # one instance / class
    def __init__(self, sock, debug):
        Thread.__init__(self, daemon=True)
        self.fsock, self.debug = FramedStreamSock(sock, debug), debug
        self.start()
    def run(self):
        print("new thread handling connection from", addr)
        fileName = ''
        mssg = ''

        while True:
            # print('attempting to receive message')
            msg = self.fsock.receivemsg()
            # print('successfully received message')
            if not msg:
                print(self.fsock, "server thread done")
                break
            mssg += msg.decode('utf-8')
            if(not fileName): # Get file name
                fileName = mssg.split(" ", 1)[0]
                fileNameLen = len(fileName)
                mssg = mssg[fileNameLen + 1:]
            requestNum = ServerThread.requestCount
            time.sleep(0.001)
            ServerThread.requestCount = requestNum + 1
            msg = ("%s! (%d)" % (msg, requestNum)).encode()
            self.fsock.sendmsg(msg)

         # Creating file on the server with contents of message
        if os.path.isfile(fileName):
            print("The file already exists on the server! Another file will not be created.")
        else:
            if fileName:    
                f = open(fileName, "w")
                f.write(mssg)
                f.close()
            else:
                print('The file you are trying to transfer is empty. Cancelling transfer. It might be due to being transferred already')


while True:
    sock, addr = lsock.accept()
    ServerThread(sock, debug)
