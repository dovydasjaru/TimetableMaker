import settings
from configuration import Configuration
from timetable import make_timetable
import excel_writer
import calendar_csv_writer

if __name__ == '__main__':
    print("Reading configuration file")
    config = Configuration(settings.configuration_file)
    print("Making timetable")
    table = make_timetable(config)
    print("Writing timetable to file")
    excel_writer.write_timetable(table)
    calendar_csv_writer.write_timetable(table)
    print("Done")

