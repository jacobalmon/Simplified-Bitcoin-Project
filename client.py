from socket import *

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
    clientSocket.sendto(data.encode(), serverName, serverPort)

    #receiving response and address from the server.
    response, serverAddress = clientSocket.recvfrom(2048)
    decodedResponse = response.decode()

    if decodedResponse['authenticated']:
        print(f'User {username} is authenicated.')
        print(f'Balance: {decodedResponse['balance']}')

        #storing the balance and the transactions
        balance = decodedResponse['balance']
        transactions = decodedResponse['txs']

        displayTransactions(transactions)

    else: #server rejects the message.
        print(f'Authenication failed for user {username}.')
        choose = input('Choose one of the following options?\n'
                       'a. Enter the username and password again\n'
                       'b. Quit the program.\n'
                       'Enter your choice: ')
        
        #close the socket and terminate the client program.
        if choose.lower() == 'b':
            clientSocket.close()
            exit()

        else: #recall main again, so the user can enter their username and password.
            main()

    #closing the socket.
    clientSocket.close()

if __name__ == "__main__":
    main()