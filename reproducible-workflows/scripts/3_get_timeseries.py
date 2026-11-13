"""Loading time series data

We need time series for wind, solar and load. They are hourly time series of
TYNDP 2026 National Trends+ 2035 (weather scenario WS032) for Germany, Austria
and Switzerland, already in MW, the base unit of PyPSA.


"""

import os
import pandas as pd


def main(input_data: pd.DataFrame) -> pd.DataFrame:

    ts = input_data

    # Average over blocks of 6 hours, to save some time.
    # Careful: 4_build_model.py has its own RESOLUTION. If you change one and
    # not the other, the snapshot weightings no longer match the time series
    # and the model is silently wrong. A single config value avoids this.

    resolution = 6
    ts = ts.resample(f"{resolution}h").mean()

    return ts


if __name__ == "__main__":

    input_path = os.path.join("data", "tyndp2026-nt2035-hourly-demand-wind-solar.csv")
    output_path = os.path.join("data", "timeseries.csv")

    # When this script is used with the ``script:`` call in snakemake,
    # you can directly access the input and output paths.
    # input_path = str(snakemake.input)
    # output_path = str(snakemake.output)

    input_data = pd.read_csv(input_path, index_col=0, parse_dates=True)

    output_data = main(input_data)
    output_data.to_csv(output_path)
