import pypsa


def main(network: pypsa.Network):
    """Print the main results and plot the generation capacity per country"""

    n = network
    print(f"Total system cost: {n.objective / 1e9:.2f} bn EUR/a")
    print(f"CO2 price: {-n.global_constraints.mu['CO2Limit']:.2f} EUR/t")
    print("\nOptimal capacities [GW, GWh]:\n", n.statistics.optimal_capacity().div(1e3))
    print("\nLine capacities [GW]:\n", n.lines.s_nom_opt.div(1e3))
    print(
        "\nElectricity balance [TWh]:\n",
        n.statistics.energy_balance(bus_carrier="AC").sort_values().div(1e6),
    )

    fig, ax, _ = n.statistics.optimal_capacity.plot.bar(
        components="Generator", x="bus", y="value", color="carrier", stacked=True
    )
    ax.set(title="Generation capacity per country", ylabel="MW")
    return fig


if __name__ == "__main__":

    try:
        solved_network_path = str(snakemake.input)
        figure_path = str(snakemake.output)
    except NameError:
        import sys

        args = sys.argv[1:]
        solved_network_path = args[0]
        figure_path = args[1]

    solved_network = pypsa.Network(solved_network_path)
    fig = main(solved_network)
    fig.savefig(figure_path, bbox_inches="tight")
