from socket import *
from prettytable import PrettyTable
import json


def displayTransactions(transactions):
    table = PrettyTable()
    table.field_names = ['TX ID', 'Payer', 'Amount Transferred by Payer', 'Payee1', 'Amount Received by Payee1', 'Payee2', 'Amount Received by Payee2']

    for tx in transactions:
        tx_id = tx['tx_id']
        payer = tx['payer']
        amount_transferred = tx['amount_transferred']
        payee1 = tx['payee1']
        amount_received_payee1 = tx['amount_received_payee1']
        payee2 = tx.get('payee2', None)
        amount_received_payee2 = tx.get('amount_received_payee2', None)

        table.add_row([tx_id, payer, amount_transferred, payee1, amount_received_payee1, payee2, amount_received_payee2])

    print(table)


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
        print(f'Balance: {decodedResponse['balance']} BTC')

        #storing the balance and the transactions
        balance = decodedResponse['balance']
        transactions = decodedResponse['txs']

        displayTransactions(transactions)

        choice = input('Choose one of the following options?\n'
                       '(1) Make a transaction.\n'
                       '(2) Fetch and display the list of transactions.\n'
                       '(3) Quit the program.\n'
                       'Enter your choice: ')
        
        if choice == '1':
            tx = {}
            tx['tx_id'] = decodedResponse['tx_id']
            tx['payer'] = username

            amount_transferred = float(input('How much do you transfer? '))

            while amount_transferred > balance:
                print(f'Please enter a value less than or equal to {balance}.')
                amount_transferred = float(input('How much do you transfer? '))

            tx['amount_transferred'] = amount_transferred

            payee1_cases = []
            if username == 'A':
                payee1_cases = ['B', 'C', 'D']

            elif username == 'B':
                payee1_cases = ['A', 'C', 'D']

            elif username == 'C':
                payee1_cases = ['A', 'B', 'D']

            elif username == 'D':
                payee1_cases = ['A', 'B', 'C']

            print('Who will be Payee1?')
            for i, payee in enumerate(payee1_cases):
                print(f'{i}. {payee}')

            payee1 = input('Enter Payee1: ')
            tx['payee1'] = payee1

            amount_payee1 = float(input(f'How much will {payee1} receive? '))
            while amount_payee1 > amount_transferred:
                print(f'Please enter a value less than or equal to {amount_transferred}.')
                amount_payee1 = float(input(f'How much will {payee1} receive? '))

            tx['amount_received_payee1'] = amount_payee1

            if amount_transferred - amount_payee1 > 0:
                payee2_cases = [p for p in payee1_cases if p != payee1]

                print(f'Who will be Payee2?')
                for i, payee in enumerate(payee2_cases):
                    print(f'{i}. {payee}')

                payee2 = input("Enter Payee2: ")
                tx['payee2'] = payee2
                tx['amount_received_payee2'] = amount_transferred - amount_payee1
            
            transactions.append(tx)

            clientSocket.sendto(json.dumps({'action': 'make_transaction', 'transaction': tx}).encode(), (serverName, serverPort))
            response, serverAddress = clientSocket.recvfrom(2048)
            decodedResponse = json.loads(response.decode())

            if decodedResponse['status'] == 'confirmed':
                print(f'Transaction {tx['tx_id']} confirmed.')
                print(f'Updated Balance: {decodedResponse['balance']} BTC')
            
            else:
                print(f'Transaction {tx['tx_id']} rejected.')
                print(f'Current Balance: {decodedResponse['balance']} BTC')
        
        elif choice == '2':
            pass

        elif choice == '3': #terminate the program.
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

if __name__ == '__main__':
    main()