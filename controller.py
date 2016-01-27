import time

interval_types = ["even","odd","day_of_week"]

program_1 = {"pid": 1,
             "time_of_day" : 0,
             "interval" : {"type":"even"},
             "in_program" : False,
             "station_duration" : [{"stid":1,
                                    "duration":5,
                                    "in_station":False},
                                   {"stid":2,
                                    "duration":5,
                                    "in_station":False},
                                   {"stid":3,
                                    "duration":5,
                                    "in_station":False},
                                   {"stid":4,
                                    "duration":5,
                                    "in_station":False},
                                   {"stid":5,
                                    "duration":5,
                                    "in_station":False},
                                   {"stid":6,
                                    "duration":5,
                                    "in_station":False},
                                   {"stid":7,
                                    "duration":5,
                                    "in_station":False},
                                   {"stid":8,
                                    "duration":5,
                                    "in_station":False}],
             "total_run_time":0}

def make_now():
    # We build now (year,month,day,day_of_week,hour,minute,second,seconds_from_midnight)
    current_time = time.localtime()
    now = dict()
    now["year"]=current_time.tm_year
    now["month"]=current_time.tm_mon
    now["day"]=current_time.tm_mday
    now["day_of_week"]=current_time.tm_wday
    now["hour"]=current_time.tm_hour
    now["minute"]=current_time.tm_min
    now["second"]=current_time.tm_sec
    
    hrs = now["hour"] * 3600
    mins = now["minute"] * 60
    secs = now["second"]
    
    seconds = hrs + mins + secs
    
    now["seconds_from_midnight"] = seconds
    
    return now

def within_program_time(program,clock):
    start_time = program["time_of_day"]
    duration = program["total_run_time"]
    end_time = start_time+duration
    if start_time <= clock and clock < end_time:
        return True
    else:
        return False
        
def is_program_run_day(program,now):
        # program_id is the program we would like to check
        # now has fields "year", "month", "day", "day_of_week", "hour", "minute", "second", "seconds_from_midnight"
        if program is None:
            return False #should throw an error here
        interval = program["interval"]
        interval_type = interval["type"]
        if interval_type in ["even","odd"]: # Run on even or odd days
            day = now["day"]
            even_odd = day % 2 == 0
            if interval_type == "even":
                return even_odd
            else:
                return not(even_odd)
        elif interval_type == "day_of_week":
            # Day of week is a number in the set (0-6) (i.e. Mon-Sun)
            # We see if this is in the intervals list of days
            wd = now["day_of_week"]
            run_days = interval.get("run_days",None)
            if run_days is None:
                return False # We should throw an error here too
            if wd in run_days:
                return True
            else:
                return False
        else:
            return False # should throw another error here
        return False
        
