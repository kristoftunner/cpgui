import numpy as np
import os
from matplotlib import pyplot as plt

data = np.linspace(0,10,10)
data2 = np.linspace(10,0,10)
fig = plt.figure()
plt.subplot(2,2,1)
plt.plot(data)
plt.subplot(2,2,2)
plt.plot(data)
plt.subplot(2,2,3)
plt.plot(data)

ax = fig.axes[0]
ax2 = fig.axes[2]
ax2.plot(data2)
ax.plot(data2)
plt.show()