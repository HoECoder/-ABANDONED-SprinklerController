import json
import glob
import os
import os.path
import copy
from collections import OrderedDict
import ConfigParser
import cerberus

if os.name == "nt":
    settings_base_dir = "D:\\toys\\controller"
else:
    settings_base_dir = os.path.expanduser("~/.controller")
master_name = "master.cfg"

MAIN_SECTION = 'Main'
STATION_SETTINGS_KEY = 'Station Settings'
OSPI_VERSION_KEY = 'ospi version'
STATION_SECTION_KEY = 'Station %d'
TZ_KEY = 'time zone'
SYS_VERSION_KEY = 'system version'
DATE_FORMAT_KEY = 'date format'
TIME_FORMAT_KEY = 'time format'
LOCATION_KEY = 'location'
RAIN_SENSOR_KEY = 'rain sensor'
INVERT_RAIN_SENSOR_KEY = 'invert rain sensor'
STATIONS_AVAIL_KEY = 'stations available'
STATION_NAME_KEY = 'name'
WIRED_KEY = 'wired'
IGNORE_RAIN_KEY = 'ignore rain sensor'
NEED_MASTER_KEY = 'need master'
STATION_LIST_KEY = 'station list'

boolean_conf_keys = [RAIN_SENSOR_KEY,
                     INVERT_RAIN_SENSOR_KEY,
                     WIRED_KEY,
                     IGNORE_RAIN_KEY,
                     NEED_MASTER_KEY]
int_conf_keys = [STATIONS_AVAIL_KEY]
                       

def make_test_settings():
    __station_template = OrderedDict()
    __station_template[STATION_NAME_KEY] = ''
    __station_template[WIRED_KEY] = True
    __station_template[IGNORE_RAIN_KEY] = False
    __station_template[NEED_MASTER_KEY] = False

    Station_Dict = OrderedDict()
    __temp = copy.deepcopy(__station_template)
    __temp[STATION_NAME_KEY] = 'Station 1'
    Station_Dict[1] = __temp
    __temp = copy.deepcopy(__station_template)
    __temp[STATION_NAME_KEY] = 'Station 2'
    Station_Dict[2] = __temp
    __temp = copy.deepcopy(__station_template)
    __temp[STATION_NAME_KEY] = 'Station 3'
    Station_Dict[3] = __temp
    __temp = copy.deepcopy(__station_template)
    __temp[STATION_NAME_KEY] = 'Station 4'
    Station_Dict[4] = __temp
    __temp = copy.deepcopy(__station_template)
    __temp[STATION_NAME_KEY] = 'Station 5'
    Station_Dict[5] = __temp
    __temp = copy.deepcopy(__station_template)
    __temp[STATION_NAME_KEY] = 'Station 6'
    Station_Dict[6] = __temp
    __temp = copy.deepcopy(__station_template)
    __temp[STATION_NAME_KEY] = 'Station 7'
    __temp[WIRED_KEY] = False
    Station_Dict[7] = __temp
    __temp = copy.deepcopy(__station_template)
    __temp[STATION_NAME_KEY] = 'Station 8'
    __temp[WIRED_KEY] = False
    Station_Dict[8] = __temp

    Master = OrderedDict()
    Master[SYS_VERSION_KEY] = 'v1.0'
    Master[OSPI_VERSION_KEY] = 'v1.4'
    Master[TIME_FORMAT_KEY] = '%H:%M:%S'
    Master[DATE_FORMAT_KEY] = '%Y-%m-%d'
    Master[TZ_KEY] = 'SYSTEM'
    Master[LOCATION_KEY] = 'Garage'
    Master[INVERT_RAIN_SENSOR_KEY] = False
    Master[RAIN_SENSOR_KEY] = False
    Master[STATIONS_AVAIL_KEY] = 8
    Master[STATION_LIST_KEY] = Station_Dict
    return Master

default_master = make_test_settings()
default_station_dict = default_master[STATION_LIST_KEY]

interval_types = ["even", "odd", "day_of_week"]
interval_types_s = str(interval_types)
def validate_interval(field, value, error):
    typ = value["type"]
    if typ == "day_of_week":
        days = value.get("run_days", None)
        if days is None:
            error(field, "Day of Week Interval must contain a list of days")
        ma = max(days)
        mi = min(days)
        if mi < 0 or ma > 6:
            error(field, "Day of Week Interval must have a list of days Sun - Sat")
    elif not(typ in ["even", "odd"]):
        error(field, "Interval type must be 'even','odd','day_of_week'")

PROGRAM_ID_KEY = "pid"
TIME_OF_DAY_KEY = "time_of_day"
INTERVAL_KEY = "interval"
IN_PROGRAM_KEY = "in_program"
TOTAL_RUN_TIME_KEY = "total_run_time"
STATION_DURATION_KEY = "station_duration"
STATION_ID_KEY = "stid"
DURATION_KEY = "duration"
IN_STATION_KEY = "in_station"

