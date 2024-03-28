from socket import *

if __name__ == '__main__':
    serverName = 'localhost'
    serverPort = 12000

    #creating UDP socket for the client.
    clientSocket = socket(AF_INET, SOCK_DGRAM)

    #getting keyboard input from the client.
    username = input("Enter username: ")
    password = input("Enter password: ")

    clientSocket.sendto(username.encode(), serverName, serverPort)
    clientSocket.sendto(password.encode(), serverName, serverPort)