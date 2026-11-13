# ENTSO-E training · Workflows Demonstration Examples

Material for the session "Reproducible and automatable workflows" of the ENTSO-E training by [Open Energy Transition](https://openenergytransition.org), 17 November 2026.

The contents of this folder are derived from Fabian Neumann's excellent
[Data Science for Energy System Modelling](https://fneum.github.io/data-science-for-esm/)
course materials, and available under the permissive MIT License.

Specifically, the contents of the `scripts` folder contain modularised versions of the
[PyPSA Capacity Expansion Modelling](https://fneum.github.io/data-science-for-esm/dsesm/workshop-pypsa-cem/)
lecture/notebook and have been reworked to demonstrate how a monolithic script can be broken up into components
as a precurser to using a workflow automation tool such as snakemake.

`PyPSA-cem.py` is the model of the [Hands on with PyPSA components](../notebooks/hands-on-with-pypsa/hands-on-pypsa-components.ipynb)
notebook (Germany, Austria and Switzerland, TYNDP 2026 data) as one monolithic script.

## Installation

Install the packages, including snakemake, into a fresh environment:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the workflow

Run all commands from this folder:

```sh
python PyPSA-cem.py                # 1) To run monolithic script
bash python-commands-example.sh     # 2) To run modular scripts, one by one
make                                # 3) Run workflow using Makefile
snakemake --cores 1                 # 4) Run workflow using Snakefile
```

