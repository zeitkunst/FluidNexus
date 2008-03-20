# Copyright (C) 2008, Nick Knouf, Bruno Vianna, and Luis Ayuso
# 
# This file is part of Fluid Nexus
#
# Fluid Nexus is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import codecs

class Logger: 
    def __init__(self, log_name, prefix = 'Foo: '): 
        self.logfile = log_name 
        self.prefix = prefix

    def write(self, obj): 
        log_file = codecs.open(self.logfile, 'a', 'utf_8') 
        log_file.write(self.prefix + unicode(obj) + '\n') 
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

