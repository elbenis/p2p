import socket
import threading
import tkinter

status = ""

root = tkinter.Tk()
root.geometry("900x900")
root.title("P2P")
root.configure(bg="#000000")

# Client 1 (Server)
def serverF():
    global server, connectionSocket, status

    status = "server"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 8080))

    server.listen(1)

    while True:
        client, addr = server.accept()
        connectionSocket = client
        receivedMsg = client.recv(2048)

        if receivedMsg:
            print("Received message: " + receivedMsg.decode())

            newMsg = tkinter.Label(chat, text=("Other: " + receivedMsg.decode()))
            newMsg.pack(side="top", anchor="w")
        else:
            print("[!] Message it's null")

# Client 2 (client)
def clientF():
    global client, status

    status = "client"
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((f'{ipEntry.get()}', 8080))

    while True:
        receivedMsg = client.recv(2048)

        if receivedMsg:
            print("Received message: " + receivedMsg.decode())

            newMsg = tkinter.Label(chat, text=("Other: " + receivedMsg.decode()))
            newMsg.pack(side="top", anchor="w")
        else:
            print("[!] Message it's null")

# Send message function
def sendMessage(msg):
    if status == "server":
        try:
            connectionSocket.send(msg.encode())

            newMsg = tkinter.Label(chat, text=("You: " + msg))
            newMsg.pack(side="top", anchor="w")
        except:
            print("[-] Error sending message")
            return

    elif status == "client":
        try:
            client.send(msg.encode())

            newMsg = tkinter.Label(chat, text=("You: " + msg))
            newMsg.pack(side="top", anchor="w")
        except:
            print("[-] Error sending message")
            return

    else:
        print("[-] Failed to send message, please be a server or client and try again")

# Send entry and button
messageInput = tkinter.Entry(width=40)
messageInput.place(x=300, y=800)
messageSend = tkinter.Button(width=5, height=2, text="Send", fg="#FFFFFF", bg="#111111", command=lambda:sendMessage(messageInput.get()))
messageSend.place(x=230, y=800)

# IP Entry
ipEntry = tkinter.Entry(width=30)
ipEntry.place(x=330, y=10)

# IP Button (Be client 1)
ipButton1 = tkinter.Button(width=10, height=2, text="Set Server \n(be client 1)", fg="#000000", bg="#00F000", command=lambda: threading.Thread(target=serverF).start())
ipButton1.place(x=10, y=10)

# IP Button (Be client 2)
ipButton2 = tkinter.Button(width=10, height=2, text="Connect server \n(be client 2)", fg="#000000", bg="#F00000", command=lambda: threading.Thread(target=clientF).start())
ipButton2.place(x=10, y=70)

# Chat frame
chat = tkinter.Frame(width=550, height=710, bg="#111111")
chat.place(y=50, x=170)
chat.pack_propagate(False)

root.mainloop()