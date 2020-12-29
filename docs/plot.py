import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

data = pd.read_csv(os.path.join(os.path.dirname(__file__), "bm.csv")) 
data = data.drop(columns=['Time in Total'])
data = data.set_index(["ContourExtractor Threads for Avg", "ContourExtractor Threads for comp", "LayerFactory Threads", "Video Buffer Length"])

labels = [f"{row[0]}, {row[1]}, {row[2]}, {row[3]}" for row in data.values]
data[:-12].plot.barh(stacked=True, label=labels)

#data.groupby(["ContourExtractor Threads for Avg"]).plot(kind="barh", stacked=True,label =labels)
plt.xlabel("time in seconds")
plt.show()