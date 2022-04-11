from asyncore import _socket
import socket

HOST = "127.0.0.1"  # localhost IP
PORT_TCP = 65432  # Hosting Port TCP ( > 1024 )

PORT_UDP = 65433  # Gato's UDP Port

# Returns the connected socket, connection and address
def createSocketTcp(): 
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp.bind((HOST, PORT_TCP))
    s_tcp.listen()
    conn, addr = s_tcp.accept()
    print("Connected with {addr}")
    return s_tcp, conn, addr 

def createSocketUdp():
    s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (HOST, PORT_UDP)
    return s_udp, addr

def checkStatusUdp(s_udp : _socket, addr : tuple):
    # Sending
    print("Mandando check de estado a Gato con dirreción {addr}")
    s_udp.sendto("STATUS", addr)
    # Receiving
    print("Esperando respuesta STATUS de Gato")
    data, server = s_udp.recvfrom(1024)
    data = data.decode('ascii')
    print("Recivido {data}")
    return data

def main():
    s_tcp, conn, addr = createSocketTcp()
    s_udp, addr = createSocketUdp()
    while True:
        data = conn.recv(1024).decode('ascii') # TCP Request to Play
        if data == "1": # Jugar
            res = checkStatusUdp(s_udp, addr) # UDP Status Request
            conn.sendall(res.encode("latin-1")) # TCP Response for Status
            if res == "OK":
                continue
            else:
                continue
        else: # Salir
            s_udp.close()
            s_tcp.close()
    return

if __name__ == '__main__':
    main()