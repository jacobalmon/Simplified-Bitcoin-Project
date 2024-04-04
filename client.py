from socket import *
import json
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class ConfirmRejectWidget(QMainWindow):
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
        central_widget = QWidget() 
        self.setCentralWidget(central_widget) 
        self.layout = QVBoxLayout(central_widget) 
        if self.serverMessage['status'] == 'confirmed':
            self.confrim_label = QLabel(f'User {self.username}\'s transaction has been confirmed.')
            self.confirm_balance = QLabel(f'User {self.username}\'s Balance: {self.balance} BTC.')
            self.layout.addWidget(self.confrim_label)
            self.layout.addWidget(self.confirm_balance)
        else:
            self.reject_label = QLabel(f'User {self.username}\'s transaction has been rejected.')
            self.current_balance = QLabel(f'User {self.username}\'s Balance: {self.balance} BTC.')
            self.layout.addWidget(self.reject_label)
            self.layout.addWidget(self.current_balance)

        self.mainpage_button = QPushButton('Main Page')
        self.mainpage_button.clicked.connect(self.mainpage)
        self.layout.addWidget(self.mainpage_button)

    def mainpage(self):
        self.parent().setCentralWidget(AuthenicationWidget(self.username, self.serverMessage, self.clientSocket, self.serverName, self.serverPort, self.transactions))
        self.close()


class TransactionWidget(QMainWindow):
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
        self.setWindowTitle('Make Transaction')
        self.setGeometry(100, 100, 800, 600)

        self.balance_label = QLabel(f'Balance: {self.balance} BTC')

        self.amount_label = QLabel('How much BTC do you transfer?')
        self.input_amount = QLineEdit()
        self.input_amount.setPlaceholderText('Enter amount')

        self.payee1_label = QLabel('Who will be Payee1?')
        self.input_payee1 = QComboBox()
        
        self.payee_options = ['Select One', 'A', 'B', 'C', 'D']
        self.payee_options.remove(self.username)
        self.input_payee1.addItems(self.payee_options)

        self.payee1_amount_label = QLabel('How much BTC do you transfer to Payee1?')
        self.input_payee1_amount = QLineEdit()
        self.input_payee1_amount.setPlaceholderText('Enter amount for Payee1')

        self.submit_transaction_button = QPushButton('Submit Transaction')
        self.submit_transaction_button.clicked.connect(self.submit_transaction)

        self.cancel_transaction_button = QPushButton('Cancel Transaction')
        self.cancel_transaction_button.clicked.connect(self.cancel_transaction)

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

        self.temp_widget = QWidget()
        self.temp_widget.setLayout(self.transaction_layout)
        self.setCentralWidget(self.temp_widget)


    def submit_transaction(self):
        self.tx = {}
        self.tx['tx_id'] = self.tx_id
        self.tx['payer'] = self.username
        amount_transferred = self.input_amount.text()
        payee1 = self.input_payee1.currentText()
        amount_received_payee1 = self.input_payee1_amount.text()

        if not payee1 or not amount_received_payee1 or not amount_transferred:
            QMessageBox.critical(self, 'Error', 'Invalid Amount', QMessageBox.Ok)
            return


        while float(amount_transferred) > self.balance or float(amount_transferred) < 0:
            QMessageBox.critical(self, 'Error', 'Invalid Amount', QMessageBox.Ok)
            self.input_amount.clear()
            return

        self.tx['amount_transferred'] = float(amount_transferred)

        while float(amount_received_payee1) > self.tx['amount_transferred']:
            QMessageBox.critical(self, 'Error', 'Invalid Amount', QMessageBox.Ok)
            self.input_payee1_amount.clear()
            return

        self.tx['payee1'] = payee1
        self.tx['amount_received_payee1'] = float(amount_received_payee1)
        self.balance -= float(amount_received_payee1)
        self.payee_options.remove(payee1)

        if self.tx['amount_transferred'] - self.tx['amount_received_payee1'] > 0:
            if hasattr(self, 'submit_transaction_button') and hasattr(self, 'cancel_transaction_button'):
                self.submit_transaction_button.deleteLater()
                self.cancel_transaction_button.deleteLater()

            self.payee2_label = QLabel('Who will be Payee2?')
            self.input_payee2 = QComboBox()
            self.input_payee2.addItems(self.payee_options)
            self.new_submit_transaction_button = QPushButton('Submit Transaction')
            self.new_submit_transaction_button.clicked.connect(self.send_transaction)
            self.new_cancel_transaction_button = QPushButton('Cancel Transaction')
            self.new_cancel_transaction_button.clicked.connect(self.cancel_transaction)

            self.transaction_layout.addWidget(self.payee2_label)
            self.transaction_layout.addWidget(self.input_payee2)
            self.transaction_layout.addWidget(self.new_submit_transaction_button)
            self.transaction_layout.addWidget(self.new_cancel_transaction_button)

        else:
            self.send_transaction()

    def send_transaction(self):
        if hasattr(self, 'new_submit_transaction_button') and hasattr(self, 'new_cancel_transaction_button'):
            self.new_submit_transaction_button.close()
            self.new_cancel_transaction_button.close()

        if hasattr(self, 'input_payee2'):
            self.tx['payee2'] = self.input_payee2.currentText()
            self.tx['amount_received_payee2'] = self.tx['amount_transferred'] - self.tx['amount_received_payee1']
            self.balance -= self.tx['amount_received_payee2']
            
        self.transactions.append(self.tx)

        self.clientSocket.sendto(json.dumps({'action': 'make_transaction', 'transaction': self.tx}).encode(), (self.serverName, self.serverPort))
        response, serverAddress = self.clientSocket.recvfrom(2048)
        decodedResponse = json.loads(response.decode())

        messageWidget = ConfirmRejectWidget(self.username, self.balance, self.transactions, decodedResponse, self.tx_id, self.clientSocket, self.serverName, self.serverPort)
        self.setCentralWidget(messageWidget)

    def cancel_transaction(self):
        self.parent().setCentralWidget(AuthenicationWidget(self.username, self.response, self.clientSocket, self.serverName, self.serverPort, self.transactions))
        self.close()


