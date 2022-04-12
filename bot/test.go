package main

import(
	"fmt"
	"math/rand"
	"strconv"
	"net"
)

func N_PORT(){
	int N_PORT= rand.int(57535)+8000
	if N_PORT==65433{
		N_PORT=N_PORT()
	}
	return N_PORT
}//listo

func MAKE_MOVE(tablero[3][3]){
	x = rand.int(2)
	y = rand.int(2)
	if tablero[y][x]!=0{
		MAKE_MOVE(tablero)
	}
	return x, y
}//listo

func READ_MSG(buffer,connection){
	n, addr, _ := connection.ReadFromUDP(buffer)

	msg := string(buffer[:n])

	return msg, addr
}//listo

func SEND_MSG(msg,addr,connection){

	//traducir a binario
	connection.WriteToUDP([]byte(msg),addr)
}//listo


func N_CONNECTION_O(N_PORT){
	
	PORT := ":"+strconv.Itoa(N_PORT)
	BUFFER := 1024
	s, err := net.ResolveUDPAddr("udp4", PORT)

	if err != nil {
		fmt.Println(err)
		return
	}

	n_connection, err := net.ListenUDP("udp4", s)
	if err != nil {
		fmt.Println(err)
		return
	}

	return n_connection
}

func N_CONNECTION_C(n_connection){
	defer n_connection.Close()
}

func main(){

	PORT := ":65433"
	BUFFER := 1024
	s, err := net.ResolveUDPAddr("udp4", PORT)
	if err != nil {
			fmt.Println(err)
			return
		}
	connection, err := net.ListenUDP("udp4", s)
	if err != nil {
		fmt.Println(err)
		return
	}
	
	buffer := make([]byte, BUFFER)

	
	msg, addr=READ_MSG(buffer,connection)
	for {
		if msg != "STATUS"{break}
		N_PORT = N_PORT()
		n_connection = N_CONNECTION_O(N_PORT)
		tablero = [3][3]int{
			{0,0,0},
			{0,0,0},
			{0,0,0}
		}
		_,_ = SEND_MSG("OK,"+strconv.Itoa(N_PORT),addr,connection)
		
		for{//aqui empiezan las jugadas
			msg,addr1=READ_MSG(buffer,n_connection)
			if msg[:4]!="PLAY"{break}
			jugada = msg[5:8]
			x=strconv.Atoi(jugada[0])
			y=strconv.Atoi(jugada[2])
			tablero[y][x]=1

			x,y=MAKE_MOVE(tablero)
			tablero[y][x]=2

			N_PORT=N_PORT() 
			_,_ = SEND_MSG(strconv.Itoa(x)+","+strconv.Itoa(y)+"-"+strconv.Itoa(N_PORT),addr1,n_connection)
			N_CONNECTION_C()
			n_connection = N_CONNECTION_O(N_PORT)	
		}//listo
		
	}
	_,_ = SEND_MSG("OK",addr,connection)
	N_CONNECTION_C(n_connection)
	N_CONNECTION_C(connection)
	

}