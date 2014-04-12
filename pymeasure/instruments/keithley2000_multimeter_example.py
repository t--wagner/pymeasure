import time

# Import the Keithley2000 class
from keithley2000_multimeter import Keithley2000Multimeter

# Create a Keithley 2000 instance
gpib_address = 'GPIB0::6'
k2000 = Keithley2000Multimeter('k2000', gpib_address)

def k2000_read():
    """
    Read a single datapoint
    """

    k2000.reset()
    
    return k2000[0].read()    


def k2000_read_init():
    """
    Initiate a measurment and read the data
    """
    
    k2000.reset()
    
    # Initiate the measurment
    k2000[0].initiate()
    
    # Read back the aquired data without initiating a new measurment
    return k2000[0].read(initiate=False)
    

def k2000_read_multi(nr_of_samples):
    """
    Read multiple datapoints by using a for loop.    
    """
    
    data = []
    k2000.reset()
    
    t_start = time.time()
    
    for point in range(0, nr_of_samples):
        data += k2000[0].read()
    
    print "Time: " + str(time.time() - t_start)
    
    return data


def k2000_read_multi_samples(nr_of_samples):
    """
    Read multiple datapoints by using the sample option of the Keithles2000.    
    This method is roughly 3 times faster than the programmed loop example.
    """
    
    data = []
    k2000.reset()
    
    t_start = time.time()

    k2000.trigger.samples = nr_of_samples
    data = k2000[0].read()
    
    print "Time: " + str(time.time() - t_start)
    
    return data
    
    
def k2000_read_buffered(nr_of_points):
    """
    Store all readings in the buffer and tranfer data at once.
    """
    
    data = []
    k2000.reset()
    
    # Set up the buffer
    k2000.buffer.points = nr_of_points
    k2000.buffer.control = True
    
    # Prepare initiate and read for buffering
    k2000[0].buffering = True
    
    # Initiate the measurments
    for point in range(0, nr_of_points):
        k2000[0].initiate()
        #print point
        # Wait a while to make sure the keithles is not busy while recieving the next init
        time.sleep(1)

    # Read the data
    return k2000[0].read(False)        
        
        
def k2000_read_triggered(nr_of_triggers):
    """
    Set up the Keithley 2000 for triggered operation.
    """
    
    data = []
    k2000.reset()
    
    # Set up the buffer
    k2000.buffer.points = nr_of_triggers
    k2000.buffer.control = True
    
    # Set up the trigger, the source is usally external
    k2000.trigger.source = 'BUS'
    k2000.trigger.count = nr_of_triggers

    # Initiate the measurment and wait for trigger signals 
    k2000[0].buffering = True   
    k2000[0].initiate()
      
    # Initiate the measurments
    for point in range(0, nr_of_triggers):
        k2000._pyvisa_instr.write("*TRG")
        
        # Wait a while to make sure the Keiethley 2000 is not busy while recieving the next trigger.
        # See in the Keithley 2000 manual section A-11 for optimizing measurment speed.
        time.sleep(1)    
    
    return k2000[0].read(False)      
        
        
        
def k2000_ext_triggered(nr_of_triggers):
    """
    Set up the Keithley 2000 for triggered operation.
    """
    
    data = []
    k2000.reset()
    
    # Set up the buffer
    k2000.buffer.points = nr_of_triggers
    k2000.buffer.control = True
    
    # Set up the trigger, the source is usally external
    k2000.trigger.source = 'ext'
    k2000.trigger.count = nr_of_triggers

    # Initiate the measurment and wait for trigger signals 
    k2000[0].buffering = True   
    k2000[0].initiate()
      
    # Initiate the measurments
    #for point in range(0, nr_of_triggers):
    #    k2000._pyvisa_instr.write("*TRG")
        
        # Wait a while to make sure the Keiethley 2000 is not busy while recieving the next trigger.
        # See in the Keithley 2000 manual section A-11 for optimizing measurment speed.
    #    time.sleep(1)    
    
    return k2000[0].read(False)      
                
        
        
        
        
        
        
    