from pandas import DataFrame, Series, ExcelWriter
from typing import Dict
from timetable import Timetable
import settings


def write_timetable(table: Timetable):
    columns: Dict[str, Series] = {}

    for slot_date, current_slot in table.slots.items():
        new_column = Series(data=current_slot.workers, index=table.positions)
        columns[slot_date.isoformat()] = new_column

    data_to_write = DataFrame(data=columns, index=table.positions)
    writer = ExcelWriter(settings.excel_file)
    data_to_write.to_excel(writer, sheet_name='my_analysis')

    for column in data_to_write:
        column_width = max(data_to_write[column].astype(str).map(len).max(), len(column))
        col_idx = data_to_write.columns.get_loc(column) + 1
        writer.sheets['my_analysis'].set_column(col_idx, col_idx, column_width)

    writer.save()
