import re,os,sys,os.path,errno,glob
import time
import functools
import logging
from termcolor import colored

def world():
    '''
    Test function
    '''
    print("Hello, World!")

class log_collector(object):

    def __init__(self, log_level, mode, path):
        self.log_level  = log_level
        self.mode       = mode
        self.path       = path
        
        self.run_level_test(self.log_level)
        self.run_mode_test(self.mode)
        self.run_path_test(self.path)

        self.start_logging()

    def __repr__(self):
        return("{}: {},{},{}".format("log_collector", self.log_level, self.mode, self.path))


    '''
    Unit tests inside the class
    Each parameter is validated before being written to the log message.
    Hard to use the custom exemption routine, so went for pass and exit(0)
    '''
    def run_level_test(self, log_level):
        if re.search('debug|info|warning|error|critical', log_level, re.IGNORECASE):
            pass
        else:
            print("Error processing log level {}".format(log_level))
            exit(0)


    def run_mode_test(self, mode):
        if re.search('w|a', mode, re.IGNORECASE):
            pass
        else:
            print("Error with log mode {}".format(mode))
            exit(0)


    def run_path_test(self, path):
        if os.path.exists(path):
            pass
        else:
            print("Error - go create: {}".format(path))
            exit(0)


    def run_msg_test(msgA, msgB):
        if len(msgA or msgB) < 50:
            pass
        
        else:
            print("Error with msg lengths: {} {}".format(msgA, msgB))
            exit(0)



    '''
    This function is initialized at startup, after we pass all the unit tests:
    self.start_logging()
    '''
    def start_logging(self):
        logging.basicConfig(level=self.log_level,
                            format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
                            filename=self.path,
                            filemode=self.mode)

        console     = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter   = logging.Formatter('%(asctime)s %(name)-8s %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)



    '''
    Write the message to a log in a custom format.
    Takes 3 positional's which are all validated.
    Then matching the input, get written out.
    '''
    def write_msg(log_level, msgA, msgB):

        log_collector.run_level_test(None, log_level)
        log_collector.run_msg_test(msgA, msgB)


        if log_level == "debug":
            logging.debug('{:50} - {}'.format(msgA, msgB))

        elif log_level == "info":
            logging.info('{:50} - {}'.format(msgA, msgB))

        elif log_level == "warning":
            logging.warning('{:50} - {}'.format(msgA, msgB))

        elif log_level == "error":
            logging.error('{:50} - {}'.format(msgA, msgB))

        elif log_level == "critical":
            logging.critical('{:50} - {}'.format(msgA, msgB))

        else:
            exit(0)



"""
This decorator prints the execution time for the decorated function.
Uses the function tools, as a wrapper to the original function.
Uses the custom message log funtion in the class log_collector.

Add in a function for coloring the time when limits are set
"""
def timed(function):

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            start   = time.time()
            result  = function(*args, **kwargs)
            end     = time.time()
            msgA    = "Func {}".format(function.__name__)

            delta   = round((end - start), 4)
            delta   = colored(delta, 'green')

            msgB    = "ran in {}".format(delta)
            log_collector.write_msg("info", msgA, msgB)
        
            return result
    
        except Exception as error: 
            log_collector.write_msg("info","There was an exception in:", function.__name__)
            exit(0)

    return wrapper


"""
A decorator that wraps the passed in function, and creates a custom log message.
"""
def exception(function):

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
      
        try:
            
            return function(*args, **kwargs)

        except Exception as error: 
            msgA = "EXEMPTION IN: {}".format(function.__name__)
            msgB = "Message {}".format(repr(error))
            log_collector.write_msg("error", msgA, msgB)
            exit(0)
    
    return wrapper
