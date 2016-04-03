import pickle
import glob
import os
import os.path
import cerberus

settings_base_dir = "D:\\toys\\controller"
master_name = "master.cfg"

main_section = "Main"
station_settings = "Station Settings"
station_section = "Station %d"
ospi_version_key = 'OSPi Version'
tz_key = 'Time Zone'
sys_version_key = 'System Version'
date_format_key = 'Date Format'
time_format_key = 'Time Format'
location_key = 'Location'
rain_sensor_key = 'Rain Sensor'
invert_rain_sensor_key = 'Invert Rain Sensor'
stations_avail_key = 'Stations Available'
station_section_key = 'Station %d'
station_name_key = 'Name'
wired_key = 'Wired'
ignore_rain_key = 'Ignore Rain Sensor'
need_master_key = 'Need Master'

default_station_dict = {1:{'Name':'Station 1',
                           'Wired':True,
                           'Ignore Rain Sensor':False,
                           'Need Master':False},
                        2:{'Name':'Station 2',
                           'Wired':True,
                           'Ignore Rain Sensor':False,
                           'Need Master':False},
                        3:{'Name':'Station 3',
                           'Wired':True,
                           'Ignore Rain Sensor':False,
                           'Need Master':False},
                        4:{'Name':'Station 4',
                           'Wired':True,
                           'Ignore Rain Sensor':False,
                           'Need Master':False},
                        5:{'Name':'Station 5',
                           'Wired':True,
                           'Ignore Rain Sensor':False,
                           'Need Master':False},
                        6:{'Name':'Station 6',
                           'Wired':True,
                           'Ignore Rain Sensor':False,
                           'Need Master':False},
                        7:{'Name':'Station 7',
                           'Wired':False,
                           'Ignore Rain Sensor':False,
                           'Need Master':False},
                        8:{'Name':'Station 8',
                           'Wired':False,
                           'Ignore Rain Sensor':False,
                           'Need Master':False}}

default_master = {'Invert Rain Sensor': False,
                  'Rain Sensor': False,
                  'Time Format': '%H:%M:%S',
                  'Location': 'Garage',
                  'System Version': 'v1.0',
                  'Time Zone': 'SYSTEM',
                  'stations_wired': 6,
                  'OSPi Version': 'v1.4',
                  'Date Format': '%Y-%m-%d',
                  '"Station Settings' : {'Stations Available':8,
                                         'station list': default_station_dict}}



def validate_station_count(field, value, error):
    if not value % 8 == 0:
        error(field, "Must be an even multiple of 8")
master_settings_schema = {"stations_available": {"type":"integer",
                                                 "validator":validate_station_count,
                                                 "min":8},
                          "stations_wired" : {"type":"integer",
                                              "min":1},
                          "has_rain_sensor" : {"type":"boolean"},
                          "invert_rain_sensor" : {"type":"boolean"},
                          "timezone" : {"type" : "string"},
                          "date_format" : {"type" : "string"},
                          "time_format" : {"type" : "string"},
                          "location" : {"type" : "string"},
                          "format_version" : {"type" : "string"},
                          "controller_version" : {"type" : "string"}}

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

program_schema = {"pid" : {"type":"integer"},
                  "time_of_day" : {"type":"integer",
                                   "min":0},
                  "interval" : {"type":"dict",
                                "validator":validate_interval},
                  "in_program" : {"type":"boolean"},
                  "total_run_time" : {"type" : "integer",
                                      "min" : 0},
                  "station_duration" : {"type" : "list",
                                        "schema" : {"type":"dict",
                                                    "schema":{"stid" : {"type":"integer",
                                                                        "min":0},
                                                              "duration" : {"type":"integer",
                                                                            "min":0},
                                                              "in_station": {"type":"boolean"}}}}}


def _load(filename, validator):
    try:
        settings_file = open(filename)
        settings = pickle.load(settings_file)
        if validator.validate(settings):
            return settings
        else:
            return None
    except pickle.UnpicklingError:
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
        pickle.dump(settings, f)
        f.flush()
        f.close()
        return True
    except pickle.PicklingError:
        return False

class ControllerSettings(object):
    def __init__(self, settings_base=settings_base_dir):
        self.settings_base = settings_base
        #Master settings file lives here
        exist = os.path.exists(self.settings_base)
        print self.settings_base, exist
        if not exist:
            os.makedirs(self.settings_base)
        self.master_file = os.path.join(self.settings_base, "master")
        #self.master_validator = cerberus.Validator(master_settings_schema)
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
            print program
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
    def load_master(self):
        settings = _load(self.master_file, self.master_validator)
        if settings is None:
            return False
        self.master_settings = settings
        return True
    def dump_master(self):
        if hasattr(self, "master_settings"):
            res = _dump(self.master_file, self.master_validator, self.master_settings)
            return res
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

