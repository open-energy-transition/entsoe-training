import pypsa

pypsa.options.api.legacy_string_dtype = False


def main(network: pypsa.Network):
    """Print the main results and plot the generation capacity"""

    n = network
    co2_per_mwh = n.generators.carrier.map(n.carriers.co2_emissions).div(n.generators.efficiency)
    co2 = n.snapshot_weightings.generators @ (n.generators_t.p * co2_per_mwh).sum(axis=1)

    print(f"Total system cost: {n.objective / 1e9:.2f} bn EUR/a")
    print(f"CO2 emissions: {co2 / 1e6:.1f} Mt/a")
    print(f"CO2 price: {-n.global_constraints.mu['CO2Limit']:.2f} EUR/t")
    print("\nOptimal capacities [GW, GWh]:\n", n.statistics.optimal_capacity().div(1e3))
    print(
        "\nElectricity balance [TWh]:\n",
        n.statistics.energy_balance(bus_carrier="AC").sort_values().div(1e6),
    )

    fig, ax, _ = n.statistics.optimal_capacity.plot.bar(
        components="Generator", x="carrier", y="value", color="carrier"
    )
    ax.set(title="Generation capacity, Germany", ylabel="MW")
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
