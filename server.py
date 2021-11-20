from socket import *
import threading
serverPort = 8001
serverSocket = socket()
serverSocket.bind(('',serverPort))
serverSocket.listen(5)

print('The server is running at port : ' + str(serverPort))

def multi_thread(client,addr):
    while 1:
        print('Current Thread : '+ str(threading.current_thread()))
        data = client.recv(1024)
        msg = data.decode('utf-8')
        print(msg)
        if msg == 'exit':
            print('Exiting..')
            break
        capatilizedSentence = data.upper()
        client.send(capatilizedSentence)
        
        
while 1 :
        connectionSocket,addr = serverSocket.accept()
        print('Connected to: '+ addr[0] + ':' + str(addr[1]))
        thread = threading.Thread(target=multi_thread,args=(connectionSocket,addr));
        thread.start()
        
  
    

