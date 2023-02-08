configuration_file: str
helping_separator: str
excel_file: str


def init():
    global configuration_file
    configuration_file = "config.json"
    global helping_separator
    helping_separator = " + "
    global excel_file
    excel_file = "timetable.xlsx"
