import logging

import pypsa

logging.basicConfig(level=logging.WARNING)
pypsa.options.params.optimize.log_to_console = False
pypsa.options.api.legacy_string_dtype = False
pypsa.options.params.optimize.include_objective_constant = False


def main(network: pypsa.Network) -> pypsa.Network:
    """Solve the network"""
    network.optimize(io_api="direct")
    return network


if __name__ == "__main__":

    try:
        network_path = str(snakemake.input)
        solved_network_path = str(snakemake.output)
    except NameError:
        import sys

        args = sys.argv[1:]
        network_path = args[0]
        solved_network_path = args[1]

    network = pypsa.Network(network_path)
    solved_network = main(network)
    solved_network.export_to_netcdf(solved_network_path)
