from sys import argv
from re import *

# read input file
fileName = argv[1]
lines = list()

with open(fileName) as fp: 
    # Read in raw file
    lines = fp.readlines()

# Remove comment
for line in lines:
    if line.startswith('#'):
        lines.remove(line)

# process inputs
tasks = dict()

for line in lines:
    # Binary constrains
    # Hard domain constrains
    # Soft deadline constrains
    # Tasks : task, ⟨name⟩ ⟨duration⟩
    tasksRegex = search("task, (?P<name>\S*) (?P<duration>\S*)",line)
    if tasksRegex is not None:
        tasks[tasksRegex.group("name")] = tasksRegex.group("duration")


print(tasks)
# # TEST
count = 0
for line in lines: 
    count += 1
    print("Line{}: {}".format(count, line.strip())) 