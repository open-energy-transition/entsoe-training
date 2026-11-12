import os
import pypsa
import pandas as pd

import matplotlib.pyplot as plt

import plotly.io as pio
import plotly.offline as py

pd.options.plotting.backend = "plotly"


def main(network: pypsa.Network):

    fig, _, _ = network.statistics.energy_balance.plot.bar()
    return fig


if __name__ == "__main__":

    import sys

    args = sys.argv[1:]

    solved_network_path = args[0]

    # solved_network_path = os.path.join("results", "cem_solved.nc")
    solved_network = pypsa.Network(solved_network_path)

    figure_path = args[1]
    # figure_path = os.path.join("results", "figure.png")
    fig = main(solved_network)
    fig.savefig(figure_path)
