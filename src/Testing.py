
from datetime import datetime
import time

if (__name__ == "__main__"):
    current_time = datetime.now().microsecond
    print("Time1: {}".format(current_time))
    time.sleep(1)
    
    prev_time = current_time
    current_time = datetime.now().microsecond
    delta = current_time - prev_time
    print("Time2: {}".format(current_time))
    print("Delta: {}".format(delta))


    round(time.time() * 1000)

    current_time = round(time.time() * 1000)
    print("Time3: {}".format(current_time))
    time.sleep(0.5)
    
    prev_time = current_time
    current_time = round(time.time() * 1000)
    delta = current_time - prev_time
    print("Time4: {}".format(current_time))
    print("Delta: {}".format(delta))
    