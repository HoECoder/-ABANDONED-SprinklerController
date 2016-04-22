#!/usr/bin/env python
import time
import os
import os.path
import logging
import logging.handlers
import pprint

#Need a more complex logging
logging.basicConfig(level=logging.INFO)

if os.name == "nt":
    log_filename = "D:\\toys\\controller\\controller.log"
else:
    log_filename = os.path.expanduser("~/.controller/controller.log")

fh = logging.handlers.RotatingFileHandler(log_filename,
                                          maxBytes=1024*128,
                                          backupCount=15)
logging.getLogger('').addHandler(fh)

from controller import Controller, make_now,monkey_program

if __name__ == "__main__":
    now = make_now()
    odd_even = now["day"] % 2 == 0
    if odd_even:
        odd_even = "even"
    else:
        odd_even = "odd"
    print "Toy Simulation"
    print "Toy Program"
    controller = Controller()
    monkey_program(controller.programs[1], 20)
    pprint.pprint(controller.programs[1])
    monkey_program(controller.programs[2], 160)
    pprint.pprint(controller.programs[2])
    monkey_program(controller.programs[3], 200)
    pprint.pprint(controller.programs[3])
    controller.prepare_programs()
    print len(controller.programs.keys())
    i = 0
    controller.add_single_station_program(6, 7)
    pprint.pprint(controller.one_shot_program)
    try:
        while True:
            print "Tick: %d" % i
            controller.tick()
            if i == 105 :
                controller.add_one_shot_program(1)
            i = i+1
            time.sleep(1)
    except KeyboardInterrupt:
        print "\nCTRL-C caught, Shutdown"
