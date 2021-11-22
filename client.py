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
isServer = False

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
    print('Enter your message :')
    msg = input()
    data = re.split('\s*[:,]\s*',msg,3)
    
    if len(data) > 3 and  re.search('.*TO',data[0].upper()) != None and re.search('M.*S.*G.*',data[2].upper()) != None :
        res  = ''
        try : 
            message = {
                'to' : int(data[1]),
                'msg' : encryptDecryptData(user['key'],data[3],1)
            }
            res = json.dumps(message)   
        except :
            print('Invalid Number :')

        clientSocket.send(res.encode())    
    else :
        print("Please re-enter the message with proper format,\n\n To : 'number',Message : 'your message' \n")

def historyThread() :
    print('History to be created')

def receivingThread() :
    global clientSocket,isactive,user,isServer
    while isactive :
    
            data = clientSocket.recv(2048)
            msg = data.decode()
            data = json.loads(msg)
            if not data['error'] :
                print('\tFrom : ' , str(data['from']),', MSG : ' ,encryptDecryptData(user['key'],data['msg'],-1))
            else :
                print(data['type'])
        
        #    isServer = False
         #   print('Server Not Responding')
          #  break

def helpThread() :
    print('\nAvailable Commands')
    print("\tsend      --send message ")
    print("\thistory   --get your message history")
    print("\thelp      -- to get additional help")   
    print("\texit      --to end the session")

def registerUserThread(client) :
    num = input('Enter your number : ')
    client.send(num.encode())
    response = client.recv(256)
    r = response.decode()
    res = json.loads(r)
    return res


user = registerUserThread(clientSocket) 

if not user['error'] :
    isServer = True
    print("use 'help' to get help")
    id = user['key']
    recevier = threading.Thread(target=receivingThread, args=())
    recevier.start()
    while 1 :
        try :
            com = input()
            com = com.upper()
            if com == 'HELP' :
                helpThread()

            elif com == 'SEND' :
                if isServer :
                    sendingThread()
                else :
                    print('Server Unavailable')

            elif com == 'HISTORY' :
                historyThread()

            elif com == 'EXIT' :
                isactive = False
                clientSocket.send('exit'.encode())
                break
            else :
                print("Command doesn't exit, use 'help' command")
        
        except :
            break

    print('Session Ended :')
    sys.exit()
    
else :
    clientSocket.send('exit'.encode())
    print('Client registration failed !')

