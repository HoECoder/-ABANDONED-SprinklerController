import pickle
import glob
import os
import os.path
import copy
from collections import OrderedDict
import ConfigParser
import cerberus

settings_base_dir = "D:\\toys\\controller"
master_name = "master.cfg"

main_section = 'Main'
station_settings_key = 'Station Settings'
ospi_version_key = 'ospi version'
station_section_key = 'Station %d'
tz_key = 'time zone'
sys_version_key = 'system version'
date_format_key = 'date format'
time_format_key = 'time format'
location_key = 'location'
rain_sensor_key = 'rain sensor'
invert_rain_sensor_key = 'invert rain sensor'
stations_avail_key = 'stations available'
station_name_key = 'name'
wired_key = 'wired'
ignore_rain_key = 'ignore rain sensor'
need_master_key = 'need master'
station_list_key = 'station list'

__station_template = OrderedDict()
__station_template[station_name_key] = ''
__station_template[wired_key] = True
__station_template[ignore_rain_key] = False
__station_template[need_master_key] = False

default_station_dict = OrderedDict()
__temp = copy.deepcopy(__station_template)
__temp[station_name_key] = 'Station 1'
default_station_dict[1] = __temp
__temp = copy.deepcopy(__station_template)
__temp[station_name_key] = 'Station 2'
default_station_dict[2] = __temp
__temp = copy.deepcopy(__station_template)
__temp[station_name_key] = 'Station 3'
default_station_dict[3] = __temp
__temp = copy.deepcopy(__station_template)
__temp[station_name_key] = 'Station 4'
default_station_dict[4] = __temp
__temp = copy.deepcopy(__station_template)
__temp[station_name_key] = 'Station 5'
default_station_dict[5] = __temp
__temp = copy.deepcopy(__station_template)
__temp[station_name_key] = 'Station 6'
default_station_dict[6] = __temp
__temp = copy.deepcopy(__station_template)
__temp[station_name_key] = 'Station 7'
__temp[wired_key] = False
default_station_dict[7] = __temp
__temp = copy.deepcopy(__station_template)
__temp[station_name_key] = 'Station 8'
__temp[wired_key] = False
default_station_dict[8] = __temp

default_master = OrderedDict()
default_master[sys_version_key] = 'v1.0'
default_master[ospi_version_key] = 'v1.4'
default_master[time_format_key] = '%H:%M:%S'
default_master[date_format_key] = '%Y-%m-%d'
default_master[tz_key] = 'SYSTEM'
default_master[location_key] = 'Garage'
default_master[invert_rain_sensor_key] = False
default_master[rain_sensor_key] = False
default_master[stations_avail_key] = 8
default_master[station_list_key] = default_station_dict

def make_test_settings():
    __station_template = OrderedDict()
    __station_template[station_name_key] = ''
    __station_template[wired_key] = True
    __station_template[ignore_rain_key] = False
    __station_template[need_master_key] = False

    Station_Dict = OrderedDict()
    __temp = copy.deepcopy(__station_template)
    __temp[station_name_key] = 'Station 1'
    Station_Dict[1] = __temp
    __temp = copy.deepcopy(__station_template)
    __temp[station_name_key] = 'Station 2'
    Station_Dict[2] = __temp
    __temp = copy.deepcopy(__station_template)
    __temp[station_name_key] = 'Station 3'
    Station_Dict[3] = __temp
    __temp = copy.deepcopy(__station_template)
    __temp[station_name_key] = 'Station 4'
    Station_Dict[4] = __temp
    __temp = copy.deepcopy(__station_template)
    __temp[station_name_key] = 'Station 5'
    Station_Dict[5] = __temp
    __temp = copy.deepcopy(__station_template)
    __temp[station_name_key] = 'Station 6'
    Station_Dict[6] = __temp
    __temp = copy.deepcopy(__station_template)
    __temp[station_name_key] = 'Station 7'
    __temp[wired_key] = False
    Station_Dict[7] = __temp
    __temp = copy.deepcopy(__station_template)
    __temp[station_name_key] = 'Station 8'
    __temp[wired_key] = False
    Station_Dict[8] = __temp

    Master = OrderedDict()
    Master[sys_version_key] = 'v1.0'
    Master[ospi_version_key] = 'v1.4'
    Master[time_format_key] = '%H:%M:%S'
    Master[date_format_key] = '%Y-%m-%d'
    Master[tz_key] = 'SYSTEM'
    Master[location_key] = 'Garage'
    Master[invert_rain_sensor_key] = False
    Master[rain_sensor_key] = False
    Master[stations_avail_key] = 8
    Master[station_list_key] = Station_Dict
    return Master

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
        config = ConfigParser.ConfigParser()
        fs = config.read(self.master_file)
        if len(fs) == 0:
            return False
        master = OrderedDict()
        sections = config.sections()
        main_opts = config.options(main_section)
        #Load the main options
        for opt in main_opts:
            master[opt] = config.get(main_section, opt)
        sections.remove(main_section)
        # Load the station info
        station_list = OrderedDict()
        master[station_list_key] = station_list
        for section in sections:
            station_id = int(section.split(' ')[1])
            options = config.options(section)
            __od = OrderedDict()
            for option in options:
                __od[option] = config.get(section, option)
            station_list[station_id] = __od
        self.master_settings = master
        return True
    def dump_master(self):
        if hasattr(self, "master_settings"):
            # Don't directly modify the master settings dict
            conf = copy.deepcopy(self.master_settings)
            config = ConfigParser.ConfigParser()
            station_list = conf.pop(station_list_key, None)
            # Write main settings
            config.add_section(main_section)
            for key, val in conf.items():
                config.set(main_section, key, val)
            # Write out the individual station settings
            for key, val in station_list.items():
                header = station_section_key % key
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

