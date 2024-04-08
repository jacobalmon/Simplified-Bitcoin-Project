from socket import *
import json
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

#object for confirming or rejecting a transaction window.
class ConfirmRejectWidget(QMainWindow):
    #initialzing data to have access throughout the class.
    def __init__(self, username, balance, transactions, serverMessage, tx_id, clientSocket, serverName, serverPort):
        super().__init__()
        self.username = username
        self.balance = balance
        self.transactions = transactions
        self.serverMessage = serverMessage
        self.tx_id = tx_id
        self.clientSocket = clientSocket
        self.serverName = serverName
        self.serverPort = serverPort
        self.initUI()

    def initUI(self):
        #making the widget the central widget.
        central_widget = QWidget() 
        self.setCentralWidget(central_widget) 
        self.layout = QVBoxLayout(central_widget) 
    
        #checking if the message has been confimed, if so display the balance and that it has been confirmed.
        if self.serverMessage['status'] == 'confirmed':
            self.confrim_label = QLabel(f'User {self.username}\'s transaction has been confirmed.')
            self.confirm_balance = QLabel(f'User {self.username}\'s Balance: {self.balance} BTC.')
            self.layout.addWidget(self.confrim_label)
            self.layout.addWidget(self.confirm_balance)

        else:#rejection message displauys its been rejected and their current balance.
            self.reject_label = QLabel(f'User {self.username}\'s transaction has been rejected.')
            self.current_balance = QLabel(f'User {self.username}\'s Balance: {self.balance} BTC.')
            self.layout.addWidget(self.reject_label)
            self.layout.addWidget(self.current_balance)

        #creating button to go back to the main page.
        self.mainpage_button = QPushButton('Main Page')
        self.mainpage_button.clicked.connect(self.mainpage)
        self.layout.addWidget(self.mainpage_button)

    def mainpage(self): #if we go back to the main page, then we go to the authenication widget.
        self.parent().setCentralWidget(AuthenicationWidget(self.username, self.serverMessage, self.clientSocket, self.serverName, self.serverPort, self.transactions))
        self.close()


