# timer.py

# A class to perform timing

import time

class Timer():

    # Parameters
    #   desc        String to be printed whenever end_time() is called and 
    #               printflag is true
    #   printflag   Boolean flag stating whether this timer should print the
    #               time.
    def __init__(self, desc="", printflag=True):
        self.prev_start_time = 0
        self.desc = desc
        self.printflag = printflag

    # Call this function to reset the timer
    def start_time(self):
        self.prev_start_time = time.time()

    # Print time since start_time() was called
    def end_time(self):
        elapsed_time = time.time() - self.prev_start_time

        if self.printflag == True:
            print("%s: %.06f s"%(self.desc, elapsed_time))

        return elapsed_time
