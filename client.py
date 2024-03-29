from socket import *
import json


def displayTransactions(transactions):
    pass


def main():
    serverName = 'localhost'
    serverPort = 12000

    #creating UDP socket for the client.
    clientSocket = socket(AF_INET, SOCK_DGRAM)

    #getting keyboard input from the client.
    username = input('Enter username: ')
    password = input('Enter password: ')

    #created hashmap/dictionary to store username and password.
    data = {'username': username, 'password': password}
    
    #sending username and password to the server.
    clientSocket.sendto(json.dumps(data).encode(), (serverName, serverPort))

    #receiving response and address from the server.
    response, serverAddress = clientSocket.recvfrom(2048)
    decodedResponse = json.loads(response.decode())

    if decodedResponse['authenticated']:
        print(f'User {username} is authenticated.')
        print(f'Balance: {decodedResponse['balance']}')

        #storing the balance and the transactions
        balance = decodedResponse['balance']
        transactions = decodedResponse['txs']

        displayTransactions(transactions)

        choice = input('Choose one of the following options?\n'
                       '(1) Make a transaction.\n'
                       '(2) Fetch and display the list of transactions.\n'
                       '(3) Quit the program.\n'
                       'Enter your choice: ')
        
        if choice == 1:
            pass
        
        elif choice == 2:
            pass

        elif choice == 3: #terminate the program.
            exit()

    else: #server rejects the message.
        print(f'Authenication failed for user {username}.')
        choose = input('Choose one of the following options?\n'
                       'a. Enter the username and password again.\n'
                       'b. Quit the program.\n'
                       'Enter your choice: ')
        
        #close the socket and terminate the client program.
        if choose.lower() == 'b':
            clientSocket.close()
            exit()

        elif choose.lower() == 'a': #recall main again, so the user can re-enter their username and password.
            main()

    #closing the socket.
    clientSocket.close()

if __name__ == "__main__":
    main()