"""Get data for making the model

1. Get technology costs

We maintain a database (https://github.com/PyPSA/technology-data) which collects assumptions and projections
for energy system technologies (such as costs, efficiencies, lifetimes, etc.) for given years, which we can
load into a `pandas.DataFrame`.

2. Get time series and capacity limits

Hourly demand and capacity factors, and the wind and solar capacity limits, of TYNDP 2026
National Trends+ 2035 for Germany. We copy them from the data
of the session "Hands on with PyPSA components" (`../02-hands-on-pypsa/data`).

"""

import os
from os.path import join

import pandas as pd

os.makedirs("data", exist_ok=True)

for year in [2035]:
    url = f"https://raw.githubusercontent.com/PyPSA/technology-data/v0.15.0/outputs/costs_{year}.csv"
    output_path = join("data", f"costs_{year}.csv")
    costs = pd.read_csv(url, index_col=[0, 1])
    costs.to_csv(output_path, index=True)

data_dir = join("..", "02-hands-on-pypsa", "data")

ts = pd.read_csv(
    join(data_dir, "tyndp2026-nt2035-hourly-demand-wind-solar.csv"),
    index_col=0,
    parse_dates=True,
)
ts.to_csv(join("data", "tyndp2026-nt2035-hourly-demand-wind-solar.csv"), index=True)

p_nom_max = pd.read_csv(join(data_dir, "tyndp2026-nt2035-wind-solar-capacity.csv"), index_col=0)
p_nom_max.to_csv(join("data", "tyndp2026-nt2035-wind-solar-capacity.csv"), index=True)
