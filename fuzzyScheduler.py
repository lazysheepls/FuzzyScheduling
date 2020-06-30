from sys import argv
from re import *
from inspect import *
# AIPython
from cspProblem import CSP, Constraint
from searchGeneric import Searcher, FrontierPQ
from cspConsistency import Search_with_AC_from_CSP

# read input file
file_name = argv[1]
# file_name = "input1.txt"

# Numeric representation in hours
#DEBUG: use this after finish
# days_in_week = {"mon":1, "tue":2, "wed":3, "thu":4, "fri":5}
# hours_of_day = {"9am":9, "10am":10, "11am":11, "12pm":12, "1pm":13, "2pm":14, "3pm":15, "4pm":16, "5pm":17}
#DEBUG: The following is just for testing, use above values when it's done
days_in_week = {'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5}
hours_of_day = {'9am': 1, '10am': 2, '11am':3, '12pm': 4, '1pm': 5, '2pm': 6, '3pm': 7, '4pm': 8, '5pm':9}
    

def main():
    # process input
    lines = read_file_to_lines(file_name)
    domains = get_domains_from_lines(lines)
    hard_constraints = get_hard_constraints_from_lines(lines)
    soft_constraints = get_soft_constraints(lines)

    # create SCP
    csp = Extended_CSP(domains,hard_constraints,soft_constraints)
    problem = Extended_Search_With_AC_from_CSP(csp)
    searcher = GreedySearcher(problem)
    result = searcher.search()

    # print("==> searcher <==")
    # print(result)
    # print("==> CSP: variables <==")
    # print(csp.variables)
    # print("==> CSP: domains <==")
    # print(csp.domains)
    # print("==> CSP: constraints <==")
    # print(csp.constraints)

    # print(lines)
    
    # print("Domains:")
    # for d in domain:
    #     print(d)
    #     for time in domain[d]:
    #         print("start-time:\t", time[0].day, "\t", time[0].hour, "\tfinish-time:\t", time[1].day, "\t", time[1].hour)

    print("Soft constraints:")
    for task in soft_constraints:
        print(task, soft_constraints[task][0], soft_constraints[task][1])

def read_file_to_lines(file_name):
    with open(file_name) as fp: 
        lines = fp.readlines()
        for line in lines:
            if line.startswith('#'):
                lines.remove(line) # Remove comment
    return lines

def get_domains_from_lines(lines):
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
                    domain[variable_name].append(Task(start_time,finish_time)) # domain includes task name and available time slots
    return domain

def get_hard_constraints_from_lines(lines):
    binary_constraints = get_binary_constraints_from_lines(lines)
    domain_constaints = get_domain_constraints_from_lines(lines)
    hard_domain_constrains = binary_constraints + domain_constaints  
    #DEBUG:
    print("Binary Constraints:")
    for bc in binary_constraints:
        print(bc.scope[0], bc.scope[1], getsource(bc.condition))
    print("Domain Constraints:")
    for dc in domain_constaints:
        print(dc.scope[0], getsource(dc.condition))
    
    return hard_domain_constrains

def get_binary_constraints_from_lines(lines):
    binary_constraints = list()
    for line in lines:
        match = search(r"^constraint, (?P<t1>\S*) (?P<type>\S*) (?P<t2>\S*)",line)
        if match is not None:
            t1 = match.group("t1")
            binary_constraint_type = match.group("type")
            t2 = match.group("t2")

            if binary_constraint_type == "before":
                scope = (t1, t2)
                condition = lambda t1, t2: t1.finish_time <= t2.start_time
            elif binary_constraint_type == "after":
                scope = (t1, t2)
                condition = lambda t1, t2: t1.start_time >= t2.finish_time
            elif binary_constraint_type == "same-day":
                scope = (t1, t2)
                condition = lambda t1, t2:t1.start_time.day == t2.start_time.day
            elif binary_constraint_type == "starts-at":
                scope = (t1, t2)
                condition = lambda t1, t2: t1.start_time.day == t2.start_time.day and t1.start_time.hour == t2.start_time.hour
            else :
                exit("Invalid binary constraint")
            
            binary_constraints.append(Constraint(scope,condition))
    return binary_constraints

def get_domain_constraints_from_lines(lines):
    domain_constraints = list()
    for line in lines:
        # domain, <t> <day>
        t_at_day_match = search(r"domain, (?P<t>\S*) (?P<day>[a-z]{3})(?![a-z])", line)

        # domain, <t> <hour>
        t_at_hour_match = search(r"domain, (?P<t>\S*) (?P<day>[0-9]+(am|pm))(?![a-z])", line)

        # domain, <t> starts-before/starts-after/ends-before/ends-after <day> <hour>
        t_range_day_hour_match = search(r"domain, (?P<t>\S*) (?P<type>\S*-\S*) (?P<day>[a-z]+) (?P<hour>[0-9]+(am|pm))(?!-|.*[0-9]+)", line)

        # domain, <t> starts-in/ends-in <day> <hour>-<day> <hour>
        t_day_hour_to_day_hour_match = search(r"domain, (?P<t>\S*) (?P<type>\S*-\S*) (?P<start_day>[a-z]+) (?P<start_hour>[0-9]+[a-z]+)-(?P<finish_day>[a-z]+) (?P<finish_hour>[0-9]+[a-z]+)", line)
        
        # domain, <t> starts-before/ends-before/starts-after/ends-after <hour>
        t_range_hour_match = search(r"domain, (?P<t>\S*) (?P<type>\S*-\S*) (?P<hour>[0-9]+[a-z]+)", line)

        if t_at_day_match is not None:
            constraint = get_at_day_constraint(t_at_day_match)
        elif t_at_hour_match is not None:
            constraint = get_at_hour_constraint(t_at_hour_match)
        elif t_range_day_hour_match is not None:
            constraint = get_range_day_hour_constraint(t_range_day_hour_match)
        elif t_day_hour_to_day_hour_match is not None:
            constraint = get_day_hour_to_day_hour_constraint(t_day_hour_to_day_hour_match)
        elif t_range_hour_match is not None:
            constraint = get_range_hour_domain_constraint(t_range_hour_match)
        else:
            continue

        domain_constraints.append(constraint)
    return domain_constraints

def get_at_day_constraint(match):
    t = match.group("t")
    scope = (t,)
    condition = lambda t: t.start_time.day == days_in_week[match.group("day")]
    return Constraint(scope,condition)

def get_at_hour_constraint(match):
    t = match.group("t")
    scope = (t,)
    condition = lambda t: t.start_time.hour == hours_of_day[match.group("hour")]
    return Constraint(scope,condition)

def get_range_day_hour_constraint(match):
    t = match.group("t")
    scope = (t,)
    constraint_type = match.group("type")
    required_day = match.group("day")
    required_hour = match.group("hour")
    if constraint_type == "starts-before":
        condition = lambda t: t.start_time.day <= required_day or (t.start_time.day == required_day and t.start_time.hour <= required_hour)
    elif constraint_type == "starts-after":
        condition = lambda t: t.start_time.day >= required_day or (t.start_time.day == required_day and t.start_time.hour >= required_hour)
    elif constraint_type == "ends-before":
        condition = lambda t: t.finish_time.day <= required_day or (t.finish_time.day == required_day and t.finish_time.hour <= required_hour)
    elif constraint_type == "ends-after":
        condition = lambda t: t.finish_time.day >= required_day or (t.finish_time.day == required_day and t.finish_time.hour >= required_hour)
    else:
        exit("Invalid hard domain constraint (starts/ends before/after)")
    return Constraint(scope,condition)

def get_day_hour_to_day_hour_constraint(match):
    t = match.group("t")
    scope = (t,)
    constraint_type = match.group("type")
    required_begin_day = match.group("start_day")
    required_begin_hour = match.group("start_hour")
    required_end_day = match.group("finish_day")
    required_end_hour = match.group("finish_hour")
    if constraint_type == "starts-in":
        condition = lambda t: t.start_time.day >= required_begin_day and t.start_time.hour >= required_begin_hour \
                    and t.start_time.day <= required_end_day and t.start_time.hour <= required_end_hour
    elif constraint_type == "ends-in":
        condition = lambda t: t.finish_time.day >= required_begin_day and t.finish_time.hour >= required_begin_hour \
                    and t.finish_time.day <= required_end_day and t.finish_time.hour <= required_end_hour
    else:
        exit("Invalid hard domain constraint (from day-hour to day-hour)")
    return Constraint(scope,condition)

def get_range_hour_domain_constraint(match):
    t = match.group("t")
    scope = (t,)
    constraint_type = match.group("type")
    required_hour = match.group("hour")
    if constraint_type == "starts-before":
        condition = lambda t: t.start_time.hour <= required_hour
    elif constraint_type == "ends-before":
        condition = lambda t: t.finish_time.hour <= required_hour
    elif constraint_type == "starts-after":
        condition = lambda t: t.start_time.hour >= required_hour
    elif constraint_type == "ends-after":
        condition = lambda t: t.finish_time.hour >= required_hour
    else:
        exit("Invalid hard domain constraint (starts/ends before/after hour)")
    return Constraint(scope,condition)

def get_soft_constraints(lines):
    soft_constraints = dict()
    for line in lines:
        match = search(r"domain, (?P<t>\S*) ends-by (?P<day>[a-z]+) (?P<hour>[0-9]+(am|pm)) (?P<cost>[0-9]+)", line)
        if match is not None:
            t = match.group("t")
            day = days_in_week[match.group("day")]
            hour = hours_of_day[match.group("hour")]
            time = Time(day,hour)
            cost = int(match.group("cost"))
            soft_constraints[t] = (time, cost)
    return soft_constraints

###### Extended Class : Extended_CSP ######
class Extended_CSP(CSP):
    def __init__(self, domains, constraints, soft_constraints):
        super().__init__(domains, constraints)
        self.soft_constraints = soft_constraints

###### Extended Class : Extended_AC_
class Extended_Search_With_AC_from_CSP(Search_with_AC_from_CSP):
    def __init__(self, csp):
        super().__init__(csp)
        self.soft_constraints = csp.soft_constraints
    
    def heuristic(self, n):
        #DEBUG:
        print("==> Node N <==")
        print(n)


###### Extended Class : GreedySearcher ######
# Modified from AstarSearcher from searchGeneric.py
class GreedySearcher(Searcher):
    def __init__(self, problem):
        super().__init__(problem)

    def initialize_frontier(self):
        self.frontier = FrontierPQ()

    def empty_frontier(self):
        return self.frontier.empty()

    def add_to_frontier(self,path):
        """add path to the frontier with the appropriate cost"""
        value = self.problem.heuristic(path.end())
        self.frontier.add(path, value)

###### Custom Class : Task ######
class Task: 
    def __init__(self, start_time, finish_time):
        self.start_time = start_time
        self.finish_time = finish_time
    
    def __repr__(self):
        return "(" + str(self.start_time) + ", " + str(self.finish_time) + ")"

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
    
    def __repr__(self):
        return str(self.day) + str(self.hour)
    
    def __gt__(self, other):
        return self.day > other.day or (self.day == other.day and self.hour > other.hour)
    
    def __ge__(self, other):
        return self.day >= other.day or (self.day == other.day and self.hour >= other.hour)
    
    def __lt__(self, other):
        return self.day < other.day or (self.day == other.day and self.hour < other.hour)
    
    def __le__(self, other):
        return self.day <= other.day or (self.day == other.day and self.hour <= other.hour)

if __name__ == '__main__':
    main()         

