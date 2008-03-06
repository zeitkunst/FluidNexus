class Logger: 
    def __init__(self, log_name, prefix = 'Foo: '): 
        self.logfile = log_name 
        self.prefix = prefix

    def write(self, obj): 
        log_file = open(self.logfile, 'a') 
        log_file.write(self.prefix + obj + '\n') 
        log_file.close() 

    def writelines(self, obj): 
        self.write(''.join(list)) 
    
    def flush(self): 
        pass 

    def print_exception_trace(self): 
        import sys, traceback 
        log_file = open(self.logfile, 'a') 
        
        try: 
            type, value, tb = sys.exc_info() 
            sys.last_type = type 
            sys.last_value = value 
            sys.last_traceback = tb 
            tblist = traceback.extract_tb(tb) 
            del tblist[:1] 
            list = traceback.format_list(tblist) 
            
            if list: 
                list.insert(0, "Traceback (most recent call last):\n") 
                list[len(list):] = traceback.format_exception_only(type, value) 
        finally: 
            tblist = tb = None 
            map(log_file.write, list) 
            log_file.close() 

