import pickle
import glob
import os
import os.path
import cerberus

settings_base_dir = "D:\\toys\\controller"

default_master = {'invert_rain_sensor': False,
                  'has_rain_sensor': False,
                  'time_format': '%H:%M:%S',
                  'location': 'Garage',
                  'format_version': 'v1.0',
                  'timezone': 'SYSTEM',
                  'stations_wired': 6,
                  'controller_version': 'v1.4',
                  'stations_available': 8,
                  'date_format': '%Y-%m-%d'}

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


class ControllerSettings(object):
    def __init__(self, settings_base=settings_base_dir):
        self.settings_base = settings_base
        #Master settings file lives here
        exist = os.path.exists(self.settings_base)
        print self.settings_base, exist
        if not exist:
            os.makedirs(self.settings_base)
        self.master_file = os.path.join(self.settings_base, "master")
        self.master_validator = cerberus.Validator(master_settings_schema)
        self.master_settings = None
        # programs are in the form of settings_base/program.*
        self.programs_finder = os.path.join(self.settings_base, "program.*")
        self.programs_validator = cerberus.Validator(program_schema,allow_unknown=True)
        self.programs = {}
    def __get_program_paths(self):
        return glob.glob(self.programs_finder)
    def __load(self, filename, validator):
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

    def __dump(self, filename, validator, settings):
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
    def __dump_program(self, program):
        pid = program["pid"]
        program_name = "program.%d" % pid
        path = os.path.join(self.settings_base, program_name)
        return self.__dump(path, self.programs_validator, program)
    def dump_all_programs(self):
        for program in self.programs.values():
            print program
            self.__dump_program(program)
    def dump_program(self, pid):
        program = self.programs.get(pid, None)
        if None:
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
        settings = self.__load(self.master_file, self.master_validator)
        if settings is None:
            return False
        self.master_settings = settings
        return True
    def dump_master(self):
        if hasattr(self, "master_settings"):
            res = self.__dump(self.master_file, self.master_validator, self.master_settings)
            return res
        else:
            return False
    def get_programs(self):
        self.programs = {}
        for pp in self.__get_program_paths():
            # We need a validation here that program.* lines up with the Program ID.
            prog = self.__load(pp, self.programs_validator)
            if not prog is None:
                pid = prog["pid"]
                self.programs[pid] = prog


if __name__ == "__main__":
    master = {'invert_rain_sensor': False,
              'has_rain_sensor': False,
              'time_format': '%H:%M:%S',
              'location': 'Garage',
              'format_version': 'v1.0',
              'timezone': 'SYSTEM',
              'stations_wired': 6,
              'controller_version': 'v1.4',
              'stations_available': 8,
              'date_format': '%Y-%m-%d'}

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
    program_2 = {"pid": 2,
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
    program_3 = {"pid": 3,
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
    
    cs = ControllerSettings()
    print cs.master_file
    cs.master_settings = master
    print cs.dump_master()
    nm = cs.load_master()
    program = {1: program_1, 2: program_2, 3: program_3}
    cs.programs = program
    cs.dump_all_programs()
    cs.get_programs()
