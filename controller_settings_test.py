from collections import OrderedDict
from controller_settings import ControllerSettings,make_test_settings

if __name__ == "__main__":

    Master = make_test_settings()

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
    cs.master_settings = Master
    print cs.dump_master()
    nm = cs.load_master()
    program = {1: program_1, 2: program_2, 3: program_3}
    cs.programs = program
    cs.dump_all_programs()
    cs.get_programs()
