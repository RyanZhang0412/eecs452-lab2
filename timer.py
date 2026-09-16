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
        # TODO: Update self.prev_start_time
        pass

    # Print time since start_time() was called
    def end_time(self):
        return
        # TODO: Replace return statment with functionality. Calculate time 
        # passed from self.prev_start_time
        # elapsed_time = Fill this in

        # Print elapsed time if printing is enabled
        if self.printflag == True:
            print("%s: %.06f s"%(self.desc, elapsed_time))
