from socket import *
import json

if __name__ == '__main__':
    serverPort = 12000 

    #creating a UDP socket for the server.
    serverSocket = socket(AF_INET, SOCK_DGRAM) 

    #bind socket to the port.
    serverSocket.bind(('', serverPort))

    print('The server is ready to receive.')

    clientList = ['A', 'B', 'C', 'D']
    transactionsList = []

    users = { #created hashmap/dictionary to store all possible user information.
        'A': {'password': 'A', 'balance': 10, 'txts': []},
        'B': {'password': 'B', 'balance': 10, 'txts': []},
        'C': {'password': 'C', 'balance': 10, 'txts': []},
        'D': {'password': 'D', 'balance': 10, 'txts': []}
    }

    while True: #run the server infinitely.
        #read from socket into message and get the clients address.
        message, clientAddress = serverSocket.recvfrom(2048)
        decodedMessage = json.loads(message.decode())

        #receiving username and password from the client.
        username = decodedMessage['username']
        password = decodedMessage['password']

        response = {}

        #sending the server response back to the client.
        serverSocket.sendto(json.dumps(response).encode(), clientAddress)