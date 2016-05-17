#!/usr/bin/python
# -*- coding: iso-8859-2 -*-

import select
import socket
import sys
import threading
import time
import os
from getch import getch, pause
from terminaltables import SingleTable
from colorclass import Color

'''
Program jako parametry przyjmuje:
    -numer portu
    -adresy ip kontrahentów
    -numer ID tej stacji
'''
global port_num
port_num=int(sys.argv[1]) #port na ktorym bedzie dzialac aplikacja

global number_of_players
number_of_players=len(sys.argv)-3 #wskazuje liczbe uzytkownikow
number_of_players=(len(sys.argv)-3)/2+1

global id_number
id_number=int(sys.argv[2])

global phase
phase="Passive"

print "Your node id is %s" % (id_number)

class Node:
    def __init__(self):
        self.nodeid=str(id_number)
        self.nodenum=str(number_of_players)
        self.event=[]
        self.diagnosis=[]
        self.tests=[]
        self.prescribe_ini()

    def prescribe_ini(self):
        for i in range(number_of_players):
            self.event.append('-1')
            self.diagnosis.append('1')
            self.tests.append('1')
        self.diagnosis[id_number]="0"
        self.tests[id_number]="2"
        self.show_status()

    def show_status(self):
        table_data=[]

        temp=[]
        temp.append('Event')
        for i in range (number_of_players):
            temp.append(self.event[i])
        table_data.append(temp)

        temp1=[]
        temp1.append('Diagnosis')
        for i in range (number_of_players):
            temp1.append(self.diagnosis[i])
        table_data.append(temp1)

        temp2=[]
        temp2.append('Tests')
        for i in range (number_of_players):
            temp2.append(self.tests[i])
        table_data.append(temp2)

        table=SingleTable(table_data)
        table.title=Color('{autored}Node ID:'+self.nodeid+' NodeNum:' +
                          self.nodenum+'{/autored}')
        table.inner_row_border="True"
        print table.table

class Packet:
    def __init__(self):
        self.sendid=''
        self.recvid=''
        self.rootevent=''
        self.event=[]
        self.fromid=[]
        self.topology=[]
        self.istested=[]
    def show_packet(self):
        table_data=[
            ['SendID', 'RecvID', 'RootEvent'],
            ['qwe', 'qwe', 'qwe']
        ]
        table=SingleTable(table_data)
        table.title=Color('{autocyan}Packet 1/2{/autocyan}')
        print table.table

        table_data2=[
            ['Event', 'From', 'Topology', 'IsTested'],
            ['to tez tabl', 'to tez', 'to tez']
        ]
        table2=SingleTable(table_data2)
        table2.title=Color('{autocyan}Packet 2/2{/autocyan}')
        print table2.table

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
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

        global gui
        gui=GUI()
        gui.start()
        self.threads.append(gui)


        if len(sys.argv)>3:
            station1=Station(sys.argv[3], sys.argv[4])
            station1.start()
            self.threads.append(station1)
        if len(sys.argv)>5:
            station2=Station(sys.argv[5], sys.argv[6])
            station2.start()
            self.threads.append(station2)
        if len(sys.argv)>7:
            station3=Station(sys.argv[7], sys.argv[8])
            station3.start()
            self.threads.append(station3)



        while running:
            inputready,outputready,exceptready=select.select(input,[],[])
            for s in inputready:
                if s==self.server:
                    c=Client(self.server.accept())
                    c.start()
                    self.threads.append(c)

        self.server.close()
        for c in self.threads:
            c.join()


class Station(threading.Thread):
    def __init__(self, address, nodeid):
        threading.Thread.__init__(self)
        self.host=address
        self.port=port_num
        self.size=1024
        self.nodeid=nodeid
        self.s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def run(self):
        self.s.connect((self.host,self.port))
        global phase
        running=1
        while running:
            #print "jestem station numer %s i sie zbudzilem i zasne na 5 sek" % (self.nodeid)
            #gui.node.show_status()
            time.sleep(1)
            if phase=="Passive":
                self.s.send("Are you alive?")
                self.data=self.s.recv(self.size)
                if self.data=="I'm alive":
                    if gui.node.diagnosis[int(self.nodeid)]!="0":
                       phase="Active"
                       print "zmieniam faze na aktywna"
            else:
                os.system('clear')
                print "active phase"
			#print "%s" % self.data
            #sys.stdout.write(self.data)
        self.s.close()


class GUI(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.node=Node()
        self.packet=Packet()


    def run(self):
        key=0
        while 1:
            key = getch()
            if key=='h':
                print 'input:\n c - to clear console\n q - to quit'
            elif key=='q':
                serwer.server.shutdown(1)
                print "you choose quit"
                os._exit(1)
            elif key=='c':
                os.system('clear')
            elif key=='s':
                print self.node.show_status()
            elif key=='p':
                print self.packet.show_packet()
            else:
                print "input h for help"


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

            if data=="Are you alive?":
				self.client.send("I'm alive")
            else:
                self.client.close()
                running=0

print "Beginning..."
serwer=Server()
serwer.run()
print "Program finished work"


