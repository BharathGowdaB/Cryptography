from socket import *
import sys
serverName = 'servername'
serverPort = 8001

clientSocket = socket()

clientSocket.connect(('localhost',int(serverPort)))

#uniId = na-na-na-na-na          n-> no of characters  a->shifting value
def encryptDecryptData(uniId,msg,type) :
    length = len(uniId)
    n = []
    a = []
    sum = 0
    for i in range(0,length,2) :
        n.append(int(uniId[i]))

    for i in range(1,length,2) :
        a.append(int(uniId[i]) * type) 
    sum = 0
    
    for i in range(len(n)) :
        sum += n[i]
        
    print(n , a)
    m = len(msg)//sum
    text = ''
    count = 0
    x = 0
    y = 0
    while True :
        for j in range(n[x]) :
            if(count >= len(msg)) :
                return text
            text += chr(ord(msg[count]) + a[j])
            count += 1
        x = (x + 1) % len(n)


text = encryptDecryptData('12342515','How are you?' ,1)
text = encryptDecryptData('12342515',text,-1)
print(text)
while 1 :
    
    msg = input('Input lowercase sentence: ')
    dataToSend = encryptDeccryptData('12342515',msg,1)
    dataBytes = bytes(dataToSend,'utf-8')
  
    clientSocket.send(dataBytes)
    
    if(msg == 'exit'):
        break
      
    response = clientSocket.recv(1024)
    
    msgreceived = encryptDeccryptData('12342515',msg,-1)
    print('From Server :' ,msgReceived)

