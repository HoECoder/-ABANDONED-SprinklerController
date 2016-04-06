import time
import logging
import logging.handlers
import pprint

#Need a more complex logging
logging.basicConfig(level=logging.DEBUG)

fh = logging.handlers.RotatingFileHandler("D:\\toys\\controller\\controller.log",
                                                            maxBytes=1024*1024,
                                                            backupCount=15)
logging.getLogger('').addHandler(fh)

from controller import Controller, make_now

def monkey_program(program, time_delta=10):
    n = make_now()
    even_odd = {1 : "odd",
                0 : "even"}[n["day"] % 2]
    program["interval"] = {"type" : even_odd}
    program["time_of_day"] = n["seconds_from_midnight"] + time_delta

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
    monkey_program(controller.programs[1])
    pprint.pprint(controller.programs[1])
    monkey_program(controller.programs[2], 55)
    pprint.pprint(controller.programs[2])
    monkey_program(controller.programs[3], 105)
    pprint.pprint(controller.programs[3])
    controller.prepare_programs()
    print len(controller.programs.keys())
    i = 0
    try:
        while True:
            print "Tick: %d" % i
            controller.tick()
            i = i+1
            time.sleep(1)
    except KeyboardInterrupt:
        print "\nCTRL-C caught, Shutdown"
