from FluidNexus.Networking import ZeroconfClient

zc = ZeroconfClient(databaseDir = "/home/nknouf/.FluidNexus", databaseType = "pysqlite2", attachmentsDir = "/home/nknouf/.FluidNexus/attachments", logPath = "/home/nknouf/.FluidNexus/FluidNexus.log", host = "192.168.1.15")
zc.run()
