from sys import argv
from re import *

# read input file
file_name = argv[1]
# file_name = "input1.txt"

# Numeric representation in hours
days_in_week = {"mon":10, "tue":20, "wed":30, "thu":40, "fri":50}
hours_of_day = {"9am":0, "10am":1, "11am":2, "12pm":3, "1pm":4, "2pm":5, "3pm":6, "4pm":7, "5pm":8}

# process inputs
# for line in lines:
    ## Constrains
    # Unary constrains
    # Binary constrains
    # Hard domain constrains

    # Soft deadline constrains
    # Tasks : task, ⟨name⟩ ⟨duration⟩ - tuple
    # tasks = list()
    # task_regex = search("task, (?P<name>\S*) (?P<duration>\S*)",line)
    # if task_regex is not None:
    #     tasks.append((task_regex.group("name"),task_regex.group("duration")))

def main():
    lines = read_file_to_lines(file_name)
    domain = get_domain_from_lines(lines)
    print(lines)
    print(domain)
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
                    start_time = day + hour
                    finish_time = start_time + duration

                    # Remove the time if the task could not finish in one day
                    if finish_time > day + list(hours_of_day.values())[-1]:
                        continue
                    domain[variable_name].append((start_time,finish_time))
    return domain

if __name__ == '__main__':
    main()         

