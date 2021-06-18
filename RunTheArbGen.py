# GeneratorArbitrary.py
#
# This example generates an arbitrary waveform.
#
# Find more information on http://www.tiepie.com/LibTiePie .

from __future__ import print_function
from array import array
from math import sin
import numpy as np
import sys
import libtiepie
import time
import datetime
import serial
# from printinfo import *

# Print library info:
# print_library_info()



################################################################
#
#               Freq duration list
#
################################################################
jobList = [[1, 4], [10, 2], [35, 1], [55, .6], [70, .4], [80, .2], [90, .2], [110, .2], [130, .2],[160,.2],[190,.2] ]
amplitude = 0.4  # in V
repeat_period = 3600  # seconds between jobs
t = (2021, 6, 11, 16, 14, 0, 0, 0, 0)  # start time
t = (t[0], t[1], t[2], t[3], 0, 0, 0, 0, 0)  # start time full hour

start_repeat = time.mktime(t)

while start_repeat < time.time():
    start_repeat += 3600

if start_repeat < time.time():
    start_repeat = time.time() + 10

print(datetime.datetime.utcfromtimestamp(start_repeat).strftime('%Y-%m-%d %H:%M:%S'))

ts = (2021, 6, 28, 17, 0, 0, 0, 0, 0)  # stop time
stop_repeat = time.mktime(ts)

port = "COM8"
ser = serial.Serial(port, baudrate=115200)  # open serial port

# Enable network search:
#libtiepie.network.auto_detect_enabled = True

# Search for devices:
libtiepie.device_list.update()

# Try to open a generator with arbitrary support:
gen = None
for item in libtiepie.device_list:
    if item.can_open(libtiepie.DEVICETYPE_GENERATOR):
        gen = item.open_generator()
        if gen.signal_types & libtiepie.ST_ARBITRARY:
            break
        else:
            gen = None

if gen:
    try:
        # Set signal type:
        gen.signal_type = libtiepie.ST_ARBITRARY
        gen.mode = libtiepie.GM_BURST_COUNT  # make burst
        gen.burst_count = 1  # make only one burst

        # Select frequency mode:
        gen.frequency_mode = libtiepie.FM_SAMPLEFREQUENCY

        # Set sample frequency:
        gen.frequency = 100e3  # 100 kHz

        # Set amplitude:
        gen.amplitude = amplitude  # 2 V

        # Set offset:
        gen.offset = 0  # 0 V

        # Enable output:


        # Create signal array, and load it into the generator:
        data = array('f')

        for job in jobList:
            n = int(job[1]*gen.frequency)
            for p in range(n):
                data.append(gen.amplitude * sin(2*np.pi*job[0]*float(p)/float(gen.frequency)))

        gen.set_data(data)

        data = None  # clear the memory

        # Print generator info:
        #print_device_info(gen)

        print("Start the sequence at: ", datetime.datetime.utcfromtimestamp(start_repeat).strftime('%Y-%m-%d %H:%M:%S'))
        while start_repeat > time.time():
            print('Wait to repeat: ', start_repeat - time.time(), " s ")
            st = (start_repeat - time.time()) * .4
            if st > 0:
                time.sleep(st)

        #  Wait for the next sequence
        #
        #  Repeat until stop_repeat timestamp
        print("Start the sequence at: ", datetime.datetime.utcfromtimestamp(start_repeat).strftime('%Y-%m-%d %H:%M:%S'))
        next_repeat = start_repeat
        while stop_repeat > time.time():

            while next_repeat > time.time():

                print('Wait to run: ', next_repeat - time.time(), " s ")
                st = (next_repeat - time.time()) * 0.4
                if st > 0:
                    time.sleep(st)

            # Start signal generation:
            ser.write(b'111')  # Arduino set 5V
            gen.output_on = True
            gen.start()
            print("Running...")

            #  wait for the burst to stop:
            while gen.status != 1:
                time.sleep(0.10)

            gen.output_on = False
            ser.write(b'000')  # Arduino set 0V

            next_repeat += repeat_period
            print("Start the sequence at: ",
                  datetime.datetime.utcfromtimestamp(next_repeat).strftime('%Y-%m-%d %H:%M:%S'))

        # Disable output:
        gen.output_on = False
        ser.close()

    except Exception as e:
        print('Exception: ' + e.message)
        sys.exit(1)

    # Close generator:
    del gen

else:
    print('No generator available with arbitrary support!')
    sys.exit(1)

sys.exit(0)
