from FluidNexus.Networking import ZeroconfClient

zc = ZeroconfClient(databaseDir = "/home/nknouf/.FluidNexus", databaseType = "pysqlite2", attachmentsDir = "/home/nknouf/.FluidNexus/attachments", logPath = "/home/nknouf/.FluidNexus/FluidNexus.log", loopType = "glib")
zc.run()
