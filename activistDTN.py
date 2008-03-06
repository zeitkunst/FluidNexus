import lightblue
import socket
import appuifw

# To make this work, I think I have to do the following
# One thread is a server thread; it advertises the service and checks to see if there are clients who want to connect
# One thread is a client thread, who tries to connect to other servers that are in the vicinity
# We probably want these things to be classes so that we can keep track of the open sockets

def testServices():
    s = socket.socket(socket.AF_BT, socket.SOCK_STREAM)
    s.setblocking(False)
    p = socket.bt_rfcomm_get_available_server_channel(s)
    s.bind(("", p))
    print "bind done"    
    s.listen(1)
    print "listening"
    socket.bt_advertise_service(u"nak", s, True, socket.RFCOMM)
    socket.set_security(s, socket.AUTH)
    print "i am listening"

    s.setblocking(False)
    sock, addr = s.accept()
    print "address is", addr

class ServerSocket:
    def __init__(self, serviceName = u'foo'):
        self.serviceName = serviceName
        self.serverSocket = socket.socket(socket.AF_BT, socket.SOCK_STREAM)
        self.serverPort = socket.bt_rfcomm_get_available_server_channel(self.serverSocket)
        self.serverSocket.bind(("", self.serverPort))

        # Only listen for one connection
        self.serverSocket.listen(1)

        # Advertise my service
        socket.bt_advertise_service(serviceName, 
                                    self.serverSocket,
                                    True,
                                    socket.RFCOMM)
        socket.set_security(self.serverSocket,
                            socket.AUTH)

        print "here!"

if __name__ == "__main__":
    server = ServerSocket(serviceName = u'activistDTNTesting')
