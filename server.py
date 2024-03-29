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
        'A': {'password': 'A', 'balance': 10, 'txs': [], 'tx_id': 100},
        'B': {'password': 'B', 'balance': 10, 'txs': [], 'tx_id': 200},
        'C': {'password': 'C', 'balance': 10, 'txs': [], 'tx_id': 300},
        'D': {'password': 'D', 'balance': 10, 'txs': [], 'tx_id': 400}
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

        #checking if the username is valid and if their password is correct.
        if username in users and users[username]['password'] == password:
            response['authenticated'] = True
            response['balance'] = users[username]['balance']
            response['txs'] = users[username]['txs']
            response['tx_id'] = users[username]['tx_id']

        else:
            response['authenticated'] = False

        #sending the server response back to the client.
        serverSocket.sendto(json.dumps(response).encode(), clientAddress)