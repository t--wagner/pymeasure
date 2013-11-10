# Importing modules
import numpy as np
import pymeasure.liveplot as lplt
from threading import Thread
import time
import Tkinter as Tk


#Creating Graphs
graph = lplt.LiveGraphTk()
axes = []

graph['sin'] = lplt.Dataplot1d(length=100, continuously=True)
graph['sin_2d'] = lplt.Dataplot2d(length=201)
graph['cos'] = lplt.Dataplot1d(length=100, continuously=True)
graph['cos_2d'] = lplt.Dataplot2d(length=201)
graph.build_grid(2)
graph['sin'].xlabel = 'test'
graph.run(delay=25)

# Main Programm
def main():
    for step1 in xrange(0, 101):

        for step2 in xrange(0, 201):
            sin_val = np.sin(2 * np.pi / 100 * (step1 + step2))
            graph['sin'].add_data([step2], [sin_val])
            graph['sin_2d'].add_data([sin_val])

            cos_val = np.cos(2 * np.pi / 100 * (step1 + step2))
            graph['cos'].add_data([step2], [cos_val])
            graph['cos_2d'].add_data([cos_val])

            time.sleep(50e-3)
        
        graph['sin'].clear()
        graph['cos'].clear()


# Main Programm muss als thread gestartet werden)
t = Thread(target=main)
t.start()