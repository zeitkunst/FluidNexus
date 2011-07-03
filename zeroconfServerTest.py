from FluidNexus.Networking import ZeroconfServer

zs = ZeroconfServer(databaseDir = "/home/nknouf/.FluidNexus", databaseType = "pysqlite2", attachmentsDir = "/home/nknouf/.FluidNexus/attachments", logPath = "/home/nknouf/.FluidNexus/FluidNexus.log")
zs.run()
