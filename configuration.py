import json
from datetime import date, timedelta
from typing import List, Dict
from math import floor, ceil


class Worker:
    name: str
    is_in_all_positions: bool
    positions: List[str]
    positions_with_help: List[str]
    appears_on_cycle: List[bool]
    date_exceptions: List[date]

    def __init__(self, name: str, properties: dict):
        self.name = name
        self.is_in_all_positions = properties.get("is_in_all_positions", False)

        if not self.is_in_all_positions:
            self.positions = properties.get("positions", [])
            self.positions_with_help = properties.get("positions_with_help", [])
        else:
            self.positions = []
            self.positions_with_help = []

        appearance_skips = floor(properties.get("appearance_skips", 0))
        if appearance_skips > 0:
            self.appears_on_cycle = [False] * appearance_skips
            self.appears_on_cycle.append(True)
        else:
            self.appears_on_cycle = [True]

        self.date_exceptions = []
        for date_string in properties.get("date_exceptions", []):
            self.date_exceptions.append(date.fromisoformat(date_string))


class Configuration:
    cycles: int
    slots_in_cycle: int
    interval: timedelta
    starting_slot_date: date
    last_slot_date: date
    positions: List[str]
    workers: Dict[str, Worker]

    def __init__(self, file: str):
        config: dict
        with open(file) as config_file:
            config = json.load(config_file)
        self.interval = timedelta(days=config["interval"])
        self.starting_slot_date = date.fromisoformat(config["starting_date"])
        self.last_slot_date = date.fromisoformat(config["ending_date"])
        self.positions = config["positions"]
        worker_dict: dict = config["workers"]
        self.workers = {}
        for name, properties in worker_dict.items():
            self.workers[name] = Worker(name, properties)

        appears_in_all: int = 0
        appears_in_position: Dict[str, int] = {}
        for position in self.positions:
            appears_in_position[position] = 0
        for worker in self.workers.values():
            if worker.is_in_all_positions and worker.appears_on_cycle[0]:
                appears_in_all += 1
            else:
                for position in worker.positions:
                    appears_in_position[position] += 1

        self.slots_in_cycle = appears_in_all + min(appears_in_position.values())
        timetable_slots = (self.last_slot_date - self.starting_slot_date).days / self.interval.days
        self.cycles = ceil(timetable_slots / self.slots_in_cycle)
