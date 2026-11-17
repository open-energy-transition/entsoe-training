# ENTSO-E training · Hands on with PyPSA components

Material for the session "Hands on with PyPSA components" of the ENTSO-E training by [Open Energy Transition](https://openenergytransition.org), 17 November 2026.

Goal: open `hands-on-pypsa-components.ipynb` and run it.

## Requirements

The requirements of the [Setup](../README.md#setup) apply. The notebook downloads the technology cost data from `raw.githubusercontent.com`; the TYNDP time series are in `data/`.

## 1 · Set up

Download this repository and create the environment using the `02-hands-on-pypsa/environment.yaml` file.

As a fallback, create the environment using `.venv`, as the [Setup](../README.md#setup) explains. The environment includes Snakemake.

## 2 · Run the notebook

Use option A or B with the environment of step 1. Option C is a fallback if the local installation fails.

In all options, open `hands-on-pypsa-components.ipynb` and run the cells with **Shift + Enter**.

**Option A · VS Code**

1. Install the **Python** and **Jupyter** extensions of VS Code.
2. Open the folder of this repository (**File › Open Folder**).
3. Open the notebook and select the `.venv` kernel (**Select Kernel**, top right).

**Option B · JupyterLab**

With the environment active, run:

```bash
jupyter lab
```

JupyterLab opens in your browser. Open `02-hands-on-pypsa/hands-on-pypsa-components.ipynb` in the file browser on the left. To come back later, activate the environment again and run `jupyter lab`.

**Option C (fallback) · Google Colab**

Colab runs the notebook on Google servers, in the browser, without local installation. A Google account is required.

1. Open the [notebook in Colab](https://colab.research.google.com/github/open-energy-transition/entsoe-training/blob/main/02-hands-on-pypsa/hands-on-pypsa-components.ipynb).
2. Insert a code cell at the top and run it. It downloads this repository, with `data/`, installs the packages and moves into the notebook folder:

   ```python
   !git clone https://github.com/open-energy-transition/entsoe-training.git
   %cd entsoe-training
   !pip install -r requirements.txt
   %cd 02-hands-on-pypsa
   ```

3. If Colab asks to restart the session, restart it, then run `%cd entsoe-training/02-hands-on-pypsa` again.

## Troubleshooting

See the [Troubleshooting](../README.md#troubleshooting) of the Setup. In particular, if a cell fails with `ModuleNotFoundError: No module named 'pypsa'`, select the `.venv` kernel.

You do not need the scripts in `scripts/`: `build_notebook.py` generates the notebook, `extract_tyndp.py` writes `data/` from the TYNDP 2026 Scenarios data package.

## Licence

The code is available under the [MIT License](LICENSE). Reused material keeps its own licence. The notebook reuses material from [Data Science for Energy System Modelling](https://fneum.github.io/data-science-for-esm/) (F. Neumann, TU Berlin; MIT for code, CC-BY-4.0 for content) and from the [PyPSA example notebooks](https://docs.pypsa.org/latest/examples/) (CC-BY-4.0, code included). The files in `data/` are extracted from the [TYNDP 2026 Scenarios data](https://2026.entsos-tyndp-scenarios.eu/download/) of ENTSO-E and ENTSOG, released under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/); `scripts/extract_tyndp.py` documents the changes (subset, rounding, unit conversion). The last section of the notebook, "Sources and licences", lists every source and its licence.
