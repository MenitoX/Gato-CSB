from asyncore import _socket
import socket

HOST = "127.0.0.1"  # server IP
PORT = 65432  # Server Port ( > 1024 )

# Returns client socket
def createSocket():
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp.connect((HOST, PORT))
    return s_tcp

# Returns game character from int
def returnCharacter(n : int):
    if n == 1:
        return 'x'
    elif n == 2:
        return 'o'
    else:
        return ' '

# Prints board
def printBoard(board : list):
    auxBoard = [(returnCharacter(pos) for pos in row) for row in board]
    print(". 0| 1 | 2 \n")
    print("0 {board[0]}| {board[1]} | {board[2]}\n")
    print("---+---+---\n")
    print("1 {board[3]}| {board[4]} | {board[5]}\n")
    print("---+---+---\n")
    print("2 {board[6]}| {board[7]} | {board[8]}\n")
    return


def playTurn(s_tcp : _socket, board : list):
    printBoard(board)
    pos = input("Ingrese su jugada (x,y)\n")
    x,y = pos.strip().split(",")
    board[int(x)][int(y)] = 1
    s_tcp.sendall(pos.encode('latin-1'))
    res = s_tcp.recv(1024).decode('ascii')
    # Server's_tcp possible responses
    if res == "WIN":
        print("YOU WIN!")
        return 1
    elif res == "LOSE":
        print("YOU LOSE")
        return 1
    elif res == "DRAW":
        print("IT'S A DRAW!")
        return 1
    else: 
        x,y = res.split(",")
        board[int(x)][int(y)] = 2
        return 0

def playGame(s_tcp : _socket):
    print("--------Comienza el Juego--------")
    board = [[0,0,0], [0,0,0], [0,0,0]] # Init board
    while True: # TODO : Add error count to close connection ? 
        if playTurn(s_tcp , board): # Game ended
            res = ""
            while res != "1" and res != "2":
                res = input("- Seleccione una opción\n1-Jugar\n2-Salir\n")
                s_tcp.sendall(res.encode('latin-1'))
                res = s_tcp.recv(1024).decode('ascii')
                if res == "OK":
                    playGame(s_tcp)
                else:
                    return

def main():
    print("-------- Bienvenido al Juego --------")
    s_tcp = createSocket()
    #option = int(input(("- Seleccione una opción\n1-Jugar\n2-Salir")))
    #s_tcp.sendall(bin(option))
    option = ""
    while option != "1" and option != "2":
        option = input("- Seleccione una opción\n1-Jugar\n2-Salir\n")
    s_tcp.sendall(option.encode('latin-1'))
    res = s_tcp.recv(1024).decode('ascii')
    if res == "OK":
        playGame(s_tcp)
        s_tcp.close()
        print("Gracias por jugar!\n")
    else:
        print("Conexión no disponible")
        s_tcp.close()    
    return

if __name__ == '__main__':
    main()