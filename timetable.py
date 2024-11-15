from typing import List, Optional, Dict, Callable
import random
from datetime import date
from configuration import Configuration, Worker
import settings


class WorkersWithPositionGenerator:
    workers_for_positions: Dict[str, List[str]]
    positions_index: Dict[str, int]
    reached_end: bool

    def __init__(self, workers_for_positions: Dict[str, List[str]]):
        self.workers_for_positions = workers_for_positions
        self.positions_index = {}
        self.reached_end = False
        for position in self.workers_for_positions.keys():
            self.positions_index[position] = 0

    def get_next_workers_with_position(self) -> Optional[Dict[str, str]]:
        if self.reached_end:
            return None

        chosen_workers: Dict[str, str] = {}
        do_increment = True
        overflow_count = 0

        for position, index in self.positions_index.items():
            chosen_workers[position] = self.workers_for_positions[position][index]

            if do_increment:
                self.positions_index[position] += 1
                if self.positions_index[position] < len(self.workers_for_positions[position]):
                    do_increment = False
                    continue

                overflow_count += 1
                self.positions_index[position] = 0

        if overflow_count == len(self.workers_for_positions.keys()):
            self.reached_end = True

        return chosen_workers


class Slot:
    workers: Dict[str, str]

    def __init__(self, workers: Dict[str, str]):
        self.workers = workers


class Timetable:
    slots: Dict[date, Slot]
    positions: List[str]

    def __init__(self, positions: List[str]):
        self.slots = {}
        self.positions = positions

    def add_new_slot(self, slot_date: date, workers: Slot):
        self.slots[slot_date] = workers


def filter_trainers(worker: Worker, position: str) -> bool:
    return worker.is_in_all_positions or position in worker.positions


def filter_trainees(worker: Worker, position: str) -> bool:
    return position in worker.positions_with_help


def make_timetable(config: Configuration) -> Timetable:
    table = Timetable(config.positions)
    for cycle_index in range(config.cycles):
        workers_with_position: Dict[str, List[Worker]] = \
            filter_workers(config.positions, cycle_index, config.workers, filter_trainers)

        workers_in_slots: Dict[date, Slot] = \
            randomly_sort_workers_into_slots(config, workers_with_position)

        if workers_in_slots is None:
            raise Exception("Can't create worker timetable, because of worker positions or date exceptions")

        trainees_with_position: Dict[str, List[Worker]] = \
            filter_workers(config.positions, cycle_index, config.workers, filter_trainees)

        assign_trainees_to_trainers(workers_in_slots, trainees_with_position)

        for slot_date, workers_in_slot in workers_in_slots.items():
            table.add_new_slot(slot_date, workers_in_slot)

    return table


def assign_trainees_to_trainers(slotted_trainers: Dict[date, Slot], trainees: Dict[str, List[Worker]]):
    for position, trainees_for_position in trainees.items():
        random_dates = random.sample(list(slotted_trainers.keys()), len(slotted_trainers.keys()))

        for trainee in trainees_for_position:
            for possible_date in random_dates:
                if settings.helping_separator in slotted_trainers[possible_date].workers[position] or \
                        possible_date in trainee.date_exceptions:
                    continue

                slotted_trainers[possible_date].workers[position] += settings.helping_separator + trainee.name
                break



def filter_workers(positions: List[str], cycle: int, workers: Dict[str, Worker],
                   filter_f: Callable[[Worker, str], bool]) -> Dict[str, List[Worker]]:
    """
    :param positions: Available positions
    :param cycle: Which cycle are you generating
    :param workers: [worker name, Worker] dictionary
    :param filter_f: function by which workers will be filtered
    :return: [position, List[worker name]] dictionary of workers that do not need help
    """
    position_to_workers_without_help: Dict[str, List[Worker]] = {}

    position_index: int = 0
    for position in positions:
        position_to_workers_without_help[position] = []
        for name, worker in workers.items():
            if not worker.appears_on_cycle[(cycle + position_index) % len(worker.appears_on_cycle)]:
                continue

            if filter_f(worker, position):
                position_to_workers_without_help[position].append(worker)

        position_index += 1

    return position_to_workers_without_help


def randomly_sort_workers_into_slots(config: Configuration, workers_for_cycle: Dict[str, List[Worker]]) -> \
        Optional[Dict[date, Slot]]:
    """
    :param config: Configuration
    :param workers_for_cycle: Dict[position, List[worker name]] dictionary of position to worker names
    :return: List[Slot] list of a working timetable for a cycle if not, None
    """
    available_slots_per_position = map(lambda workers_list: len(workers_list), workers_for_cycle.values())
    config.slots_in_cycle = min(available_slots_per_position)

    workers_for_slots: Dict[date, Dict[str, List[str]]] = {}
    next_slot_date: date = config.starting_slot_date
    for slot_index in range(config.slots_in_cycle):
        workers_for_slots[next_slot_date] = {}
        for position in config.positions:
            workers = \
                list(filter(lambda worker: next_slot_date not in worker.date_exceptions, workers_for_cycle[position]))
            workers_for_slots[next_slot_date][position] = list(map(lambda worker: worker.name, workers))
            random.shuffle(workers_for_slots[next_slot_date][position])

        next_slot_date += config.interval

    config.starting_slot_date = next_slot_date

    return choose_worker_for_each_slot(workers_for_slots)


def choose_worker_for_each_slot(workers_for_slots: Dict[date, Dict[str, List[str]]],
                                chosen_workers: Dict[str, List[str]] = None) -> Optional[Dict[date, Slot]]:
    if workers_for_slots == {}:
        return {}

    slot_date, workers_for_slot = workers_for_slots.popitem()
    if chosen_workers is None:
        chosen_workers = {}
        for position in workers_for_slot.keys():
            chosen_workers[position] = []

    for position, workers in workers_for_slot.items():
        workers_for_slot[position] = list(filter(lambda name: name not in chosen_workers[position], workers))
        if len(workers_for_slot[position]) == 0:
            return None

    worker_generator = WorkersWithPositionGenerator(workers_for_slot)

    workers_choice = worker_generator.get_next_workers_with_position()
    while workers_choice is not None:
        chosen_slots: Optional[Dict[date, Slot]] = None

        currently_chosen_workers: Dict[str, List[str]] = {}
        for position, names in chosen_workers.items():
            currently_chosen_workers[position] = names.copy()
            currently_chosen_workers[position].append(workers_choice[position])

        if len(set(workers_choice.values())) == len(workers_choice.keys()):
            chosen_slots = choose_worker_for_each_slot(make_deep_copy(workers_for_slots), currently_chosen_workers)

        if chosen_slots is None:
            workers_choice = worker_generator.get_next_workers_with_position()
            continue

        chosen_slots[slot_date] = Slot(workers_choice)
        return chosen_slots

    return None


def make_deep_copy(item: Dict[date, Dict[str, List[str]]]) -> Dict[date, Dict[str, List[str]]]:
    deep_copy: Dict[date, Dict[str, List[str]]] = {}
    for date_key, dict_value in item.items():
        deep_copy[date_key] = {}
        for str_key, list_value in dict_value.items():
            deep_copy[date_key][str_key] = list_value.copy()

    return deep_copy
