from socket import *
import sys
import json
import threading
import re

serverName = 'servername'
serverPort = 8001

clientSocket = socket(AF_INET,SOCK_STREAM)
clientSocket.connect(('localhost',int(serverPort)))

uniId = ''
isactive = True
user = {}

#uniId = na-na-na-na-na          n-> no of characters  a->shifting value
def encryptDecryptData(uniId,msg,multiplier) :
    senderPat = ''
    for i in range(0,len(uniId),2) :
        x = int(uniId[i])
        for j in range(x) :
            senderPat += uniId[i+1]

    text = ''
    s = 0
    for i in range(len(msg)) :
        text += chr(ord(msg[i]) - int(senderPat[s]) * multiplier)
        s = (s + 1) % len(senderPat)

    return text 

def sendingThread() :
    global clientSocket
    print('enter msg to send')
    msg = input()
    data = re.split('\s*[:,]\s*',msg,3)
    print(data)
    
    if len(data) > 3 and  re.search('.*TO',data[0].upper()) != None and re.search('M.*S.*G.*',data[2].upper()) != None :
        try : 
            message = {
                'to' : int(data[1]),
                'msg' : encryptDecryptData(user['id'],data[3],1)
            }
            
            data = json.dumps(message)
            clientSocket.send(data.encode())
            print('msg sent')
        except :
            print('Invalid Number :')
    else :
        print("Please re-enter the message with proper format,\n\n To : 'number',Message : 'your message' \n")

def historyThread() :
    print('History to be created')

def receivingThread() :
    global clientSocket,isactive,user
    while isactive :
        try : 
            data = clientSocket.recv(2048)
            msg = data.decode()
            data = json.loads(data)
            if not data['error'] :
                print(encryptDecryptData(user['id'],data['msg'],-1))
            else :
                print(data['type'])
        except :
            print('Error in receiving Thread')

    print('Session Ended :')

def helpThread() :
    print('Available Command with Syntax')
    print("send :     //send message ")
    print("history :  //get your message history")
    print("help :     // to get additional help")   
    print("exit :     //to end the session")

def registerUserThread(client) :
    num = input('Enter your number : ')
    client.send(num.encode())
    response = client.recv(256)
    r = response.decode()
    res = json.loads(r)
    return res


user = registerUserThread(clientSocket) 
print(user)
if not user['error'] :
    print("use 'help' to get help")
    id = user['id']
    recevier = threading.Thread(target=receivingThread, args=())
    recevier.start()
    while 1 :
        try :
            com = input()
            com = com.upper()
            if com == 'HELP' :
                helpThread()
            elif com == 'SEND' :
                sendingThread()
            elif com == 'HISTORY' :
                historyThread()
            elif com == 'EXIT' :
                isactive = False
                clientSocket.send('exit'.encode())
                break
            else :
                print("Command doesn't exit, use 'help' command")
        
        except :
            print('error in while')
    
 
    sys.exit()
    
else :
    clientSocket.send('exit'.encode())
    print('Client registration failed !')

