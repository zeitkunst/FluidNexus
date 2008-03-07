# Standard library imports
import sys
import os
import socket
import select
import md5
import time

# other imports
import lightblue

class FluidNexusClient(object):
    def __init__(self):
        # Nothing here right now...
        pass
    
    def run(self):
        allDevices = lightblue.finddevices(length = 5)
        phones = []

        for device in allDevices:
            foo, isPhone, bar = lightblue.splitclass(device[2])
            if isPhone == 2:
                phones.append(device)

        for phone in phones:
            print "Looking at phone", phone
            services = lightblue.findservices(phone[0])
            print services
            for service in services:
                if service[2] is not None and 'FluidNexus' in service[2]:
                    port = service[1]
                    break
                else:
                    port = None
            print port
            print "at end of service search"

            if port is not None:
                print "sending data!"
                clientSocket = lightblue.socket()
                clientSocket.connect((phone[0], port))
                clientSocket.send('01')
                time.sleep(1)
                clientSocket.send('010')
                time.sleep(1)
                clientSocket.send('000010')
                time.sleep(1)
                clientSocket.send(str(time.time()))
                time.sleep(1)
                clientSocket.send(md5.md5('foo').hexdigest())
                time.sleep(1)
                clientSocket.send('aaaaaaaaaa')
                time.sleep(1)
                clientSocket.send('aaaaaaaaaa')
                time.sleep(1)
                clientSocket.close()

if __name__ == "__main__":
    client = FluidNexusClient()
    client.run()
