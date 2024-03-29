from socket import *
import json

if __name__ == '__main__':
    #using port 12000.
    serverPort = 12000

    #creating a UDP socket for the server.
    serverSocket = socket(AF_INET, SOCK_DGRAM) 

    #bind socket to the port.
    serverSocket.bind(('', serverPort))

    #printing that the server is ready to receive messages.
    print('The server is ready to receive.')

    #created hashmap/dictionary to store all possible user information.
    users = { #Note the user's username is used as the key.
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

        #using hashmap/dictionary for server response.
        response = {}

        #sending the server response back to the client.
        serverSocket.sendto(json.dumps(response).encode(), clientAddress)