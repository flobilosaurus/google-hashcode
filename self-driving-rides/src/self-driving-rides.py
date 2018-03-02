import utils
import typing
from typing import Dict
import copy

Point = typing.NamedTuple('Point', [('x', int), ('y', int)])
Ride = typing.NamedTuple('Ride',
                         [('number', int),
                          ('start', Point),
                          ('end', Point),
                          ('earliest_start', int),
                          ('latest_finish', int)])

# Beispiele
p = Point(1, 2)
ride1 = Ride(0, Point(0, 0), Point(2, 3), 0, 3)

def get_numbers_in_line(line: str):
    return map(int, line[0:-1].split(' '))


def get_input(lines: list):
    rows, columns, num_vehicles, num_rides, bonus, num_steps = get_numbers_in_line(lines[0])
    rides = []
    for i in range(1, len(lines)):
        x_start, y_start, x_end, y_end, earliest_start, latest_finish = get_numbers_in_line(lines[i])
        rides.append(Ride(i-1, Point(x_start, y_start), Point(x_end, y_end), earliest_start, latest_finish))
    return rows, columns, num_vehicles, num_rides, bonus, num_steps, rides


def get_distance(ride: Ride):
    return get_distance_between(ride.start, ride.end)


def get_distance_between(start: Point, end: Point):
    x_distance = abs(start.x - end.x)
    y_distance = abs(start.y - end.y)
    return x_distance + y_distance


def is_on_time(time_of_arival, latest_finish):
    return latest_finish >= time_of_arival


def waiting(cur_time, earliest_start):
    return max(0, earliest_start - cur_time)


def get_score(vehicle_to_rides: Dict, bonus: int, num_steps: int):
    score = 0
    for vehicle in vehicle_to_rides:
        cur_time = 0
        cur_point = Point(0, 0)
        for ride in vehicle_to_rides[vehicle]:
            if cur_time < num_steps:
                distance_to_start = get_distance_between(cur_point, ride.start)
                distance = get_distance(ride)
                cur_time += distance_to_start
                cur_time += waiting(cur_time, ride.earliest_start)
                if is_on_time(cur_time + distance, ride.latest_finish):
                    score += distance
                    if cur_time == ride.earliest_start:
                        score += bonus
                cur_time += distance
                cur_point = ride.end
    return score


def get_score_of_ride(ride: Ride, bonus, cur_pos, cur_time):
    distance_to_start = get_distance_between(cur_pos, ride.start)
    waiting_time = waiting(cur_time + distance_to_start, ride.earliest_start)
    is_bonus_possible = cur_time + distance_to_start <= ride.earliest_start
    ride_distance = get_distance(ride)

    applied_bonus = (int(is_bonus_possible) * bonus)

    earning = ride_distance + applied_bonus
    waisted_time = distance_to_start + waiting_time

    return earning - waisted_time


def get_scored_rides(cur_pos, cur_time, bonus, rides, score_function):
    scored_rides = [(ride, score_function(ride, bonus, cur_pos, cur_time)) for ride in rides]
    return sorted(scored_rides, key=lambda i: i[1], reverse=True)

import math

def get_greedy_solution(num_vehicles, rides, bonus, num_steps):
    remaining_rides = copy.deepcopy(rides)
    vehicle_to_rides = {v: [] for v in range(num_vehicles)}
    progress_printer = utils.ProgressPrinter(num_steps)
    cur_pos = {v: Point(0,0) for v in vehicle_to_rides}
    next_steps_busy = {v: 0 for v in vehicle_to_rides}

    for cur_step in range(num_steps+1):
        # if possible assign new ride
        for v in vehicle_to_rides:
            if next_steps_busy[v] <= 0: # not busy
                scored_rides = get_scored_rides(cur_pos[v], cur_step, bonus, remaining_rides,  get_score_of_ride)
                for ride, _ in scored_rides:
                    distance_of_ride = get_distance(ride)
                    distance_to_start = get_distance_between(cur_pos[v], ride.start)
                    waiting_time = waiting(cur_step + distance_to_start, ride.earliest_start)
                    time_needed = distance_to_start + waiting_time + distance_of_ride
                    if time_needed <= num_steps:
                        vehicle_to_rides[v].append(ride)
                        remaining_rides.remove(ride)
                        next_steps_busy[v] = time_needed
                        cur_pos[v] = ride.end
                        break

        # move vehicles
        for v in vehicle_to_rides:
            next_steps_busy[v] -= 1

        # print progress online ten times, expensive because of get_score
        if cur_step % (num_steps // 10) == 0:
            progress_printer.print(cur_step, get_score(vehicle_to_rides, bonus, num_steps))

    return vehicle_to_rides


def to_string(vehicle_to_rides):
    lines = []
    for vehicle in vehicle_to_rides:
        rides = vehicle_to_rides[vehicle]
        lines.extend([f"{len(rides)} {' '.join(map(lambda r: str(r.number), rides))}"])
    return lines


if __name__ == '__main__':
    instances = ['a_example', 'b_should_be_easy', 'c_no_hurry', 'd_metropolis', 'e_high_bonus']
    for instance in instances:
        print(f'\n\033[95msolving instance {instance}:\033[0m')
        rows, columns, num_vehicles, num_rides, bonus, num_steps, rides = utils.read_input(instance, get_input)
        vehicle_to_rides = get_greedy_solution(num_vehicles, rides, bonus, num_steps)
        utils.write_output(instance, to_string(vehicle_to_rides))