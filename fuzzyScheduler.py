from sys import argv
from re import *
from inspect import *
from cspProblem import Constraint

# read input file
file_name = argv[1]
# file_name = "input1.txt"

# Numeric representation in hours
days_in_week = {"mon":1, "tue":2, "wed":3, "thu":4, "fri":5}
hours_of_day = {"9am":9, "10am":10, "11am":11, "12pm":12, "1pm":13, "2pm":14, "3pm":15, "4pm":16, "5pm":17}

# process inputs
# for line in lines:
    ## constraints
    # Unary constraints
    # Binary constraints
    # Hard domain constraints

    # Soft deadline constraints
    # Tasks : task, ⟨name⟩ ⟨duration⟩ - tuple
    # tasks = list()
    # task_regex = search("task, (?P<name>\S*) (?P<duration>\S*)",line)
    # if task_regex is not None:
    #     tasks.append((task_regex.group("name"),task_regex.group("duration")))

def main():
    lines = read_file_to_lines(file_name)
    domain = get_domain_from_lines(lines)
    tasks = get_tasks_from_domain(domain)
    get_hard_constraints_from_lines(lines,tasks)
    # print(lines)
    # for d in domain:
    #     print(d)
    #     for time in domain[d]:
    #         print("start-time:\t", time[0].day, "\t", time[0].hour, "\tfinish-time:\t", time[1].day, "\t", time[1].hour)

def read_file_to_lines(file_name):
    with open(file_name) as fp: 
        lines = fp.readlines()
        for line in lines:
            if line.startswith('#'):
                lines.remove(line) # Remove comment
    return lines

def get_domain_from_lines(lines):
    domain = dict()
    for line in lines:
        match = search(r"task, (?P<name>\S*) (?P<duration>\S*)",line)
        if match is not None:
            variable_name = match.group("name")
            duration = int(match.group("duration"))
            domain[variable_name] = list() # new variable found
            
            # get domain for each variable
            for day in days_in_week.values():
                for hour in hours_of_day.values():
                    start_time = Time(day,hour)
                    finish_time = Time(start_time,duration)
                    #do not add to domain if task cannot finish on same day
                    if start_time.day != finish_time.day:
                        continue
                    if finish_time.hour > hours_of_day["5pm"]:
                        continue
                    domain[variable_name].append((start_time,finish_time)) # domain includes task name and available time slots
    return domain

def get_tasks_from_domain(domain):
    tasks = list()
    for task_name in domain:
        tasks.append(Task(task_name))
    return tasks

def get_hard_constraints_from_lines(lines,tasks):
    binary_constraints = get_binary_constraints_from_lines(lines,tasks)
    #DEBUG:
    for bc in binary_constraints:
        print(bc.scope[0].name, bc.scope[1].name, getsource(bc.condition))

def get_binary_constraints_from_lines(lines,tasks):
    binary_constraints = list()
    for line in lines:
        match = search(r"^constraint, (?P<t1>\S*) (?P<type>\S*) (?P<t2>\S*)",line)
        if match is not None:
            t1 = get_task_by_name(match.group("t1"),tasks)
            binary_constraint_type = match.group("type")
            t2 = get_task_by_name(match.group("t2"),tasks)

            if binary_constraint_type == "before":
                scope = (t1, t2)
                condition = lambda t1, t2: t1.start_time <= t2.start_time
            elif binary_constraint_type == "after":
                scope = (t1, t2)
                condition = lambda t1, t2: t1.start_time >= t2.start_time
            elif binary_constraint_type == "same-day":
                scope = (t1, t2)
                condition = lambda t1, t2: t1.start_time.day == t2.start_time.day
            elif binary_constraint_type == "starts-at":
                scope = (t1, t2)
                condition = lambda t1, t2: t1.start_time.day == t2.start_time.day and t1.start_time.hour == t2.start_time.hour
            else :
                exit("Invalid binary constraint")
            
            binary_constraints.append(Constraint(scope,condition))
    return binary_constraints

def get_domain_constraints_from_lines(lines):
    pass

###### Custom Class : Task ######
class Task:
    def __init__(self, name, start_time=None, finish_time=None):
        self.name = name
        self.start_time = start_time
        self.finish_time = finish_time
    
    def set_time(self, start_time, finish_time):
        self.start_time = start_time
        self.finish_time = finish_time

def get_task_by_name(name, tasks):
    for task in tasks:
        if name == task.name:
            return task
    return None # task not found

###### Custom Class : Time ######
class Time:
    # Constants
    WORK_HOURS_A_DAY = 8
    FULL_HOURS_A_DAY = 24
    
    # Constructor
    def __init__(self, arg1, arg2):
        if isinstance(arg1, int) and isinstance(arg2, int): # day and hour
            self.day = arg1
            self.hour = arg2
        elif isinstance(arg1, Time) and isinstance(arg2, int): # time and duration
            start_time = arg1
            duration = arg2
            extra_number_of_days = duration // self.WORK_HOURS_A_DAY
            extra_hours = duration % self.WORK_HOURS_A_DAY
            self.day = start_time.day + extra_number_of_days
            self.hour = start_time.hour + extra_hours

if __name__ == '__main__':
    main()         

