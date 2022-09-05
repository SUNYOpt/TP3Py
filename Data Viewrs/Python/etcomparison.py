import matplotlib.pyplot as plt
import json
from collections import namedtuple

#f = open('ETdata-.json')
#Calibdata = json.loads(f)
"""
with open('ETdata-.json') as f:
    data = json.load(f.readlines())
    print(data[0]['text'])

with open('ETdata-.json') as f:
    contents = f.readlines()
    print(contents)

f.close()

print(contents)

all_actions = ['fame','gright','gleft']


sequence_array = []
with open('ETdata-.json', 'r') as f:
    for line in f.readlines():
        for action in all_actions:
            if action in line:
                sequence_array.append(action)

for action in sequence_array:
    print(action)

with open('TSdata-test4-19-37.txt') as f:
    data = json.load(json.load(f))
    print(data[0]['text'])

with open('Gazedata-test4-19-37.txt') as f:
    data = json.load(json.load(f))
    print(data[0]['text'])

print(contents)
"""
TimeArray = []
Gaze2DxArray = []
Gaze2DyArray = []

with open('Gazedata-test1-12-18.txt') as f:
    lines = (f.readlines())

for streamString in lines:
    #print('st:', streamString[0:len(streamString)])

    GazeD = json.loads(streamString[0:len(streamString)], object_hook=
    lambda d: namedtuple('X', d.keys())
    (*d.values()))

    TimeArray.append(GazeD.tgz)
    Gaze2DxArray.append(GazeD.gaze2d[0])
    Gaze2DyArray.append(GazeD.gaze2d[1])

#print (Gaze2DxArray)
plt.rcParams.update({'font.size': 12, 'lines.linewidth':2})
fig = plt.figure()
ax = fig.add_axes((0.2, 0.2, 0.4, 0.4))
ax.plot(TimeArray, Gaze2DxArray, 'b')
ax.plot(TimeArray, Gaze2DyArray, 'r')
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_linewidth(2)
ax.spines["left"].set_linewidth(2)
ax.xaxis.set_tick_params(width=2)
ax.yaxis.set_tick_params(width=2)

plt.show()