class AuthenicationWidget(QMainWindow):
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
        self.setWindowTitle('Authenticated - Simplified Bitcoin')
        self.setGeometry(100, 100, 800, 600)

        self.user_authenicated = QLabel(f'User {self.username} is authenicated.')
        self.user_balance = QLabel(f'Balance: {self.balance} BTC')

        self.user_transaction_table = QTableWidget()
        self.user_transaction_table.setColumnCount(7)
        self.user_transaction_table.setHorizontalHeaderLabels(['TX ID', 'Payer', 'Amount Transferred by Payer', 'Payee1', 'Amount Received by Payee1', 'Payee2', 'Amount Received by Payee2'])

        self.user_transaction_table.setRowCount(len(self.transactions))
        for i, tx, in enumerate(self.transactions):
            self.user_transaction_table.setItem(i, 0, QTableWidgetItem(str(tx['tx_id'])))
            self.user_transaction_table.setItem(i, 1, QTableWidgetItem(tx['payer']))
            self.user_transaction_table.setItem(i, 2, QTableWidgetItem(str(tx['amount_transferred'])))
            self.user_transaction_table.setItem(i, 3, QTableWidgetItem(tx['payee1']))
            self.user_transaction_table.setItem(i, 4, QTableWidgetItem(str(tx['amount_received_payee1'])))
            self.user_transaction_table.setItem(i, 5, QTableWidgetItem(tx.get('payee2', '')))
            self.user_transaction_table.setItem(i, 6, QTableWidgetItem(str(tx.get('amount_received_payee2', ''))))

        self.user_transaction_table.setColumnWidth(0, 100)  # TX ID
        self.user_transaction_table.setColumnWidth(1, 150)  # Payer
        self.user_transaction_table.setColumnWidth(2, 220)  # Amount Transferred by Payer
        self.user_transaction_table.setColumnWidth(3, 150)  # Payee1
        self.user_transaction_table.setColumnWidth(4, 220)  # Amount Received by Payee1
        self.user_transaction_table.setColumnWidth(5, 150)  # Payee2
        self.user_transaction_table.setColumnWidth(6, 220)  # Amount Received by Payee2

        self.make_transaction_button = QPushButton('Make Transaction')
        self.make_transaction_button.clicked.connect(self.make_transaction)

        self.fetch_and_display_button = QPushButton('Fetch & Display Table')
        self.fetch_and_display_button.clicked.connect(self.fetch_and_display)

        self.logout = QPushButton('Logout')
        self.logout.clicked.connect(self.quit)

        self.authenication_layout = QVBoxLayout()
        self.authenication_layout.addWidget(self.user_authenicated)
        self.authenication_layout.addWidget(self.user_balance)
        self.authenication_layout.addWidget(self.user_transaction_table)
        self.authenication_layout.addWidget(self.make_transaction_button)
        self.authenication_layout.addWidget(self.fetch_and_display_button)
        self.authenication_layout.addWidget(self.logout)
        
        self.authenticated_widget = QWidget()
        self.authenticated_widget.setLayout(self.authenication_layout)
        self.setCentralWidget(self.authenticated_widget)
        self.show()

    def make_transaction(self):
        make_transaction_window = TransactionWidget(self.username, self.balance, self.transactions, self.tx_id, self.clientSocket, self.serverName, self.serverPort, self.response)
        self.setCentralWidget(make_transaction_window)

    def fetch_and_display(self):
        pass #do not implement yet.

    def quit(self):
        self.parent().setCentralWidget(GUI())
        self.close()


class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Simplified Bitcoin')
        self.setGeometry(100, 100, 1280, 800)
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
        
        self.login = QLabel('Login')

        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText('Username')

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText('Password')
        self.input_password.setEchoMode(QLineEdit.Password)
        
        self.login_button = QPushButton('Login')
        self.login_button.clicked.connect(self.authenicate_user)

        self.exit_button = QPushButton('Exit')
        self.exit_button.clicked.connect(self.quit_app)

        login_layout = QVBoxLayout()
        login_layout.addWidget(self.login, alignment=Qt.AlignCenter)
        login_layout.addWidget(self.input_username)
        login_layout.addWidget(self.input_password)
        login_layout.addWidget(self.login_button)
        login_layout.addWidget(self.exit_button)

        main_widget = QWidget()
        main_widget.setLayout(login_layout)
        self.setCentralWidget(main_widget)
        self.show()

        self.serverName = 'localhost'
        self.serverPort = 12000
        self.clientSocket = socket(AF_INET, SOCK_DGRAM)

    def quit_app(self):
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

        if self.decodedResponse['authenticated']:
            self.authenicated_window = AuthenicationWidget(username, self.decodedResponse, self.clientSocket, self.serverName, self.serverPort, self.decodedResponse['txs'])
            self.setCentralWidget(self.authenicated_window)

        else:
            QMessageBox.critical(self, 'Error', 'Invalid Credentials', QMessageBox.Ok)
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GUI()
    sys.exit(app.exec_())