program_schema = {PROGRAM_ID_KEY : {"type":"integer"},
                  TIME_OF_DAY_KEY : {"type":"integer",
                                     "min":0},
                  INTERVAL_KEY : {"type":"dict",
                                  "validator":validate_interval},
                  IN_PROGRAM_KEY : {"type":"boolean"},
                  TOTAL_RUN_TIME_KEY : {"type" : "integer",
                                        "min" : 0},
                  STATION_DURATION_KEY : {"type" : "list",
                                          "schema" : {"type":"dict",
                                                      "schema":{STATION_ID_KEY : {"type":"integer",
                                                                                  "min":0},
                                                                DURATION_KEY : {"type":"integer",
                                                                                "min":0},
                                                                IN_STATION_KEY : {"type":"boolean"}}}}}

station_template = {PROGRAM_ID_KEY : -1,
                    TIME_OF_DAY_KEY : 0,
                    INTERVAL_KEY : "even",
                    IN_PROGRAM_KEY:False,
                    TOTAL_RUN_TIME_KEY:0,
                    STATION_DURATION_KEY : list()}
station_duration_template = {STATION_ID_KEY : -1,
                             DURATION_KEY : 0,
                             IN_STATION_KEY : False}

def _load(filename, validator):
    try:
        settings_file = open(filename)
        settings = json.load(settings_file)
        if validator.validate(settings):
            return settings
        else:
            return None
    except IOError:
        return None

def _dump(filename, validator, settings):
    valid = validator.validate(settings)
    if not valid:
        print "invalid"
        print validator.errors
        return False

    f = open(filename, "w")
    if f is None:
        return False
    try:
        json.dump(settings, f, indent=4)
        f.flush()
        f.close()
        return True
    except IOError:
        return False

def find_key_gap(l, start=1):
    if len(l) == 0:
        return start
    end = max(l)
    check_set = set(range(start, end+1))
    l = set(l)
    diff_set = check_set.difference(l)
    
    if len(diff_set) == 0:
        return end+1
    else:
        return min(diff_set)
    

class ControllerSettings(object):
    def __init__(self, settings_base=settings_base_dir):
        self.settings_base = settings_base
        #Master settings file lives here
        exist = os.path.exists(self.settings_base)
        #print self.settings_base, exist
        if not exist:
            os.makedirs(self.settings_base)
        self.master_file = os.path.join(self.settings_base, master_name)
        self.master_settings = None
        # programs are in the form of settings_base/program.*
        self.programs_finder = os.path.join(self.settings_base, "program.*")
        self.programs_validator = cerberus.Validator(program_schema, allow_unknown=True)
        self.programs = {}
    def __get_program_paths(self):
        return glob.glob(self.programs_finder)

    def __dump_program(self, program):
        pid = program["pid"]
        program_name = "program.%d" % pid
        path = os.path.join(self.settings_base, program_name)
        return _dump(path, self.programs_validator, program)
    def dump_all_programs(self):
        for program in self.programs.values():
            #print program
            self.__dump_program(program)
    def dump_program(self, pid):
        program = self.programs.get(pid, None)
        if program is None:
            return False
        return self.__dump_program(program)
    def delete_program(self, pid):
        program = self.programs.pop(pid, None)
        if program is None:
            return True
        program_name = "program.%d" % program["pid"]
        path = os.path.join(self.settings_base, program_name)
        try:
            os.remove(path)
            return True
        except OSError:
            return False
    def add_new_program(self, program):
        new_id = find_key_gap(self.programs.keys())
        program[PROGRAM_ID_KEY] = new_id
        self.programs[new_id] = program
        self.dump_program(new_id)
    def load_master(self):
        config = ConfigParser.ConfigParser()
        fs = config.read(self.master_file)
        if len(fs) == 0:
            return False
        master = OrderedDict()
        sections = config.sections()
        main_opts = config.options(MAIN_SECTION)
        #Load the main options
        for opt in main_opts:
            master[opt] = config.get(MAIN_SECTION, opt)
        sections.remove(MAIN_SECTION)
        # Load the station info
        station_list = OrderedDict()
        master[STATION_LIST_KEY] = station_list
        for section in sections:
            station_id = int(section.split(' ')[1])
            options = config.options(section)
            __od = OrderedDict()
            for option in options:
                if option in boolean_conf_keys:
                    __od[option] = config.getboolean(section,option)
                elif option in int_conf_keys:
                    __od[option] = config.getint(section,option)
                else:
                    __od[option] = config.get(section, option)
            station_list[station_id] = __od
        master[STATIONS_AVAIL_KEY] = int(master[STATIONS_AVAIL_KEY])
        self.master_settings = master
        return True
    def dump_master(self):
        if hasattr(self, "master_settings"):
            # Don't directly modify the master settings dict
            conf = copy.deepcopy(self.master_settings)
            config = ConfigParser.ConfigParser()
            station_list = conf.pop(STATION_LIST_KEY, None)
            # Write main settings
            config.add_section(MAIN_SECTION)
            for key, val in conf.items():
                config.set(MAIN_SECTION, key, val)
            # Write out the individual station settings
            for key, val in station_list.items():
                header = STATION_SECTION_KEY % key
                config.add_section(header)
                for k2, v2 in val.items():
                    config.set(header, k2, v2)
            fi = open(self.master_file, 'wb')
            config.write(fi)
            fi.flush()
            fi.close()
            del fi
            return True
        else:
            return False
    def get_programs(self):
        self.programs = {}
        for pp in self.__get_program_paths():
            # We need a validation here that program.* lines up with the Program ID.
            prog = _load(pp, self.programs_validator)
            if not prog is None:
                pid = prog["pid"]
                self.programs[pid] = prog

