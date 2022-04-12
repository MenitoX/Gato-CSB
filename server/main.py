import socket

HOST = "127.0.0.1"  # localhost IP
PORT_TCP = 65432  # Hosting Port TCP ( > 1024 )

PORT_UDP = 65433  # Gato's UDP Port

PLAYER = 1
BOT = 2

# Returns the connected socket, connection and address
def createSocketTcp(): 
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp.bind((HOST, PORT_TCP))
    s_tcp.listen()
    conn, addr = s_tcp.accept()
    print(f"Connected with {addr}")
    return s_tcp, conn, addr 

def notifSocketTcp(data, mode):
    if mode == "GET":
        print(f"Mensaje de socket TCP recivido con data : {data}")
    else:
        print(f"Mensaje de socket TCP enviado con data : {data}")

def notifSocketUdp(data, mode):
    if mode == "GET":
        print(f"Mensaje de socket UDP recivido con data : {data}")
    else:
        print(f"Mensaje de socket UDP enviado con data : {data}")

def createSocketUdp(port):
    s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (HOST, port)
    return s_udp, addr

def checkStatusUdp(s_udp, addr : tuple):
    # Sending
    print(f"Mandando check de estado a Gato con dirreción {addr}")
    s_udp.sendto(b"STATUS", addr)
    # Receiving
    print("Esperando respuesta STATUS de Gato")
    data, server = s_udp.recvfrom(1024)
    data = data.decode('ascii')
    print(f"Recivido {data}")
    return data

# Checks result, x and y are the curr play position and player is 0 -> bot , 1 -> client
def checkResult(board : list, x : str, y : str, player : int):
    x , y = int(x), int(y)
    n = PLAYER if player == PLAYER else BOT
    # Check space
    flag = True
    for row in board:
        for spot in row:
            if spot == 0:
                flag = False
    if flag:
        return -1 # DRAW
    # Check lines
    if board[0][x] == n and board[1][x] == n and board[2][x] == n:
        return n # n WINS
    elif board[y][0] == n and board[y][1] == n and board[y][2] == n:
        return n
    elif x+y != 3 and x+y != 1:
        if x == 1 and y == 1:
            if (board[0][0] == n and board[1][1] == n and  board[2][2] == n) or (board[2][0] == n and board[1][1] and board[0][2] == n):
                return n
        elif x+y == 2 and (board[2][0] == n and board[1][1] and board[0][2] == n):
            return n
        elif (x+y == 4 or x+y == 0) and (board[0][0] == n and board[1][1] == n and  board[2][2] == n):
            return n
    else:
        return 0 # NONE

def playRound(board : list, conn, udp_play_port : int):
    pos = conn.recv(1024).decode('ascii')
    notifSocketTcp(pos, "GET")
    x,y = pos.split(",")
    board[int(y)][int(x)] = PLAYER
    res = checkResult(board, x, y, PLAYER)
    send = ""
    if res == PLAYER:
        send = "WIN-{x},{y}"
        conn.sendall(send.encode("latin-1"))
        notifSocketTcp(send, "POST")
        return 0
    elif res == -1:
        send = "DRAW-{x},{y}"
        conn.sendall(send.encode("latin-1"))
        notifSocketTcp(send, "POST")
        return 0
    
    s_udp, addr = createSocketUdp(udp_play_port)
    topic = "PLAY-"+pos
    s_udp.sendall(topic.encode("latin-1"), addr)
    notifSocketUdp(topic, "POST")
    data, server = s_udp.recvfrom(1024)
    data = data.decode("ascii")
    notifSocketUdp(data, "GET")
    pos, port = data.split("-") #
    
    x,y = pos.split(",")
    board[int(y)][int(x)] = BOT
    res = checkResult(board, x, y, BOT)
    send = ""
    if res == BOT:
        send = "LOSE-{x},{y}"
        conn.sendall(send.encode("latin-1"))
        notifSocketTcp(send, "POST")
        s_udp.close()
        return 0
    elif res == 0:
        send = "NONE-{x},{y}"
        conn.sendall(send.encode("latin-1"))
        notifSocketTcp(send, "POST")
        s_udp.close()
        return port
    

def playGame(conn, udp_play_port : int):
    board = [[0,0,0], [0,0,0], [0,0,0]]
    while True:
        res = playRound(board, conn, udp_play_port)
        if not res:
            return  
        udp_play_port = res
            

def main():
    s_tcp, conn, addr = createSocketTcp()
    s_udp, addr = createSocketUdp(PORT_UDP)
    while True:
        data = conn.recv(1024).decode('ascii') # TCP Request to Play
        notifSocketTcp(data, "GET")
        if data == "1": # Jugar
            res,udp_play_port = checkStatusUdp(s_udp, addr).split(",") # UDP Status Request
            conn.sendall(res.encode("latin-1")) # TCP Response for Status
            notifSocketTcp(res, "POST")
            if res == "OK": # Play the game
                playGame(conn, int(udp_play_port))
                s_udp.sendall(b'EXIT', addr)
                notifSocketUdp('EXIT', "POST")
                s_udp.close()
                s_tcp.close()
            else:           # Exit
                s_udp.close()
                s_tcp.close()  
        else: # Salir
            s_udp.close()
            s_tcp.close()
    return

if __name__ == '__main__':
    main()