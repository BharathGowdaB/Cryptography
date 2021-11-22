from socket import *
import threading
import json
import sys
import random

serverPort = 8001
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(5)

dbms_Authenticate = []

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
    for user in dbms_Authenticate :
        if user['mobNo'] == mobNo :
            return user
    
def clientManager(client,addr,user):
    print('Connected to Client : ' + str(user['mobNo']))
    while True:
        try :
            data = client.recv(2048)
            msg = data.decode()
            if msg.lower() == 'exit':
                dbms_Authenticate.remove(user)
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
                res = json.dumps(res)
                client.send(res.encode())
                print('\tTo : Receiver Offline')
            else :
                text = encryptData(user['id'],receiver['id'],data['msg'])
                res = {
                    'from' : user['mobNo'],
                    'msg' : text,
                    'error' :False
                }
                print('\tTo   : ' ,receiver['mobNo'],', Message :' ,res['msg'])
                res = json.dumps(res)
                receiver['ip'].send(res.encode())
                
        except :
            dbms_Authenticate.remove(user)
            print(str(user['mobNo'] ), ' : ' , 'error')
            break


    print('Client : '+ str(user['mobNo']) + ', session ended') 

def registerClient(clientSocket,addr) :
    global dbms_Authenticate
    user = {}
    try : 
        client = clientSocket.recv(256)
        
        user['ip'] = clientSocket
        user['mobNo'] = int(client.decode())
        user['id'] = getNewId(10)
       
        dbms_Authenticate.append(user)

        thread = threading.Thread(target=clientManager,args=(clientSocket,addr,user))
        thread.start()

        res = { 'error' : False , 'type' :'' ,'id' : user['id'] }
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
        c = threading.Thread(target=registerClient ,args=(clientSocket,addr))
        c.start()
    except :
        print('Error at main server :')
        

    

