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


        if 'username' in decodedMessage and 'password' in decodedMessage:
            print(f'Received an authenication request from user {username}')
            #receiving username and password from the client.
            username = decodedMessage['username']
            password = decodedMessage['password']

            #using hashmap/dictionary for server response.
            response = {}

            #checking if the username is valid and if their password is correct.
            if username in users and users[username]['password'] == password:
                response['authenticated'] = True
                response['tx_id'] = users[username]['tx_id']
                response['balance'] = users[username]['balance']
                response['txs'] = users[username]['txs']

                print(f'User {username} is authenticated.')

            else:
                response['authenticated'] = False

                print(f'User {username} is not authenticated.')

            #sending the server response back to the client.
            serverSocket.sendto(json.dumps(response).encode(), clientAddress)
        
        elif 'action' in decodedMessage and decodedMessage['action'] == 'make_transaction':
            print(f'Received an make transaction request from user {username}.')
            tx = decodedMessage['transaction']
            payer = tx['payer']
            amount_transferred = tx['amount_transferred']
            payee1 = tx['payee1']
            amount_received_payee1 = tx['amount_received_payee1']
            payee2 = tx.get('payee2', None)
            amount_received_payee2 = tx.get('amount_received_payee2', None)

            response = {}

            if users[payer]['balance'] < amount_transferred:
                response['status'] = 'rejected'
                response['balance'] = users[payer]['balance']

                print(f'Rejected a transaction for user {username}')

            else:
                print(f'Send the list of transactions to user {username}.')
                response['status'] = 'confirmed'
                response['balance'] = users[payer]['balance'] - amount_transferred

                users[payer]['balance'] -= amount_transferred
                users[payer]['txs'].append(tx)
                users[payee1]['txs'].append(tx)
                users[payer]['tx_id'] += 1
                users[payee1]['balance'] += amount_received_payee1
                
                if payee2:
                    users[payee2]['balance'] += amount_received_payee2
                    users[payee2]['txs'].append(tx)

                print(f'Confirmed a transaction for user {username}.')


            serverSocket.sendto(json.dumps(response).encode(), clientAddress)