#object for make transaction option window.s
class TransactionWidget(QMainWindow):
    #initializing the data to have access throughout the class.
    def __init__(self, username, balance, transactions, tx_id, clientSocket, serverName, serverPort, response):
        super().__init__()
        self.username = username
        self.balance = balance
        self.transactions = transactions
        self.tx_id = tx_id
        self.clientSocket = clientSocket
        self.serverName = serverName
        self.serverPort = serverPort
        self.response = response
        self.initUI()

    def initUI(self):
        #creating window for make transaction.
        self.setWindowTitle('Make Transaction')
        self.setGeometry(100, 100, 800, 600)

        #creating balance label.
        self.balance_label = QLabel(f'Balance: {self.balance} BTC')

        #creating question label.
        self.amount_label = QLabel('How much BTC do you transfer?')
        self.input_amount = QLineEdit()
        self.input_amount.setPlaceholderText('Enter amount')

        #creating question label with a combo box.
        self.payee1_label = QLabel('Who will be Payee1?')
        self.input_payee1 = QComboBox()
        
        self.payee_options = ['Select One', 'A', 'B', 'C', 'D']
        self.payee_options.remove(self.username)
        self.input_payee1.addItems(self.payee_options)

        #payee1 labels and boxes for inputs.
        self.payee1_amount_label = QLabel('How much BTC do you transfer to Payee1?')
        self.input_payee1_amount = QLineEdit()
        self.input_payee1_amount.setPlaceholderText('Enter amount for Payee1')

        #button for submitting the transaction.
        self.submit_transaction_button = QPushButton('Submit Transaction')
        self.submit_transaction_button.clicked.connect(self.submit_transaction)

        #button for cancelling the transaction.
        self.cancel_transaction_button = QPushButton('Cancel Transaction')
        self.cancel_transaction_button.clicked.connect(self.cancel_transaction)

        #inserting all the widgets into the layout.
        self.transaction_layout = QVBoxLayout()
        self.transaction_layout.addWidget(self.balance_label)
        self.transaction_layout.addWidget(self.amount_label)
        self.transaction_layout.addWidget(self.input_amount)
        self.transaction_layout.addWidget(self.payee1_label)
        self.transaction_layout.addWidget(self.input_payee1)
        self.transaction_layout.addWidget(self.payee1_amount_label)
        self.transaction_layout.addWidget(self.input_payee1_amount)
        self.transaction_layout.addWidget(self.submit_transaction_button)
        self.transaction_layout.addWidget(self.cancel_transaction_button)

        #displaying the layout to the screen.
        self.temp_widget = QWidget()
        self.temp_widget.setLayout(self.transaction_layout)
        self.setCentralWidget(self.temp_widget)

    #if submit transaction has been clicked
    def submit_transaction(self):
        self.tx = {}
        self.tx['tx_id'] = self.tx_id
        self.tx['payer'] = self.username
        amount_transferred = self.input_amount.text()
        payee1 = self.input_payee1.currentText()
        amount_received_payee1 = self.input_payee1_amount.text()

        #checking edge case for if none of the following were entered.
        if not payee1 or not amount_received_payee1 or not amount_transferred:
            QMessageBox.critical(self, 'Error', 'Invalid Amount', QMessageBox.Ok)
            return
        
        self.tx['amount_transferred'] = float(amount_transferred)

        #checking edge case for payee1 amount being invalid.
        while float(amount_received_payee1) > self.tx['amount_transferred']:
            QMessageBox.critical(self, 'Error', 'Invalid Amount', QMessageBox.Ok)
            self.input_payee1_amount.clear()
            return

        self.tx['payee1'] = payee1
        self.tx['amount_received_payee1'] = float(amount_received_payee1)

        #avoid printing incorrect balance.
        if self.balance < self.tx['amount_transferred']:
            self.flag = True
        else:
            self.flag = False
            self.balance -= float(amount_received_payee1)

        self.payee_options.remove(payee1)

        #checking if payee2 exists.
        if self.tx['amount_transferred'] - self.tx['amount_received_payee1'] > 0:
            if hasattr(self, 'submit_transaction_button') and hasattr(self, 'cancel_transaction_button'):
                self.submit_transaction_button.deleteLater()
                self.cancel_transaction_button.deleteLater()

            #buttons, labels, for the payee2.
            self.payee2_label = QLabel('Who will be Payee2?')
            self.input_payee2 = QComboBox()
            self.input_payee2.addItems(self.payee_options)
            self.new_submit_transaction_button = QPushButton('Submit Transaction')
            self.new_submit_transaction_button.clicked.connect(self.send_transaction)
            self.new_cancel_transaction_button = QPushButton('Cancel Transaction')
            self.new_cancel_transaction_button.clicked.connect(self.cancel_transaction)

            #layout for the widgets.
            self.transaction_layout.addWidget(self.payee2_label)
            self.transaction_layout.addWidget(self.input_payee2)
            self.transaction_layout.addWidget(self.new_submit_transaction_button)
            self.transaction_layout.addWidget(self.new_cancel_transaction_button)

        else:
            self.send_transaction()

    def send_transaction(self): #sends the transactions to the widget.
        if hasattr(self, 'new_submit_transaction_button') and hasattr(self, 'new_cancel_transaction_button'):
            self.new_submit_transaction_button.close()
            self.new_cancel_transaction_button.close()

        if hasattr(self, 'input_payee2'):
            self.tx['payee2'] = self.input_payee2.currentText()
            self.tx['amount_received_payee2'] = self.tx['amount_transferred'] - self.tx['amount_received_payee1']
            if not self.flag:
                self.balance -= self.tx['amount_received_payee2']

        #sending requerst to the server.
        self.clientSocket.sendto(json.dumps({'action': 'make_transaction', 'transaction': self.tx}).encode(), (self.serverName, self.serverPort))
        response, serverAddress = self.clientSocket.recvfrom(2048)
        decodedResponse = json.loads(response.decode())
        
        #setting new swindow the the confirm or reject widget.
        messageWidget = ConfirmRejectWidget(self.username, self.balance, self.transactions, decodedResponse, self.tx_id, self.clientSocket, self.serverName, self.serverPort)
        self.setCentralWidget(messageWidget)

    def cancel_transaction(self): #cancel transaction goes back to the options window.
        self.parent().setCentralWidget(AuthenicationWidget(self.username, self.response, self.clientSocket, self.serverName, self.serverPort, self.transactions))
        self.close()


