import settings
from configuration import Configuration
from timetable import make_timetable
from excel_writer import write_timetable


if __name__ == '__main__':
    settings.init()
    print("Reading configuration file")
    config = Configuration(settings.configuration_file)
    print("Making timetable")
    table = make_timetable(config)
    print("Writing timetable to file")
    write_timetable(table)
    print("Done")

