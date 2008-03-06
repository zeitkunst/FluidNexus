import appuifw
import e32
import thread

lock = e32.Ao_lock()
lockTHR = thread.allocate_lock()

###### Sostituisci questa funzione con quello che vuoi fare eseguire
i = 0
def funzDaemon():
    global i
    
    while(1):
        lockTHR.acquire()
        e32.ao_sleep(1)
        print i
        i+=1
        lockTHR.release()
                                                        ####################################################################

appuifw.app.title = u'DaemonS60'
def appExit():
    lock.signal()
appuifw.app.exit_key_handler = appExit

print 'DaemonS60 - Start'

thread.start_new_thread(funzDaemon, ())

lock.wait()

print 'DaemonS60 - Stop'