#object for options to where make transaction, fetch table, or quit onto the screen.
class AuthenicationWidget(QMainWindow):
    #intialzing data to have access throughout the class.
    def __init__(self, username, response, clientSocket, serverName, serverPort, transactions):
        super().__init__()
        self.username = username
        self.balance = response['balance']
        self.transactions = response.get('txs', transactions)
        self.tx_id = response.get('tx_id', '')
        self.clientSocket = clientSocket
        self.serverName = serverName
        self.serverPort = serverPort
        self.response = response
        self.initUI()

    def initUI(self):
        #creating the window geometry.
        self.setWindowTitle('Authenticated - Simplified Bitcoin')
        self.setGeometry(100, 100, 800, 600)

        #creating labels for user and balance.
        self.user_authenicated = QLabel(f'User {self.username} is authenicated.')
        self.user_balance = QLabel(f'Balance: {self.balance} BTC')

        #creating the table for the transactions.
        self.user_transaction_table = QTableWidget()
        self.user_transaction_table.setColumnCount(7)
        self.user_transaction_table.setHorizontalHeaderLabels(['TX ID', 'Payer', 'Amount Transferred by Payer', 'Payee1', 'Amount Received by Payee1', 'Payee2', 'Amount Received by Payee2'])

        self.user_transaction_table.setColumnWidth(0, 100)  #TX ID
        self.user_transaction_table.setColumnWidth(1, 150)  #Payer
        self.user_transaction_table.setColumnWidth(2, 220)  #Amount Transferred by Payer
        self.user_transaction_table.setColumnWidth(3, 150)  #Payee1
        self.user_transaction_table.setColumnWidth(4, 220)  #Amount Received by Payee1
        self.user_transaction_table.setColumnWidth(5, 150)  #Payee2
        self.user_transaction_table.setColumnWidth(6, 220)  #Amount Received by Payee2

        self.table()

        #creating buttons for the make transaction and fetch and display.
        self.make_transaction_button = QPushButton('Make Transaction')
        self.make_transaction_button.clicked.connect(self.make_transaction)

        self.fetch_and_display_button = QPushButton('Fetch and Display Table')
        self.fetch_and_display_button.clicked.connect(self.fetch_and_display)
        
        #button for logging out.
        self.logout = QPushButton('Logout')
        self.logout.clicked.connect(self.quit)

        #layout for the authenication layout to display to the screen.
        self.authenication_layout = QVBoxLayout()
        self.authenication_layout.addWidget(self.user_authenicated)
        self.authenication_layout.addWidget(self.user_balance)
        self.authenication_layout.addWidget(self.user_transaction_table)
        self.authenication_layout.addWidget(self.make_transaction_button)
        self.authenication_layout.addWidget(self.fetch_and_display_button)
        self.authenication_layout.addWidget(self.logout)
        
        #setting it as the central widget.
        self.authenticated_widget = QWidget()
        self.authenticated_widget.setLayout(self.authenication_layout)
        self.setCentralWidget(self.authenticated_widget)
        self.show()

    def make_transaction(self): #creates the transaction window.
        make_transaction_window = TransactionWidget(self.username, self.balance, self.transactions, self.tx_id, self.clientSocket, self.serverName, self.serverPort, self.response)
        self.setCentralWidget(make_transaction_window)

    def fetch_and_display(self): #displays the table of transactions.
         # Send a request to the server to fetch the user's current balance and transactions
        self.clientSocket.sendto(json.dumps({'action': 'fetch_transactions', 'username': self.username}).encode(), (self.serverName, self.serverPort))

         # Receive response from the server
        response, serverAddress = self.clientSocket.recvfrom(2048)
        decodedResponse = json.loads(response.decode())

        # Update the list of transactions with the new list received from the server.
        self.transactions = decodedResponse['txs']
    
        # Update the table widget with the new transactions
        self.table()
          
    def quit(self): #quits the tranaction page, back to login.
        self.parent().setCentralWidget(GUI())
        self.close()

    def table(self): #function for displaying the table.
        self.user_transaction_table.setRowCount(len(self.transactions))
        for i, tx in enumerate(self.transactions):
            self.user_transaction_table.setItem(i, 0, QTableWidgetItem(str(tx['tx_id'])))
            self.user_transaction_table.setItem(i, 1, QTableWidgetItem(tx['payer']))
            self.user_transaction_table.setItem(i, 2, QTableWidgetItem(str(tx['amount_transferred'])))
            self.user_transaction_table.setItem(i, 3, QTableWidgetItem(tx['payee1']))
            self.user_transaction_table.setItem(i, 4, QTableWidgetItem(str(tx['amount_received_payee1'])))
            self.user_transaction_table.setItem(i, 5, QTableWidgetItem(tx.get('payee2', '')))
            self.user_transaction_table.setItem(i, 6, QTableWidgetItem(str(tx.get('amount_received_payee2', '')))) 

