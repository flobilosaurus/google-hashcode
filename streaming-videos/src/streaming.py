from typing import Dict
import random
import math
import copy
import utils

random.seed(1)
datacenter = -1

def get_numbers_in_line(line: str):
    return map(int, line[0:-1].split(' '))


def get_input(lines: list) -> (Dict[int, Dict], Dict[int, Dict], Dict[int, int], int, int):
    num_videos, num_endpoints, num_request_descriptions, num_cache_server, cache_size = get_numbers_in_line(lines[0])
    video_sizes = {i: s for i, s in enumerate(get_numbers_in_line(lines[1]))}
    offset = 2
    latencies = {}
    for endpoint in range(num_endpoints):
        latency_datacenter, num_caches = get_numbers_in_line(lines[offset])
        endpoint_latencies = {datacenter: latency_datacenter}
        for i in range(num_caches):
            offset += 1
            cache, latency = get_numbers_in_line(lines[offset])
            endpoint_latencies[cache] = latency
        latencies[endpoint] = endpoint_latencies
        offset += 1

    requests = {v: {} for v in range(num_videos)}
    for i in range(offset, len(lines)):
        video, endpoint, num_requests = get_numbers_in_line(lines[i])
        offset += 1
        requests[video][endpoint] = num_requests

    return latencies, requests, video_sizes, cache_size, num_cache_server


def get_cache_importance(latencies, requests, video_sizes, num_caches):
    cache_importance = {}
    for cache in range(num_caches):
        video_importance = []
        for video in requests:
            video_size = video_sizes[video]
            importance = 0
            for endpoint in requests[video]:
                num_requests = requests[video][endpoint]
                latency_datacenter = latencies[endpoint][datacenter]
                if cache in latencies[endpoint]:
                    latency = latencies[endpoint][cache]
                    endpoint_importance = math.ceil(((latency_datacenter - latency) * num_requests) / video_size)
                    importance += endpoint_importance
            video_importance.append((video, importance))
        cache_importance[cache] = sorted(video_importance, key=lambda x: x[1], reverse=True)
    return cache_importance


def score(latencies, requests, allocation):
    sum_reduced_latency = 0
    sum_num_requests = 0
    for video in requests:
        for endpoint in requests[video]:
            num_requests = requests[video][endpoint]
            sum_num_requests += num_requests
            min_latency = latencies[endpoint][datacenter]
            for cache in allocation:
                if cache in latencies[endpoint] and video in allocation[cache]:
                    if latencies[endpoint][cache] < min_latency:
                        min_latency = latencies[endpoint][cache]
            reduced_latency = latencies[endpoint][datacenter] - min_latency
            sum_reduced_latency += reduced_latency * num_requests
    return math.ceil(sum_reduced_latency / sum_num_requests * 1000)


def is_allocation_valid(video_sizes, cache_size, num_caches, allocation):
    space_left = {i: cache_size for i in range(num_caches)}
    for cache in allocation:
        for video in allocation[cache]:
            space = space_left[cache]
            video_size = video_sizes[video]
            if video_size > space:
                return False
            else:
                space_left[cache] -= video_size
    return True


def mutate(allocation: Dict, num_videos) -> Dict:
    if random.randint(0, 1) > 0:
        return swap(allocation)
    else:
        return add(allocation, num_videos)


def swap(allocation):
    first_cache = random.randint(0, len(allocation) - 1)
    while not allocation[first_cache]:
        first_cache = random.randint(0, len(allocation) - 1)
    copy_of_first_cache = copy.deepcopy(allocation[first_cache])
    first_video = allocation[first_cache].pop()

    second_cache = random.randint(0, len(allocation) - 1)
    while not allocation[second_cache]:
        second_cache = random.randint(0, len(allocation) - 1)
    copy_of_second_cache = copy.deepcopy(allocation[second_cache])
    second_video = allocation[second_cache].pop()

    allocation[first_cache].add(second_video)
    allocation[second_cache].add(first_video)

    def rollback():
        allocation[first_cache] = copy_of_first_cache
        allocation[second_cache] = copy_of_second_cache

    return rollback


def add(allocation, num_videos):
    cache = random.randint(0, len(allocation) - 1)
    while len(allocation[cache]) >= num_videos:
        cache = random.randint(0, len(allocation) - 1)
    video = ({c for c in range(num_caches)} - allocation[cache]).pop()
    allocation[cache].add(video)

    def rollback():
        allocation[cache].remove(video)

    return rollback


def solve_by_local_search(cache_importance, latencies, requests, video_sizes, cache_size, num_caches):
    allocation = get_initial_allocation(cache_importance, video_sizes, num_caches, cache_size)
    current_score = score(latencies, requests, allocation)
    num_mutation_steps = 100000
    progress_printer = utils.ProgressPrinter(num_mutation_steps)
    for i in range(num_mutation_steps):
        rollback_action = mutate(allocation, len(video_sizes))
        if is_allocation_valid(video_sizes, cache_size, num_caches, allocation):
            mutation_score = score(latencies, requests, allocation)
            if current_score < mutation_score:
                current_score = mutation_score
            else:
                rollback_action()
        else:
            rollback_action()
        progress_printer.print(i+1, current_score)

    return allocation


def get_initial_allocation(cache_importance, video_sizes, num_caches, cache_size):
    allocation = {c: set() for c in range(num_caches)}
    space_left = {c: cache_size for c in range(num_caches)}
    already_cached = []
    for cache in cache_importance:
        for video, _ in cache_importance[cache]:
            if video_sizes[video] <= space_left[cache] and video not in already_cached:
                already_cached.append(video)
                allocation[cache].add(video)
                space_left[cache] -= video_sizes[video]
    return allocation


def to_string(allocation):
    used_caches = {cache for cache in allocation if allocation[cache]}
    lines = [f"{len(used_caches)}"]
    for cache in allocation:
        lines.extend([f"{cache} {' '.join(map(str, allocation[cache]))}"])
    return lines


if __name__ == '__main__':
    instances = ['example', 'me_at_the_zoo', 'videos_worth_spreading', 'trending_today', 'kittens']

    for instance in instances:
        print(f'\n\033[95msolving instance {instance}:\033[0m')
        latencies, requests, video_sizes, cache_size, num_caches = utils.read_input(instance, get_input)
        cache_importance = get_cache_importance(latencies, requests, video_sizes, num_caches)
        allocation = solve_by_local_search(cache_importance, latencies, requests, video_sizes, cache_size, num_caches)
        utils.write_output(instance, to_string(allocation))
