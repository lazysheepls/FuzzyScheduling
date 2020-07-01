import sys
from cspProblem import CSP, Constraint
from cspConsistency import Search_with_AC_from_CSP
from searchGeneric import AStarSearcher


###############################################################################3
# Change class display in display.py:
# change 'max_display_level = 1 to 'max_display_level = 0'
# this is to disable the display function to print the expanded path
#################################################################################
# Change class Arc in searchProblem.py:
# change def __init__(self, from_node, to_node, cost=1, action=None):
# to  def __init__(self, from_node, to_node, cost=0, action=None):
# as in this task arrangement problem, no arc cost from one node to next node
#################################################################################


#######################################################
############ extend CSP class #########################
# add self.soft_constraints to store soft constraints which is a dict with format {'t1': ['end-by    ']}
# add soft_cost {t1:}
class New_CSP(CSP):
    def __init__(self,domains,constraints,soft_constraints,soft_cost):
        super().__init__(domains,constraints)
        self.soft_constraints = soft_constraints
        self.soft_cost = soft_cost

class Search_with_AC_from_Cost_CSP(Search_with_AC_from_CSP):
    def __init__(self,csp):
        super().__init__(csp)
        self.cost = []
        self.soft_cons = csp.soft_constraints
        self.soft_cost = soft_cost

    def heuristic(self,node):
        #print(node)
        cost = 0
        cost_list = []
        for task in node:
            if task in self.soft_cons:
                temp = []
                expect_time = self.soft_cons[task]
                for value in node[task]:
                    actual_time = value[1]
                    if actual_time > expect_time:
                        delay = (actual_time//10- expect_time//10)*24 + ((actual_time%10) - (expect_time%10))
                        temp.append(self.soft_cost[task] * delay)
                    else:
                        temp.append(0)

                if len(temp)!=0:
                    cost_list.append(min(temp))

        cost = sum(cost_list)

        return cost


####################################################
######### binary constraint ########################
####################################################
def binary_before(t1,t2):
    return t1[1]<=t2[0]

def binary_after(t1,t2):
    return t2[1]<=t1[0]

def binary_same_day(t1,t2):
    return t1[0]//10 == t2[0]//10

def binary_starts_at(t1,t2):
    return t1[0] == t2[1]




####################################################
######### hard constraint ##########################
####################################################

def hard_day(day):
    hardday = lambda x: x[0]//10 ==day
    '''
    def hardday(val):
        return val[0]//10 ==day
    '''
    return hardday

def hard_time(time):
    def hardtime(val):
        return val[0] % 10 == time
    return hardtime

def hard_starts_before_daytime(day,time):
    def startsbefore(val):
        giventime = day*10 + time
        return val[0] <= giventime
    return startsbefore

def hard_starts_before_time(time):
    def startsbefore(val):
        return val[0]%10 <= time
    return startsbefore

def hard_starts_after_daytime(day,time):
    def startsafter(val):
        giventime = day*10 + time
        return val[0] >= giventime
    return startsafter

def hard_starts_after_time(time):
    def startsafter(val):
        return val[0]%10 >= time
    return startsafter

def hard_ends_before_daytime(day,time):
    def endsbefore(val):
        giventime = day*10 + time
        return val[1] <= giventime
    return endsbefore

def hard_ends_before_time(time):
    def endsbefore(val):
        return val[1]%10 <= time
    return endsbefore

def hard_ends_after_daytime(day,time):
    def endsafter(val):
        giventime = day*10 + time
        return val[1] >= giventime
    return endsafter

def hard_ends_after_time(time):
    def endsafter(val):
        return val[1]%10 >= time
    return endsafter

def hard_startin_range(day1,time1,day2,time2):
    def start_range(val):
        giventime1 = day1*10 + time1
        giventime2 = day2*10 + time2
        return val[0]>=giventime1 and val[0]<=giventime2
    return start_range

def hard_endin_range(day1,time1,day2,time2):
    def end_range(val):
        giventime1 = day1*10 + time1
        giventime2 = day2*10 + time2
        return val[1]>=giventime1 and val[1]<=giventime2
    return end_range



#filename = sys.argv[1]
filename = 'input1.txt'
week_to_num = {'mon': 1, 'tue': 2, 'wed': 3, 'thu': 4, 'fri': 5}
time_to_num = {'9am': 1, '10am': 2, '11am':3, '12pm': 4, '1pm': 5, '2pm': 6, '3pm': 7, '4pm': 8, '5pm':9}
domain =set()
for i in range(1, 6):
    for j in range(1, 10):
        domain.add(i * 10 + j)

task_duration = {}
task_domain = {}
hard_constraint = []
soft_constraint = {}
soft_cost = {}
task_list = []

file =  open(filename,'r', encoding = 'utf-8')
for line in file:
    #Remove '\n'
    if (line=='\n') or (line[0]=='#'):
        continue
    line = line.strip()
    line = line.replace('\n','')
    line = line.replace(',', '')
    line = line.replace('-',' ')
    line = line.split(' ')
    ### get task and duration
    if line[0]=='task':
        #print(line)
        task_duration[line[1]] = int(line[2])
        di = set()
        duration = int(line[2])
        for item in domain:
            if item % 10 + duration <= 9:
                di.add(item)
        task_domain[line[1]] = set((x, x + duration) for x in di)

    # get binary constraint
    elif line[0]=='constraint':
        #print(line)
        t1 = line[1]
        t2 = line[-1]
        if 'before' in line:
            hard_constraint.append(Constraint((t1,t2),binary_before))
        if 'after' in line:
            hard_constraint.append(Constraint((t1,t2),binary_after))
        if 'same' in line:
            hard_constraint.append(Constraint((t1,t2),binary_same_day))
        if 'starts' in line:
            hard_constraint.append(Constraint((t1,t2),binary_starts_at))
    # get soft constraint
    elif (line[0]=='domain') and (line[-1] not in week_to_num) and (line[-1] not in time_to_num):
        #print(line)
        task = line[1]
        day = week_to_num[line[4]]
        time = time_to_num[line[5]]
        soft_cost[task]=int(line[-1])
        soft_constraint[task]=day*10+time
    # get hard constraint
    else:
        task = line[1]
        #print(line)
        # domain, t, day
        if line[2] in week_to_num:
            day = week_to_num[line[2]]
            hard_constraint.append(Constraint((task,),hard_day(day)))
        # domain, t time
        elif line[2] in time_to_num:
            time = time_to_num[line[2]]
            hard_constraint.append(Constraint((task,),hard_time(time)))

        elif ('starts' in line) and ('before' in line):
            #domain t starts before day time
            if len(line)==6:
                day = week_to_num[line[-2]]
                time = time_to_num[line[-1]]
                hard_constraint.append(Constraint((task,), hard_starts_before_daytime(day,time)))
            #domain t starts before time
            if len(line)==5:
                time = time_to_num[line[-1]]
                hard_constraint.append(Constraint((task,), hard_starts_before_time(time)))

        elif ('starts' in line) and ('after' in line):
            # domain t starts after day time
            if len(line) == 6:
                day = week_to_num[line[-2]]
                time = time_to_num[line[-1]]
                hard_constraint.append(Constraint((task,), hard_starts_after_daytime(day, time)))
            # domain t starts after time
            if len(line) == 5:
                time = time_to_num[line[-1]]
                hard_constraint.append(Constraint((task,), hard_starts_after_time(time)))

        elif ('ends' in line) and ('before' in line):
            # domain t ends before day time
            if len(line) == 6:
                day = week_to_num[line[-2]]
                time = time_to_num[line[-1]]
                hard_constraint.append(Constraint((task,), hard_ends_before_daytime(day, time)))
            # domain t ends before time
            if len(line) == 5:
                time = time_to_num[line[-1]]
                hard_constraint.append(Constraint((task,), hard_ends_before_time(time)))
        elif ('ends' in line) and ('after' in line):
            # domain t ends after day time
            if len(line) == 6:
                day = week_to_num[line[-2]]
                time = time_to_num[line[-1]]
                hard_constraint.append(Constraint((task,), hard_ends_after_daytime(day, time)))
            # domain t ends after time
            if len(line) == 5:
                time = time_to_num[line[-1]]
                hard_constraint.append(Constraint((task,), hard_ends_after_time(time)))
        #day-time range
        else:
            #domain t starts in day time day time
            if 'starts' in line:
                day1 = week_to_num[line[4]]
                time1 = time_to_num[line[5]]
                day2 = week_to_num[line[6]]
                time2 = time_to_num[line[7]]
                hard_constraint.append(Constraint((task,), hard_startin_range(day1,time1,day2,time2)))
            elif 'ends' in line:
                day1 = week_to_num[line[4]]
                time1 = time_to_num[line[5]]
                day2 = week_to_num[line[6]]
                time2 = time_to_num[line[7]]
                hard_constraint.append(Constraint((task,), hard_endin_range(day1, time1, day2, time2)))



#print(soft_constraint)
#print(hard_constraint)
#print(task_domain)

csp = New_CSP(task_domain,hard_constraint,soft_constraint,soft_cost)
problem = Search_with_AC_from_Cost_CSP(csp)
solution = AStarSearcher(problem).search()


if solution:
    solution = solution.end()
    for task in solution:
        for item in week_to_num:
            if week_to_num[item] ==list(solution[task])[0][0]//10:
                day = item
        for item in time_to_num:
            if time_to_num[item] == list(solution[task])[0][0]%10:
                time = item
        print(f'{task}:{day} {time}')
    print(f'cost:{problem.heuristic(solution)}')
else:
    print('No solution')



