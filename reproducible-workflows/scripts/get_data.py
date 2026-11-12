"""Get data for making the model

1. Get technology costs

We maintain a database (https://github.com/PyPSA/technology-data) which collects assumptions and projections
for energy system technologies (such as costs, efficiencies, lifetimes, etc.) for given years, which we can
load into a `pandas.DataFrame`. This requires some pre-processing to load (e.g. converting units, setting defaults,
re-arranging dimensions):

2. Get time series

"""

import pandas as pd
from os.path import join

for year in [2030]:
    url = f"https://raw.githubusercontent.com/PyPSA/technology-data/master/outputs/costs_{year}.csv"
    output_path = join("data", f"costs_{year}.csv")
    costs = pd.read_csv(url, index_col=[0, 1])
    costs.to_csv(output_path, index=True)

url = (
    "https://tubcloud.tu-berlin.de/s/pKttFadrbTKSJKF/download/time-series-lecture-2.csv"
)
ts = pd.read_csv(url, index_col=0, parse_dates=True)
ts.to_csv(join("data", "time-series-lecture-2.csv"), index=True)
