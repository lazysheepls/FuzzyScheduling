from sys import argv
from re import *
from cspProblem import Constraint

# read input file
file_name = argv[1]
# file_name = "input1.txt"

# Numeric representation in hours
days_in_week = {"mon":10, "tue":20, "wed":30, "thu":40, "fri":50}
hours_of_day = {"9am":0, "10am":1, "11am":2, "12pm":3, "1pm":4, "2pm":5, "3pm":6, "4pm":7, "5pm":8}

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
    get_hard_constraints_from_lines(lines)
    # print(lines)
    # print(domain)
    # for d in domain:
    #     print(d)

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
                    # TODO: create a class to save and compare time
                    start_time = day + hour #TODO: replce by the time class
                    finish_time = start_time + duration #TODO: replace by the time class
                    start_time = Time(day,hour)

                    # Remove the time if the task could not finish in one day
                    if finish_time > day + list(hours_of_day.values())[-1]:
                        continue
                    domain[variable_name].append((start_time,finish_time))
    return domain

def get_hard_constraints_from_lines(lines):
    get_binary_constraints_from_lines(lines)

def get_binary_constraints_from_lines(lines):
    for line in lines:
        match = search(r"^constraint, (?P<t1>\S*) (?P<type>\S*) (?P<t2>\S*)",line)
        if match is not None:
            t1 = match.group("t1")
            binary_constraint_type = match.group("type")
            t2 = match.group("t2")

            if binary_constraint_type == "before":
                pass
            elif binary_constraint_type == "after":
                pass
            elif binary_constraint_type == "same-day":
                pass
            elif binary_constraint_type == "starts-at":
                pass
            else :
                exit("Invalid binary constraint")

            print(t1,binary_constraint_type,t2)

def get_domain_constraints_from_lines(lines):
    pass

###### Custom Class : Time ######
class Time:
    def __init__(self, day, hour):
        self.time = (day, hour)
        #TODO: finishe the time add, and time compare


if __name__ == '__main__':
    main()         

