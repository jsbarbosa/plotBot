#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation


# In[3]:


def plotPosition(x1,
                 y1,
                 x0=0,
                 y0=0,
                 source: bool = False,
                 ax=None):
    
    if ax is None:
        fig, ax = plt.subplots()
    
    ax.plot([x0, x1], [y0, y1], c='k')
    if source:
        ax.scatter([x0], [y0], c='g', s=200)
    else:
        ax.scatter([x0], [y0], c='r')
    return ax


# In[ ]:


class plotBot(object):
    def __init__(self,
                 inner_length: float = 41,
                 outer_length: float = 44,
                 distance_between_origins: float = 24,
                 x_origin: float = 22,
                 y_origin: float = -26):

        self.INNER_LENGTH = inner_length
        self.OUTER_LENGTH = outer_length
        self.DISTANCE_BETWEEN_ORIGINS = distance_between_origins
        self.X_ORIGIN = x_origin #: from origin to first motor
        self.Y_ORIGIN = y_origin #: from origin to first motor

        self.current_x = 0
        self.current_y = 0
    
    def set_position(self, 
                     x: float,
                     y: float):
        self.current_x = x
        self.current_y = y
        
    def get_left_angle(self):
        x = self.current_x - self.X_ORIGIN
        y = self.current_y - self.Y_ORIGIN

        r2 = x ** 2 + y ** 2
        r = r2 ** 0.5
        theta2 = np.arccos((r2 - self.INNER_LENGTH ** 2 - self.OUTER_LENGTH ** 2)                            / (2 * self.INNER_LENGTH * self.OUTER_LENGTH))

        return np.arcsin(self.OUTER_LENGTH * np.sin(theta2) / r) + np.arctan2(y, x)
    
    def get_left_positions(self):
        theta = self.get_left_angle()
        
        x_motor = self.X_ORIGIN
        y_motor = self.Y_ORIGIN
        
        x = self.INNER_LENGTH * np.cos(theta) + x_motor
        y = self.INNER_LENGTH * np.sin(theta) + y_motor
        
        array = [
            (x_motor, y_motor),
            (x, y),
            (self.current_x, self.current_y)
        ]
        
        return np.array(array)
    
    def get_right_angle(self):
        x = self.current_x - (self.X_ORIGIN + self.DISTANCE_BETWEEN_ORIGINS)
        y = self.current_y - self.Y_ORIGIN

        r2 = x ** 2 + y ** 2
        r = r2 ** 0.5
        theta2 = np.arccos((r2 - self.INNER_LENGTH ** 2 - self.OUTER_LENGTH ** 2)                            / (2 * self.INNER_LENGTH * self.OUTER_LENGTH))

        return np.arctan2(y, x) - np.arcsin(self.OUTER_LENGTH * np.sin(theta2) / r)
    
    def get_right_positions(self):
        theta = self.get_right_angle()
        
        x_motor = self.X_ORIGIN + self.DISTANCE_BETWEEN_ORIGINS
        y_motor = self.Y_ORIGIN
        
        x = self.INNER_LENGTH * np.cos(theta) + x_motor
        y = self.INNER_LENGTH * np.sin(theta) + y_motor
        
        array = [
            (x_motor, y_motor),
            (x, y),
            (self.current_x, self.current_y)
        ]
        
        return np.array(array)


# In[ ]:


pb = plotBot()


# In[ ]:


width = 30
x = np.linspace(pb.X_ORIGIN + pb.DISTANCE_BETWEEN_ORIGINS / 2 - width, 
                pb.X_ORIGIN + pb.DISTANCE_BETWEEN_ORIGINS / 2 + width,
                15)
y = np.linspace(48, 2, 10)

xx, yy = np.meshgrid(x, y)

n_j, n_i = xx.shape


# In[ ]:


def animate(ii):
    global xx, yy, left_arm, elapsed_plots
    i = ii // n_i
    j = ii % n_i
    
    if i % 2:
        j = -(j + 1)
        elapsed_plots[i].set_data(xx[i, j:], yy[i, j:])
    
    else:
        elapsed_plots[i].set_data(xx[i, :j+1], yy[i, :j+1])
    
    x = xx[i, j]
    y = yy[i, j]
    
    pb.set_position(x, y)
    
    x1, y1 = pb.get_left_positions().T
    x2, y2 = pb.get_right_positions().T
    
    left_arm.set_data(x1, y1)
    right_arm.set_data(x2, y2)
    
    return ax,


# In[ ]:


fig, ax = plt.subplots()

left_arm = ax.plot([], [], '-o', c='b')[0]
right_arm = ax.plot([], [], '-o', c='b')[0]

elapsed_plots = [ax.plot([], [], c='k')[0] for i in range(n_i)]

rect = patches.Rectangle((0, 0),
                         71,
                         50,
                         linewidth=2,
                         edgecolor='r',
                         facecolor='none')

# Add the patch to the Axes
ax.add_patch(rect)

x_extra = 50

ax.set_xlim(-x_extra, 71 + x_extra)
ax.set_ylim(-40, 60)
ax.set_aspect('equal')
ax.set_axis_off()
# ax.grid()

fig.tight_layout()

ani = FuncAnimation(fig, animate, frames=n_i*n_j, interval=70)
ani.save('animation.gif', writer='imagemagick')
plt.show()

