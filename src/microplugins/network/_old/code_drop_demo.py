from time import sleep

from microplugins.network._old.code_drop import CodeDropClient, \
    CodeDropServer

if __name__ == "__main__":

    # Multicast address:
    multicast_group = ('224.0.0.1', 5007)

    # Callback:
    def on_message_received(sender_addr, message):
        print(f" *Server*: Message received: '{message}' from: {sender_addr}")

    # Start server:
    server = CodeDropServer(multicast_group, 6000, on_message_received)
    server.start_broadcasting()
    server.start_receiving()

    # Start client:
    client = CodeDropClient(multicast_group, 6000)
    client.start_discovering()
    sleep(2)
    while True:
        for server in client.servers:
            print(f" *Client*: Discovered server: {server}, sending message")
            client.send_message(server, "Hello, Server!")
            sleep(2)



