import pickle
import os.path
import cerberus

settings_base_dir = "D:\\toys\\controller"

def validate_station_count(field, value, error):
    if value % 8 == 0:
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
        self.master_file = os.path.join(self.settings_base, "master")
        self.master_validator = cerberus.Validator(master_settings_schema)
        self.programs_file = os.path.join(self.settings_base, "programs")
        self.programs_validator = cerberus.Validator(program_schema)
    def __load(self, filename, validator):
        with open(filename) as f:
            try:
                settings = pickle.load(f)
                if validator.validate(settings):
                    return settings
            except pickle.UnpicklingError:
                return None
    def loadMaster(self):
        settings = self.__load(self.master_file, self.master_validator)
        if settings is None:
            return False
        self.master_settings = settings
        return True
    def loadPrograms(self):
        settings = self.__load(self.programs_file, self.programs_validator)
        if settings is None:
            return False
        self.programs = settings
        return True
    def __dump(self, filename, validator, settings):
        valid = validator.validate(settings)
        if not valid:
            print "invalid"
            return False

        f = open(filename, "w+")
        if f is None:
            return False
        try:
            pickle.dump(settings, f)
            f.flush()
            f.close()
            return True
        except pickle.PicklingError:
            return False
    def dumpMaster(self):
        if hasattr(self, "master_settings"):
            res = self.__dump(self.master_file, self.master_validator, self.master_settings)
            return res
        else:
            return False
    def dumpPrograms(self):
        if hasattr(self, "programs"):
            res = self.__dump(self.programs_file, self.programs_validator, self.programs)
            return res
        else:
            return False


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
    cs = ControllerSettings()
    print cs.master_file
    cs.master_settings = master
    print cs.dumpMaster()
    nm = cs.loadMaster()
