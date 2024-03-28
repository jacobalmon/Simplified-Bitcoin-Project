from socket import *

if __name__ == '__main__':
    serverPort = 12000 
    #creating a UDP socket for the server.
    serverSocket = socket(AF_INET, SOCK_DGRAM) 
    serverSocket.bind(serverPort)
    print("The server is ready to receive.")

    clientList = ['A', 'B', 'C', 'D']
    transactionsList = []

    while True: #run the server infinitely.
        #read from socket into message and get the clients address.
        message, clientAddress = serverSocket.recvfrom(2048)