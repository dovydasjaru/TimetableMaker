from datetime import date
from timetable import Timetable
import settings

def write_timetable(table: Timetable, default_time: str):
    """
    Writes given timetable into .ics file that should be supported by Google Calendar.
    :param Timetable to write into an iCalendar format.
    """
    with open(settings.file_name + ".ics", "w", encoding="utf-8") as file:
        file.write("BEGIN:VCALENDAR\n")
        file.write("VERSION:2.0\n")
        file.write("PRODID:<-//Google Inc//Google Calendar 70.9054//EN>\n")
        file.write("CALSCALE:GREGORIAN\n")
        file.write("METHOD:PUBLISH\n")
        file.write("X-WR-CALNAME:Timetable\n")
        
        for date, slot in table.slots.items():
            file.write(__make_calendar_event(slot.workers.values(), date, default_time))
        
        file.write("END:VCALENDAR")


def __make_calendar_event(worker_names: list[str], date: date, default_time: str) -> str:
    event = "BEGIN:VEVENT\n"
    event += "DTSTART:" + date.strftime("%Y%m%d") + "T" + default_time + "\n"
    event += "DTEND:" + date.strftime("%Y%m%d") + "T" + default_time + "\n"
    event += "SUMMARY:" + settings.together_separator.join(worker_names) + "\n"
    event += "START:VALARM\n"
    event += "ACTION:DISPLAY\n"
    event += "TRIGGER:-P" + str(settings.event_reminder_days) + "DT0H0M0S\n"
    event += "DESCRIPTION:" + settings.together_separator.join(worker_names) + "\n"
    event += "END:VALARM\n"
    return event + "END:VEVENT\n"
