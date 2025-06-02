import settings
from configuration import Configuration
from timetable import make_timetable
import excel_writer
import icalendar_writer

if __name__ == '__main__':
    print("Reading configuration file")
    config = Configuration(settings.configuration_file)
    print("Making timetable")
    table = make_timetable(config)
    print("Writing timetable to files")
    excel_writer.write_timetable(table)
    icalendar_writer.write_timetable(table, config.default_time)
    print("Done")

