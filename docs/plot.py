import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

data = pd.read_csv(os.path.join(os.path.dirname(__file__), "bm.csv")) 
data = data.drop(columns=['total'])
data = data.set_index(["ce_average_threads", "ce_comp_threads", "lf_threads", "videoBufferLength"])

labels = [f"{row[0]}, {row[1]}, {row[2]}, {row[3]}" for row in data.values]
data.plot.barh(stacked=True, label=labels)
plt.show()
print(data)