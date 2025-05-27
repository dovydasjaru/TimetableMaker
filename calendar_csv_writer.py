from timetable import Timetable
import settings

def write_timetable(table: Timetable):
    with open(settings.file_name + ".csv", "w") as file:
        file.write("Subject,Start Date\n")
        for date, slot in table.slots.items():
            file.write(" & ".join(slot.workers.values()))
            file.write(",")
            file.write("{:02d}/{:02d}/{:d}".format(date.month, date.day, date.year))
            file.write("\n")