class Controller(object):
    def __init__(self,programs):
        self.programs = dict()
        for program in programs:
            self.programs[program["pid"]] = program
    def prepare_programs(self):
        for program in self.programs.values(): 
            total_run_time = 0
            for sd in program["station_duration"]:
                tod = program["time_of_day"]
                station_run = sd["duration"]
                sd["start_time"] = total_run_time + tod
                total_run_time = total_run_time + station_run
                sd["end_time"] = total_run_time + tod
                #sd["running"] = False
            program["total_run_time"] = total_run_time

    def get_current_programs(self,now):
        running_programs = list()
        clock = now["seconds_from_midnight"]
        for program in self.programs.values():
            if program["in_program"]: # Grab a program that may already be running
                running_programs.append(program)
                # Check if we should expire this program
                if not(within_program_time(program,clock)):
                    program["expire"]=True # We should expire this program
                if not(is_program_run_day(program,now)):
                    program["expire"]=True # On the chance we got suspended and the day changed on us
            else: # Grab programs that should be running
                if is_program_run_day(program,now): # We look if it is a run day
                    if within_program_time(program,clock): # We should run this program
                        running_programs.append(program)
        return running_programs

    def stop_program(self,program_id):
        program = self.programs.get(program_id,None)
        if program is None:
            return
        program["in_program"]=False
        program.pop("expire",None)
        for station in program["station_duration"]:
            station["in_station"]=False
        print "Stopping program"
        self.dispatch_full_stop()
    def start_program(self,program_id,now):
        program = self.programs.get(program_id,None)
        if program is None:
            return
        program["in_program"]=True
        print "Starting program"
        self.advance_program(program_id,now)
    def advance_program(self,program_id,now):
        program = self.programs.get(program_id,None)
        if program is None:
            return
        clock = now["seconds_from_midnight"]
        start_time = program["time_of_day"]
        elapsed_time = clock - start_time
        run_length = 0
        stop_stations = list()
        start_stations = list()
        print "Checking advancement. Clock: %d, start: %d, elapsed: %d" % (clock,start_time,elapsed_time)
        # We go through all the stations in the program
        # We determine who needs to start and stop
        for station in program["station_duration"]:
            station_start = station["start_time"]
            station_stop = station["end_time"]
            running = station["in_station"]
            stid = station["stid"]
            print "\tStation stid:%d, start %d, stop %d, running %s" % (stid,station_start,station_stop,str(running))
            if (station_start <= clock and clock < station_stop):
                if not(running):
                    # Fire up the station
                    print "\t\tFire up the station"
                    start_stations.append(stid)
                    station["in_station"] = True
                else:
                    print "\t\tStation is already running"
                    #Otherwise we sit patiently. Latching relays
            else: #Station is old
                if running: # We have to stop this guy first
                    stop_stations.append(stid)
                    station["in_station"] = False
                    print "\t\tStopping station"
                else:
                    print "\t\tStation was not running"
        # Now we stop all stations first
        self.dispatch_stop(stop_stations)
        # Now we start all stations
        self.dispatch_start(start_stations)
    def dispatch_full_stop(self):
        print "Dispatch FULL STOP"
        pass # We would call dispatch_stop
    def dispatch_stop(self,stations):
        print "Stopping stations: " , stations
        pass
    def dispatch_start(self,stations):
        print "Starting stations: " , stations
        pass
    def tick(self):
        # This is our main function. Should be called from some sort of loop
        # 1. We build now (year,month,day,day_of_week,hour,minute,second,seconds_from_midnight)
        # 2. We find any running programs
        # 3. Loop over the programs
        # 3.a If the program is expired, stop it
        # 3.b If a program is live, possibly advance its stations
        # 3.c If a new program is up, start it
        
        # 1. Build NOW
        now = make_now()
        print now
        print "Getting programs"
        # 2. Get the list of programs
        running_programs = self.get_current_programs(now)
        # 3. Loop over the programs
        if len(running_programs) > 0:
            print "Looping over programs"
        else:
            print "No programs this tick"
        for program in running_programs:
            # 3.a Expire the expired programs
            expired = program.get("expire",False)
            in_program = program.get("in_program",None)
            pid = program["pid"]
            if expired:
                print "Expiring pid:", pid
                self.stop_program(pid)
            elif in_program: # 3.b Possibly advance the program
                print "Checking for advancement of pid:",pid
                self.advance_program(pid,now)
            else: # 3.c Start up the program
                print "Starting up program pid:", pid
                self.start_program(pid,now)
    
if __name__ == "__main__":
    import pprint
    now = make_now()
    odd_even = now["day"] % 2 == 0
    if odd_even:
        odd_even = "even"
    else:
        odd_even = "odd"
    program_1["interval"]["type"]=odd_even
    tod = now["seconds_from_midnight"] + 10
    program_1["time_of_day"] = tod
    print "Toy Simulation"
    print "Toy Program"
    pprint.pprint(program_1)
    controller = Controller([program_1])
    controller.prepare_programs()
    pprint.pprint(program_1)
    i = 0
    while i < 90:
        print "Tick"
        controller.tick()
        i = i+1
        time.sleep(1)