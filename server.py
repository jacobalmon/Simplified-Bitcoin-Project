from socket import *
import json
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

#object for the server.
class Server(QThread):
    #used for server messages.
    signal = pyqtSignal(str)

    def __init__(self, users):
        super().__init__()
        self.users = users #possible users.
        self.serverSocket = socket(AF_INET, SOCK_DGRAM) #creating a UDP socket
        self.serverSocket.bind(('', 12000)) #binding the port.
        self.running = False #set as not running for now.

    def run(self):
        self.running = True #runs server infinitely, unless stopped.

        while self.running:
            #read from socket into message and get the clients address.
            message, clientAddress = self.serverSocket.recvfrom(2048)
            decodedMessage = json.loads(message.decode())

            if 'username' in decodedMessage and 'password' in decodedMessage:
                #receiving username and password from the client.
                username = decodedMessage['username']
                password = decodedMessage['password']
                #printing server message.
                self.signal.emit(f'Received Authentication Request from User {username}.')

                #using hashmap/dictionary for server response.
                response = {}

                #checking if the username is valid and if their password is correct.
                if username in self.users and self.users[username]['password'] == password:
                    response['authenticated'] = True
                    response['tx_id'] = self.users[username]['tx_id']
                    response['balance'] = self.users[username]['balance']
                    response['txs'] = self.users[username]['txs']
                    #printing server message.
                    self.signal.emit(f'User {username} is Authenicated.')

                else:
                    response['authenticated'] = False
                    #printing server message.
                    self.signal.emit(f'User {username} is not Authenicated.')

                #sending the server response back to the client.
                self.serverSocket.sendto(json.dumps(response).encode(), clientAddress)
            
            elif 'action' in decodedMessage and decodedMessage['action'] == 'make_transaction':
                tx = decodedMessage['transaction']
                payer = tx['payer']
                amount_transferred = tx['amount_transferred']
                payee1 = tx['payee1']
                amount_received_payee1 = tx['amount_received_payee1']
                payee2 = tx.get('payee2', None)
                amount_received_payee2 = tx.get('amount_received_payee2', None)

                #using hashmap/dictionary for server response.
                response = {}

                #printing server message
                self.signal.emit(f'Received Make Transaction request from user {username}.')

                #checking if you don't have enough BTC.
                if self.users[payer]['balance'] < amount_transferred:
                    #setting response to client.
                    response['status'] = 'rejected'
                    response['balance'] = self.users[payer]['balance']

                    #printing error messages.
                    self.signal.emit(f'User {username}\'s Make Transaction Request Rejected.')
                    self.signal.emit(f'User {username}\'s Balance is {self.users[payer]['balance']} BTC.')
                else:
                    #setting response to client.
                    response['status'] = 'confirmed'
                    response['balance'] = self.users[payer]['balance'] - amount_transferred

                    #updating users information in the hashmap/dictionary.
                    self.users[payer]['balance'] -= amount_transferred
                    self.users[payer]['txs'].append(tx)
                    self.users[payee1]['txs'].append(tx)
                    self.users[payer]['tx_id'] += 1
                    response['tx_id'] = self.users[payer]['tx_id'] #used for multiple transactions by the same user.
                    self.users[payee1]['balance'] += amount_received_payee1
                    
                    if payee2: #checks if there is a second payee, if so update the hashmap.
                        self.users[payee2]['balance'] += amount_received_payee2
                        self.users[payee2]['txs'].append(tx)

                    #printing server messages.
                    self.signal.emit(f'User {username}\'s Make Transaction Request Confirmed.')
                    self.signal.emit(f'User {username}\'s Balance is {response['balance']} BTC.')
                    self.signal.emit(f'Sending User {username} their Transactions.')
                #sending the client, the server response.
                self.serverSocket.sendto(json.dumps(response).encode(), clientAddress)
                
            elif True:
                pass

    def close(self): #when server has been stopped.
        self.running = False


#object for the interface.
class GUI(QWidget): 
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        #setting window title and size.
        self.setWindowTitle('Simplified Bitcoin')
        self.setGeometry(100, 100, 400, 500)

        #default information for all users in the system.
        self.users = { 
            'A': {'password': 'A', 'balance': 10, 'txs': [], 'tx_id': 100},
            'B': {'password': 'B', 'balance': 10, 'txs': [], 'tx_id': 200},
            'C': {'password': 'C', 'balance': 10, 'txs': [], 'tx_id': 300},
            'D': {'password': 'D', 'balance': 10, 'txs': [], 'tx_id': 400}
        }

        #css code implemented for a modern looking interface.
        self.setStyleSheet("""
                 QWidget {
                    background-color: #f0f0f0;
                 }

                 QLabel {
                    font-size: 18px;
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
                           
                QPlainTextEdit {
                    font-size: 16px;     
                }
                 """)
        
        #label for the server status, whether it's running or not, by default set it to the server name.
        self.server_status = QLabel('Simplified Bitcoin Server', self)

        #creating start server button and connecting it to function to start the server.
        self.start_button = QPushButton('Start Server', self)
        self.start_button.clicked.connect(self.start_server)
        
        #creating stop server button and connecting it to function to stop the server.
        self.stop_button = QPushButton('Stop Server', self)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_server)

        #creating button to exit the server program.
        self.exit_button = QPushButton('Exit', self)
        self.exit_button.clicked.connect(self.exit_app)
        
        #creating a server log to keep track of what the server is receiving from the user.
        self.serverlog_label = QLabel('Server Log')
        self.serverlog = QPlainTextEdit(self)
        self.serverlog.setReadOnly(True)
        self.serverlog.setPlaceholderText('Server Messages')

        #creating the layout for the window to be displayed.
        server_layout = QVBoxLayout()
        server_layout.addWidget(self.server_status, alignment=Qt.AlignCenter)
        server_layout.addWidget(self.start_button)
        server_layout.addWidget(self.stop_button)
        server_layout.addWidget(self.exit_button)
        server_layout.addWidget(self.serverlog)
        server_layout.addWidget(self.serverlog_label, alignment=Qt.AlignCenter)

        #setting it as the current layout and displaying to the window.
        self.setLayout(server_layout)
        self.show()

        #creating a server object to update the server log and overall logic of the server.
        self.server = Server(self.users)
        self.server.signal.connect(self.update_serverlog)

    def update_status(self, status):
        #updates the status of the server.
        self.server_status.setText(status)

    def start_server(self):
        #starts the server.
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.server.start()
        self.update_status('Server is running...')

    def stop_server(self):
        #stops the server.
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.server.close()
        self.update_status('Server stopped.')

    def exit_app(self):
        #checks if the server is running, and stops it, so the server isn't running forever.
        if self.server.running:
            self.stop_server()
        #closing the application.
        self.close()

    def update_serverlog(self, text):
        #edits the servrlog by adding the new server message.
        current = self.serverlog.toPlainText()
        if current:
            new = f'{current}\n{text}'
        else:
            new = text

        self.serverlog.setPlainText(new)
        self.serverlog.verticalScrollBar().setValue(self.serverlog.verticalScrollBar().maximum())


#main function for creating the interface
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GUI()
    sys.exit(app.exec_())