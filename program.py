import select
import socket
import sys
import threading
import time
import os
from getch import getch, pause

#wirtualka: 192.168.122.29
#jasam:     192.168.1.118
global port_num
port_num=int(sys.argv[1])

class Server:
    def __init__(self):
        self.host=''
        self.port=port_num
        self.backlog=5
        self.size=1024
        self.server=None
        self.threads=[]

    def open_socket(self):
        try:
            self.server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host,self.port))
            self.server.listen(5)
        except socket.error, (value, message):
            if self.server:
                self.server.close()
            print "could not open socket: " + message
            sys.exit(1)

    def run(self):
        self.open_socket()
        input=[self.server,sys.stdin]
        running=1
        key=0
        station=Station('localhost')
        station.start()
        gui=GUI()
        gui.start()
        self.threads.append(station)
        while running:
            inputready,outputready,exceptready=select.select(input,[],[])

            for s in inputready:
                if s==self.server:
                    c=Client(self.server.accept())
                    c.start()
                    self.threads.append(c)
                    print "Ilosc watkow: %s" % len(self.threads)

        self.server.close()
        for c in self.threads:
            c.join()


class Station(threading.Thread):
    def __init__(self, address):
        threading.Thread.__init__(self)
        self.host=address
        self.port=port_num
        self.size=1024
        self.s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def run(self):
        self.s.connect((self.host,self.port))

        running=1
        while running:
            time.sleep(5)
            self.s.send("sam do siebie! :-)")
            self.data=self.s.recv(self.size)
            #sys.stdout.write(self.data)
        self.s.close()

class GUI(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        key=0
        while 1:
            key = getch()
            if key=='h':
                print 'Wprowadz:\n c - aby wyczyscic konsole\n q - zeby zakonczyc dzialanie programu'
            elif key=='q':
                serwer.server.shutdown(1)
                print "Koniec dzialania programu"
                os._exit(1)
            elif key=='c':
                os.system('clear')
            else:
                print "wpisz h (help) aby poznac opcje"

class Client(threading.Thread):
    def __init__(self,(client,address)):
        threading.Thread.__init__(self)
        self.client=client
        self.address=address
        self.size=1024
    def run(self):
        running=1
        while running:
            data=self.client.recv(self.size)
            if data:
                self.client.send(data)
                print "Otrzymalem: %s" % data
            else:
                self.client.close()
                running=0

print "Program obrazujacy dzialanie algorytmu ADAPT2!"
serwer=Server()
serwer.run()
print "Skonczylem  roobote"



