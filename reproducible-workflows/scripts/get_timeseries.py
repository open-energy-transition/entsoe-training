"""Loading time series data

We are also going to need some time series for wind, solar
and load. For now, we are going to recycle the time series we
used at the beginning of the course. They are given for Germany
in the year 2015.


"""

import os
import pandas as pd


def main(input_data: pd.DataFrame) -> pd.DataFrame:

    ts = input_data

    # Convert the load time series from GW to MW, the base unit of PyPSA:
    ts.load *= 1e3

    # Sample only every other hour, to save some time:

    resolution = 4
    ts = ts.resample(f"{resolution}h").first()

    return ts


if __name__ == "__main__":

    input_path = os.path.join("data", "time-series-lecture-2.csv")
    output_path = os.path.join("data", "timeseries.csv")

    # When this script is used with the ``script:`` call in snakemake,
    # you can directly access the input and output paths.
    # input_path = str(snakemake.input)
    # output_path = str(snakemake.output)

    input_data = pd.read_csv(input_path, index_col=0, parse_dates=True)

    output_data = main(input_data)
    output_data.to_csv(output_path)