#object for the login page of the interface.
class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        #setting window.
        self.setWindowTitle('Simplified Bitcoin')
        self.setGeometry(100, 100, 1280, 800)

        #css code styling all the widgets.
        self.setStyleSheet("""
                QMainWindow {
                    background-color: #f0f0f0;
                }
                           
                QWidget {
                    background-color: #f0f0f0;
                }

                QLabel {
                    font-size: 30px;
                    margin-bottom: 20px;
                }

                QPushButton {
                    background-color: #007BFF;
                    color: white;
                    padding: 10px 20px;
                    font-size: 16px;
                    border-radius: 5px;
                }
                 
                QPushButton:hover {
                    background-color: #0056b3;
                }
                           
                QLineEdit {
                    padding: 10px;
                    font-size: 16px;
                    border: 1px solid #007BFF;
                    border-radius: 5px;
                }
                           
                QLineEdit:focus {
                    border-color: #0056b3;
                    border-radius: 15px;
                }
                           
                QTableWidget {
                    background-color: white;
                    border: 1px solid #007BFF;
                    gridline-color: #007BFF;
                    margin: 5px;
                }

                QTableWidget::item {
                    padding: 5px;
                    border: none;
                }

                QHeaderView::section {
                    background-color: #f0f0f0;
                    padding: 5px;
                    border: 1px solid #007BFF;
                    font-size: 16px;
                }

                QComboBox {
                    padding: 10px;
                    font-size: 16px;
                    border: 1px solid #007BFF;
                    border-radius: 5px;
                }
                           
                QComboBox:focus {
                    border-color: #0056b3
                    border-radius: 15px;
                }
                
                QComboBox::drop-down {
                    border: none;
                }
                           
                QToolTip {
                    background-color: #007BFF;
                    color: white;
                    border: none;
                }
                 """)
        
        #login label.
        self.login = QLabel('Login')

        #input boxes, and buttons for the interface.
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText('Username')

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText('Password')
        #Uncomment to have password hidden when entered.
        #self.input_password.setEchoMode(QLineEdit.Password)
        
        self.login_button = QPushButton('Login')
        self.login_button.clicked.connect(self.authenicate_user)

        self.exit_button = QPushButton('Exit')
        self.exit_button.clicked.connect(self.quit_app)

        #creating the layout for the all widgets.
        login_layout = QVBoxLayout()
        login_layout.addWidget(self.login, alignment=Qt.AlignCenter)
        login_layout.addWidget(self.input_username)
        login_layout.addWidget(self.input_password)
        login_layout.addWidget(self.login_button)
        login_layout.addWidget(self.exit_button)

        #putting the widgets into the screen.
        main_widget = QWidget()
        main_widget.setLayout(login_layout)
        self.setCentralWidget(main_widget)
        self.show()

        #setting servername, port, and creating the socket.
        self.serverName = 'localhost'
        self.serverPort = 12000
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)

    def quit_app(self): #ends the interface app.
        self.clientSocket.close()
        QApplication.exit()

    def authenicate_user(self):
        #getting keyboard input from the client.
        username = self.input_username.text()
        password = self.input_password.text()

        #created hashmap/dictionary to store username and password.
        data = {'username': username, 'password': password}

        #sending username and password to the server.
        self.clientSocket.sendto(json.dumps(data).encode(), (self.serverName, self.serverPort))

        #receiving response and address from the server.
        response, serverAddress = self.clientSocket.recvfrom(2048)
        self.decodedResponse = json.loads(response.decode())

        if self.decodedResponse['authenticated']: #create window to the options menu.
            self.authenicated_window = AuthenicationWidget(username, self.decodedResponse, self.clientSocket, self.serverName, self.serverPort, self.decodedResponse['txs'])
            self.setCentralWidget(self.authenicated_window)

        else:
            QMessageBox.critical(self, 'Error', 'Invalid Credentials', QMessageBox.Ok)
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GUI()
    sys.exit(app.exec_())