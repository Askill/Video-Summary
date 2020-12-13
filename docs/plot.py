import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
[
    {"threads": "32, 16",  "Contour Extractor": 106.0405707359314,  "Layer Factory": 0.5175004005432129, "Layer Manager": 1.4864997863769531, "Exporter": 34.591999769210815},
    {"threads": "1, 1",    "Contour Extractor": 463.66750025749207, "Layer Factory": 0.5290005207061768, "Layer Manager": 1.551999807357788,  "Exporter": 34.5339994430542},
    {"threads": "1, 4",    "Contour Extractor": 193.51898574829102, "Layer Factory": 0.5249984264373779, "Layer Manager": 1.5125021934509277, "Exporter": 35.06749963760376},
    {"threads": "4, 4",    "Contour Extractor": 186.46951842308044, "Layer Factory": 0.5295009613037109, "Layer Manager": 1.545145034790039,  "Exporter": 34.260000705718994},
    {"threads": "4, 8",    "Contour Extractor": 126.90402793884277, "Layer Factory": 0.5275006294250488, "Layer Manager": 1.536078929901123,  "Exporter": 34.61099886894226},
    {"threads": "16, 16",  "Contour Extractor": 109.17592716217041, "Layer Factory": 0.4179983139038086, "Layer Manager": 1.5620002746582031, "Exporter": 33.80550146102905},
    
]
x = {
    "threads":["1, 1","1, 4","4, 4","4, 8","16, 16", "32, 16"],
    "Contour Extraction":[ 463.66750025749207, 193.51898574829102,186.46951842308044,126.90402793884277,109.17592716217041,106.0405707359314],
}

df = pd.DataFrame.from_dict(x)
ax = df.plot.bar(x="threads", title="Benötigte Zeit für Konturenextraktion mit unterschiedlicher Anzahlen von Threads", figsize=(10,4))
ax.set_xlabel("Threads für Durchschnittsbildung | Threads für Differenzberechnung")
ax.set_ylabel("Zeit in Sekunden")
plt.show()
