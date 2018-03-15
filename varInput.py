import numpy as np

time = np.linspace(1,13100,2360)


import matplotlib.pyplot as plt

import random

def decision(time, sinscale):
    import random
    b = np.sin(time / sinscale)
    return random.random() < np.sin(time/sinscale)

a = []
sinscale=500
for i in range(0,len(time)):
    a.append(decision(time[i],sinscale))

plt.scatter(time, np.asarray(a))
plt.show()



dict = {"a":1,"b":1,"c":0,"d":1}

    for key in list(hand.keys()):  ## creates a list of all keys
        ...
        if hand[key] == 0:
            ...
        del hand[key]
