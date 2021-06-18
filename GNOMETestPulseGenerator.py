# Generator.py
#
# This example generates a 100 kHz triangle waveform, 4 Vpp.
#
# Find more information on http://www.tiepie.com/LibTiePie .

from __future__ import print_function
import sys
import libtiepie
import time
import serial
import datetime
#from printinfo import *

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

port = "COM6"
ser = serial.Serial(port, baudrate=115200)  # open serial port

print(start_repeat - time.time())
print()
print("Start the sequence at: ", datetime.datetime.utcfromtimestamp(start_repeat).strftime('%Y-%m-%d %H:%M:%S'))
while start_repeat > time.time():
    sys.stdout.flush()
    print('Wait to start: ', start_repeat - time.time(), " s ")
    time.sleep((start_repeat - time.time())*.4)

# Print library info:
#print_library_info()

# Enable network search:
#libtiepie.network.auto_detect_enabled = True

# Search for devices:
libtiepie.device_list.update()

# Try to open a generator:
gen = None
for item in libtiepie.device_list:
    if item.can_open(libtiepie.DEVICETYPE_GENERATOR):
        gen = item.open_generator()
        if gen:
            break

if gen:
    try:
        # Set signal type:
        gen.signal_type = libtiepie.ST_SINE

        # Set frequency:
        gen.frequency = jobList[0][0]  # 100 kHz

        # Set amplitude:
        gen.amplitude = amplitude  # 2 V

        # Set offset:
        gen.offset = 0  # 0 V

        # Enable output:
        gen.output_on = True

        # Print generator info:
        #print_device_info(gen)

        # Start signal generation:
        #gen.start()

        next_repeat = start_repeat - repeat_period
        while stop_repeat > time.time():

            next_repeat += repeat_period
            print("Start at: ", datetime.datetime.utcfromtimestamp(next_repeat).strftime('%Y-%m-%d %H:%M:%S'))
            while next_repeat > time.time():
                time.sleep((next_repeat - time.time())*.4)
                print("Wait for new job: ", next_repeat - time.time(), " s")

            next_time = time.time()
            for job in jobList:
                next_time += job[1]
                ser.write(b'111')  # Arduino set 5V
                gen.frequency = job[0]
                if not gen.is_running:
                    gen.output_on = True
                    gen.start()

                print("f = ", gen.frequency, " Hz, T = ", job[1], ' s')

                while time.time() < next_time:
                    time.sleep(0.001)
            # Stop generator:
            gen.stop()
            gen.output_on = False
            ser.write(b'000')  # Arduino set 0V

        # Wait for keystroke:
        #print('Press Enter to stop signal generation...')
        #input()

        # Stop generator:
        gen.stop()

        # Disable output:
        gen.output_on = False

    except Exception as e:
        print('Exception: ' + e.message)
        sys.exit(1)

    # Close generator:
    del gen

else:
    print('No generator available!')
    sys.exit(1)

sys.exit(0)