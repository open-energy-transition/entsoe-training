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

## 1 · Create the environment

Open a terminal in the folder of this repository and run the block for your system. It creates a virtual environment `.venv` and installs the pinned packages of `requirements.txt`. If Python is missing, install it from [python.org](https://www.python.org/downloads/); on Windows, keep the **py launcher** option ticked.

**Windows, Command Prompt (`cmd`)**

```bat
py -3 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**Windows, PowerShell**

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**macOS and Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Check the version with `python --version` once the environment is active: it must be 3.11, 3.12 or 3.13. If not, recreate `.venv` with a supported version (on Windows, for example, `py -3.12 -m venv .venv`).


## 2 · Running the workflow

Run all commands from this folder:

```sh
python PyPSA-cem.py                # 1) To run monolithic script
bash python-commands-example.sh     # 2) To run modular scripts, one by one
make                                # 3) Run workflow using Makefile
snakemake --cores 1                 # 4) Run workflow using Snakefile
```

