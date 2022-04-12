from asyncore import _socket
import socket

HOST = "127.0.0.1"  # server IP
PORT = 65432  # Server Port ( > 1024 )

PLAYER = 1
BOT = 2

# Returns client socket
def createSocket():
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp.connect((HOST, PORT))
    return s_tcp

# Returns game character from int
def returnCharacter(n : int):
    if n == PLAYER:
        return 'x'
    elif n == BOT:
        return 'o'
    else:
        return ' '

# Prints board
def printBoard(board : list):
    auxBoard = [(returnCharacter(pos) for pos in row) for row in board]
    print(". 0| 1 | 2 ")
    print("0 {board[0]}| {board[1]} | {board[2]}")
    print("---+---+---")
    print("1 {board[3]}| {board[4]} | {board[5]}")
    print("---+---+---")
    print("2 {board[6]}| {board[7]} | {board[8]}")
    return


def playTurn(s_tcp : _socket, board : list):
    printBoard(board)
    pos = input("Ingrese su jugada (x,y)")
    x,y = pos.strip().split(",")
    board[int(y)][int(x)] = PLAYER
    s_tcp.sendall(pos.encode('latin-1'))
    res,pos = s_tcp.recv(1024).decode('ascii').split("-") # Ej: WIN-2,1 , NONE-0,0
    x,y = pos.split(",")
    if res != "WIN" and res != "DRAW": # Only client can trigger a DRAW or a WIN
        board[int(y)][int(x)] = BOT
    # Server's_tcp possible responses
    if res == "WIN":
        print("---- YOU WIN! ----")
        print(board)
        return 1
    elif res == "LOSE":
        print("---- YOU LOSE ----")
        print(board)
        return 1
    elif res == "DRAW":
        print("---- IT'S A DRAW! ----")
        print(board)
        return 1
    else: 
        return 0

def playGame(s_tcp : _socket):
    print("--------Comienza el Juego--------")
    board = [[0,0,0], [0,0,0], [0,0,0]] # Init board
    while True: # TODO : Add error count to close connection ? 
        if playTurn(s_tcp , board): # Game ended
            res = ""
            while res != "1" and res != "2":
                res = input("- Seleccione una opción\n1-Jugar\n2-Salir")
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
        option = input("- Seleccione una opción\n1-Jugar\n2-Salir")
    s_tcp.sendall(option.encode('latin-1'))
    res = s_tcp.recv(1024).decode('ascii')
    if res == "OK":
        playGame(s_tcp)
        s_tcp.close()
        print("Gracias por jugar!")
    else:
        print("Conexión no disponible")
        s_tcp.close()    
    return

if __name__ == '__main__':
    main()