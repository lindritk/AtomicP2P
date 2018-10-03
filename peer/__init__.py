import threading
import time
import socket
import pickle
import sys

from threading import Event

from peer.connection import PeerConnection

class Peer(threading.Thread):
    def __init__(self, ip='0.0.0.0', port=8000, name='none', role='core', loopDelay = 1 ):
        threading.Thread.__init__(self)
        self.stopped = Event()
        self.loopDelay = loopDelay

        self.setServer(ip, port)
        self.connectlist=[]
        self.connectnum=0
        self.lock = threading.Lock()
        self.name = name
        self.role = role

    def run(self):
        while not self.stopped.wait(self.loopDelay):
            (conn,addr) = self.server.accept()           
            accepthandle = threading.Thread(target=self.acceptHandle,args=(conn,addr))
            accepthandle.start()   
    def stop(self):
        self.stopped.set()

    #accept
    def setServer(self,listenIp,listenPort):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(( listenIp , int(listenPort) ))
        self.server.listen(5)
        self.listenPort = listenPort
        print("server prepared")

    def acceptHandle(self,conn, addr):
        data = (pickle.loads(conn.recv(1024)))
        #join event
        if data[0] == 'join':
            print('new member join')
            for member in self.connectlist:
                self.sendMessage(member[2],member[1],'newmember',[data[1], addr[0]])
            self.addConnectlist(data[1],addr[0])
            self.sendMessage(addr[0],data[1][1],'checkjoin',[self.name, self.listenPort, self.role])
            conn.send(b'join successful.')
        elif data[0] == 'newmember':
            print('new member join')
            self.addConnectlist(data[1][0],data[1][1])
            self.sendMessage(data[1][1],data[1][0][1],'checkjoin',[self.name, self.listenPort, self.role])
            conn.send(b'')        
        elif data[0] == 'checkjoin':
            self.addConnectlist(data[1],addr[0])
            conn.send(b'')

        #message event
        elif data[0] == 'message':
            print (data[0] +": '"+ data[1] + "' from " + addr[0])
            conn.send(b'')
            
        #broadcast event
        elif data[0] == 'broadcast':
            if data[1][1] == self.role or data[1][1] == 'all':
                print("get broadcast from '"+ data[1][0] + "': " + data[1][2]) 


    #send
    def sendMessage(self, ip, port, sendType, message):
        sender = PeerConnection( ip, port, sendType, message)
        sender.start()

    #list
    def addConnectlist(self, member, ip):
        check=True
        for listmember in self.connectlist:
            if self.connectlist != []:
                if member[1] == listmember[1]:
                    check = False
                    break
        if member[1]==self.listenPort:
            check = False  
        if check == True:
            member.insert(2,ip)
            self.connectlist.append(member)
            self.connectnum += 1
            
    def removeConnectlist(self):
        pass