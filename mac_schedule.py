import random
import sys
import time
from collections import defaultdict
from copy import copy
from dataclasses import dataclass, field
from itertools import count

sys.setrecursionlimit(int(1e+6))
random.seed(0)

PLANNING_HORIZON = 50
MIN_JOB_DURATION = 1
MAX_JOB_DURATION = 10
MIN_JOB_PROFIT = 50
MAX_JOB_PROFIT = 150
MIN_PRIORITY = 1
MAX_PRIORITY = 2
N_JOB = 40


@dataclass
class Range:
    start: int
    end: int

    def does_overlap(self, other: 'Range') -> bool:
        return self.start < other.end and other.start < self.end


@dataclass
class Job:
    priority: int
    profit: int
    range: Range
    id: int = field(init=False, default_factory=count().__next__)

    def does_overlap(self, other: 'Job') -> bool:
        return self.range.does_overlap(other.range)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


class Objective:
    profit: int
    high_priority_jobs: dict[int, int]
    _priority_order = [p for p in range(MIN_PRIORITY, MAX_PRIORITY + 1)]

    def __init__(self):
        self.profit = 0
        self.high_priority_jobs = defaultdict(int)

    def add_job(self, job: Job) -> "Objective":
        new_obj = self.copy()
        new_obj.profit += job.profit
        new_obj.high_priority_jobs[job.priority] += 1
        return new_obj

    def copy(self):
        new_obj = Objective()
        new_obj.profit = self.profit
        new_obj.high_priority_jobs = copy(self.high_priority_jobs)
        return new_obj

    def is_better(self, other: 'Objective') -> bool:
        if self.profit > other.profit:
            return True
        if self.profit < other.profit:
            return False

        for priority in self._priority_order:
            if self.high_priority_jobs[priority] > other.high_priority_jobs[priority]:
                return True
            if self.high_priority_jobs[priority] < other.high_priority_jobs[priority]:
                return False

        return False


@dataclass
class Solution:
    sol: list[Job]
    obj: Objective
    _ranges: frozenset[tuple[int, int]] = field(init=False)

    def __post_init__(self):
        self._ranges = frozenset((job.range.start, job.range.end) for job in self.sol)

    def is_job_feasible_to_add(self, job: Job) -> bool:
        for j in self.sol:
            if j.does_overlap(job):
                return False
        return True

    def add_job(self, job: Job) -> 'Solution':
        new_sol = self.sol + [job]
        new_obj = self.obj.add_job(job)
        return Solution(new_sol, new_obj)

    def print(self):
        sols = sorted(self.sol, key=lambda x: x.range.start)

        print(f"Objective: {self.obj.profit}")
        priorities = sorted(self.obj.high_priority_jobs.keys())
        for priority in priorities:
            print(f"{self.obj.high_priority_jobs[priority]} {priority} priority jobs")

        for job in sols:
            print(f"Job {job.id} | {job.priority}: {job.range.start}-{job.range.end}")

    def __repr__(self):
        return f"Solution(objective={self.obj.profit})"

    def __hash__(self):
        return hash(self._ranges)

    def __eq__(self, other):
        return self._ranges == other._ranges


def solve_recursive(jobs: tuple[Job, ...],
                    current_sol=None,
                    cache=None) -> Solution:
    if cache is None:
        cache = {}
    if current_sol is None:
        current_sol = Solution([], Objective())

    if len(jobs) == 0:
        return current_sol

    if (jobs, current_sol) in cache:
        return cache[jobs, current_sol]

    job = jobs[0]
    remaining_jobs = jobs[1:]

    without_job = solve_recursive(remaining_jobs, current_sol, cache)

    if current_sol.is_job_feasible_to_add(job):
        new_sol = current_sol.add_job(job)
        with_job = solve_recursive(remaining_jobs, new_sol, cache)

        best_sol = with_job if with_job.obj.is_better(without_job.obj) else without_job
    else:
        best_sol = without_job

    cache[jobs, current_sol] = best_sol
    return best_sol


def generate_random_job():
    duration = random.randint(MIN_JOB_DURATION, MAX_JOB_DURATION)
    start = random.randint(0, PLANNING_HORIZON - duration)
    priority = random.randint(MIN_PRIORITY, MAX_PRIORITY)
    profit = random.randint(MIN_JOB_PROFIT, MAX_JOB_PROFIT)
    return Job(priority,
               profit,
               Range(start, start + duration))


def check_sol_feasibility(sol: Solution):
    def does_two_ranges_overlap(range1: tuple[int, int], range2: tuple[int, int]) -> bool:
        return range1[0] < range2[1] and range2[0] < range1[1]

    ranges: list[tuple[int, int]] = []
    for job in sol.sol:
        for r in ranges:
            if does_two_ranges_overlap(r, (job.range.start, job.range.end)):
                return False
        ranges.append((job.range.start, job.range.end))
    return True


def draw_sol(sol: Solution):
    jobs = sol.sol
    for i in range(PLANNING_HORIZON):
        if any(job.range.start <= i < job.range.end for job in jobs):
            print("X", end="")
        else:
            print("-", end="")


jobs = [generate_random_job() for _ in range(N_JOB)]

start = time.time()
sol = solve_recursive(tuple(jobs))
print(f"Elapsed time: {time.time() - start}")

sol.print()
check_sol_feasibility(sol)
draw_sol(sol)

# Solved the problem using dynamic programming, considering it as a special case of the knapsack problem.
# In this case, the constraint is a time horizon rather than capacity.

# The Objective class represents the objective function for the problem.
# Objective A is considered better than Objective B if A has a higher profit
# or if it includes more high-priority jobs.
# Jobs with lower priority are consider higher priority.
