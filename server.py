from socket import *
import threading
import json
import sys
import random
import os 
import re

db = os.path.join(os.getcwd(),'Database')
dbms_clientbox = os.path.join(db,'dbms_clientbox.csv')
dbms_authenticate = []

serverPort = 8001
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(5)

print('The server is running at port : ' + str(serverPort))

def encryptData(senderId,receiverId,msg) :
    senderPat = ''
    receiverPat = ''

    for i in range(0,len(senderId),2) :
        x = int(senderId[i])
        for j in range(x) :
            senderPat += senderId[i+1]
 
    for i in range(0,len(receiverId),2) :
        x = int(receiverId[i])
        for j in range(x) :
            receiverPat += receiverId[i+1]
    
    text = ''
    s = 0
    r = 0

    for i in range(len(msg)) :
        text += chr(ord(msg[i]) + int(senderPat[s]) - int(receiverPat[r]))
        s = (s + 1) % len(senderPat)
        r = (r + 1) % len(receiverPat)

    return text

def getNewId(length) :
    a = '123456'
    id = ''
    for i in range(length) :
        id += random.choice(a)
    return id

def getUser(mobNo) :
    for user in dbms_authenticate :
        if user['mobNo'] == mobNo :
            return user

def checkForMsg(client,user,lock) :
    lock.acquire()
    box = open(dbms_clientbox,'r')
    data = box.read()
    line = re.split('&\n*',data)
    msgList = []
    text = line[0]
    del line[0]
    for x in line :
        msg = re.search('^'+str(user['mobNo']),x)
        if msg != None :
            data = x.split(',')
            res = {
                    'from' : data[1],
                    'msg' : encryptData(data[2],user['key'],data[3]),
                    'error' :False
            }
            print('\tTo   : ' ,user['mobNo'],', Message :' ,res['msg'])
            msgList.append(res)
        else :
            text +=  '&\n' + x
    box = open(dbms_clientbox,'w')
    box.write(text)
    box.close()
    lock.release()
    for i in range(len(msgList)) :
        res = json.dumps(msgList[i])
        client.send(res.encode())



def clientManager(client,addr,user,lock):
    print('Connected to Client : ' + str(user['mobNo']))
    checkForMsg(client,user,lock)
    while True:
        try :
            data = client.recv(2048)
            msg = data.decode()
            if msg.lower() == 'exit':
                dbms_authenticate.remove(user)
                res = {'error' : True ,'type' : 'exiting...'}
                data = json.dumps(res)
                client.send(data.encode())
                client.close()
                break  
            data = json.loads(msg)
    
            print('\tFrom : ',user['mobNo'] ,', Message :' ,data['msg'])

            receiver = getUser(data['to'])
            if receiver == None :
                res = { 
                    'error' : True,
                    'type' : 'Receiver Offline'
                }

                lock.acquire()
                text = '&\n'+str(data['to']) + ','  + str(user['mobNo']) + ',' + user['key'] + ',' + data['msg']
                box = open(dbms_clientbox ,mode='a+')
                box.write(text)
                box.close()
                lock.release()

                res = json.dumps(res)
                client.send(res.encode())
                print('\tTo : Receiver Offline')
            else :
                text = encryptData(user['key'],receiver['key'],data['msg'])
                res = {
                    'from' : user['mobNo'],
                    'msg' : text,
                    'error' :False
                }
                print('\tTo   : ' ,receiver['mobNo'],', Message :' ,res['msg'])
                res = json.dumps(res)
                receiver['ip'].send(res.encode())
                
        except :
            dbms_authenticate.remove(user)
            print(str(user['mobNo'] ), ' : ' , 'error')
            break

    print('Client : '+ str(user['mobNo']) + ', session ended') 

def registerClient(clientSocket,addr,lock) :
    global dbms_authenticate
    user = {}
    try : 
        client = clientSocket.recv(256)
        
        user['ip'] = clientSocket
        user['mobNo'] = int(client.decode())
        user['key'] = getNewId(10)
       
        dbms_authenticate.append(user)

        thread = threading.Thread(target=clientManager,args=(clientSocket,addr,user,lock))
        thread.start()

        res = { 'error' : False , 'type' :'' ,'key' : user['key'] }
        data = json.dumps(res)
        clientSocket.send(data.encode())
    except :
        res = { 'error' : True , 'Type' : 'Invalid Number' }
        data = json.dumps(res)
        clientSocket.send(data.encode())


def exitTemp() :
    i = input()
    if i == 'q' :
        serverSocket.close()
        sys.exit()

while 1 :
    e = threading.Thread(target=exitTemp, args=())
    e.start()
    try :
        clientSocket,addr = serverSocket.accept()
        lock = threading.Lock()
        c = threading.Thread(target=registerClient ,args=(clientSocket,addr,lock))
        c.start()
    except :
        print('Error at main server :')
        break
        

    

