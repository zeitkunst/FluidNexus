#!/usr/bin/env python
import avahi
import dbus
import hashlib
import socket
import time

__all__ = ["ZeroconfService"]

class ZeroconfService:
    """A simple class to publish a network service with zeroconf using
    avahi.
        
    """

    def __init__(self, name, port, stype="_fluidnexus._tcp",
                 domain="", host="", text=""):
        self.name = name
        self.stype = stype
        self.domain = domain
        self.host = host
        self.port = port
        self.text = text
    
    def publish(self):
        bus = dbus.SystemBus()
        server = dbus.Interface(
                         bus.get_object(
                                 avahi.DBUS_NAME,
                                 avahi.DBUS_PATH_SERVER),
                        avahi.DBUS_INTERFACE_SERVER)

        g = dbus.Interface(
                    bus.get_object(avahi.DBUS_NAME,
                                   server.EntryGroupNew()),
                    avahi.DBUS_INTERFACE_ENTRY_GROUP)

        g.AddService(avahi.IF_UNSPEC, avahi.PROTO_UNSPEC,dbus.UInt32(0),
                     self.name, self.stype, self.domain, self.host,
                     dbus.UInt16(self.port), self.text)

        g.Commit()
        self.group = g
    
    def unpublish(self):
        self.group.Reset()

def testSocket():
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.bind((socket.gethostname(), 65123))
    ss.listen(1)

    while 1:
        (cs, ca) = ss.accept()
        data = cs.recv(1024)
        print data

def test():
    port = 65123
    service = ZeroconfService(name=hashlib.md5(str(time.time())).hexdigest(), port=port)
    service.publish()
    testSocket()
    raw_input("Press any key to unpublish the service ")
    service.unpublish()


if __name__ == "__main__":
    test()