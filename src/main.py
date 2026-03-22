import socket
import threading
import tkinter
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

status = ""
root = tkinter.Tk()
root.geometry("900x900")
root.title("P2P")
root.configure(bg="#000000")

# --- RSA ---
def generate_private_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)

def sign_message(private_key, message):
    if isinstance(message, str):
        message = message.encode('utf-8')
    return private_key.sign(message, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())

def verificate(public_key, message, signature):
    if isinstance(message, str):
        message = message.encode('utf-8')
    public_key.verify(signature, message, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())

def encrypt_message(public_key, message):
    if isinstance(message, str):
        message = message.encode('utf-8')
    return public_key.encrypt(message, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))

def decrypt_message(private_key, ciphertext):
    return private_key.decrypt(ciphertext, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
# ------

# Server
def ServerFN():
    global server, connectionSocket, status, private_key, client_public_key
    status = "server"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 8080))
    private_key = generate_private_key()
    server.listen(1)
    client, addr = server.accept()
    connectionSocket = client
    client.send(private_key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
    client_public_pem = client.recv(4096)
    client_public_key = serialization.load_pem_public_key(client_public_pem)

    while True:
        receivedMsg = client.recv(8192)
        if receivedMsg:
            sig, cipher = receivedMsg[:256], receivedMsg[256:]
            plaintext = decrypt_message(private_key, cipher).decode()
            try:
                verificate(client_public_key, plaintext, sig)
            except:
                pass
            newMsg = tkinter.Label(chat, text=("Other: " + plaintext))
            newMsg.pack(side="top", anchor="w")

# Client
def ClientFN():
    global client, status, private_key, server_public_key
    status = "client"
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((f'{ipEntry.get()}', 8080))
    private_key = generate_private_key()
    server_public_pem = client.recv(4096)
    server_public_key = serialization.load_pem_public_key(server_public_pem)
    client.send(private_key.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))

    while True:
        receivedMsg = client.recv(8192)
        if receivedMsg:
            sig, cipher = receivedMsg[:256], receivedMsg[256:]
            plaintext = decrypt_message(private_key, cipher).decode()
            try:
                verificate(server_public_key, plaintext, sig)
            except:
                pass
            newMsg = tkinter.Label(chat, text=("Other: " + plaintext))
            newMsg.pack(side="top", anchor="w")

def sendMessage(msg):
    if status == "server":
        signature = sign_message(private_key, msg)
        ciphertext = encrypt_message(client_public_key, msg)
        connectionSocket.send(signature + ciphertext)
    elif status == "client":
        signature = sign_message(private_key, msg)
        ciphertext = encrypt_message(server_public_key, msg)
        client.send(signature + ciphertext)
    newMsg = tkinter.Label(chat, text=("You: " + msg))
    newMsg.pack(side="top", anchor="w")

messageInput = tkinter.Entry(width=40)
messageInput.place(x=300, y=800)
messageSend = tkinter.Button(width=5, height=2, text="Send", fg="#FFFFFF", bg="#111111", command=lambda:sendMessage(messageInput.get()))
messageSend.place(x=230, y=800)

ipEntry = tkinter.Entry(width=30)
ipEntry.place(x=330, y=10)

ipButton1 = tkinter.Button(width=10, height=2, text="Set Server", fg="#000000", bg="#00F000", command=lambda: threading.Thread(target=ServerFN).start())
ipButton1.place(x=10, y=10)

ipButton2 = tkinter.Button(width=10, height=2, text="Connect server", fg="#000000", bg="#F00000", command=lambda: threading.Thread(target=ClientFN).start())
ipButton2.place(x=10, y=70)

chat = tkinter.Frame(width=550, height=710, bg="#111111")
chat.place(y=50, x=170)
chat.pack_propagate(False)

root.mainloop()