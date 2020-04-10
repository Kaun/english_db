import json
from data import teachers, goals

# with open('data.py', "r") as f:
#     data = f.read()
#
# with open('mydata.json', "w") as ff:
#     json.dump(data, ff)

with open("teachers.json", "w") as f:
    json.dump(teachers, f)

with open("goals.json", "w") as ff:
    json.dump(goals, ff)
