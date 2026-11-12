# ENTSO-E training · Hands on with PyPSA components

Material for the session "Hands on with PyPSA components" of the ENTSO-E training by [Open Energy Transition](https://openenergytransition.org), 17 November 2026.

Goal: open `hands-on-pypsa-components.ipynb` in JupyterLab and run it.

## Requirements

- Windows, macOS or Linux.
- Python 3.11, 3.12 or 3.13.
- Internet access to `pypi.org`, `github.com` and `raw.githubusercontent.com`. The notebook downloads the technology cost data from the last one; the TYNDP time series are in `data/`.

No solver licence is needed: the notebook uses [HiGHS](https://highs.dev) (open source).

## 1 · Download this repository

Clone it with git:

```bash
git clone https://github.com/open-energy-transition/entsoe-training.git
cd entsoe-training
```

Or click **Code › Download ZIP** and extract it. On Windows, extract it to a short path such as `C:\entsoe-training` to avoid the 260-character path limit.

## 2 · Create the environment

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

## 3 · Run the notebook

With the environment active, run:

```bash
jupyter lab
```

JupyterLab opens in your browser. Open `hands-on-pypsa-components.ipynb` and run the cells with **Shift + Enter**. To come back later, activate the environment again and run `jupyter lab`.

In VS Code, open the folder, open the notebook and select the `.venv` kernel (**Select Kernel**, top right).

The notebook also runs on [Google Colab](https://colab.research.google.com/), provided you install the packages of `requirements.txt` and upload the `data/` folder.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `'py' is not recognized` | Python installed without the launcher, or the Microsoft Store stub | Reinstall Python from python.org with the py launcher |
| `Activate.ps1 cannot be loaded` | PowerShell execution policy | Run `Set-ExecutionPolicy -Scope Process Bypass`, or use `cmd` |
| pip cannot connect, or `URLError` in a data cell | Corporate proxy | Set the `HTTPS_PROXY` environment variable to your proxy address (ask your IT department), then retry |
| pip `SSL: CERTIFICATE_VERIFY_FAILED` | Corporate TLS inspection | Add `--trusted-host pypi.org --trusted-host files.pythonhosted.org`, or ask IT for the certificate bundle |
| Long path error during `pip install` | Windows 260-character path limit | Move the folder to a short path such as `C:\entsoe-training` |
| `ModuleNotFoundError: No module named 'pypsa'` | The notebook runs on another Python | Select the `.venv` kernel |

You do not need `build_notebook.py` (generates the notebook) or `extract_tyndp.py` (writes `data/` from the TYNDP 2026 Scenarios data package).

## Licence

The notebook reuses material from [Data Science for Energy System Modelling](https://fneum.github.io/data-science-for-esm/) (F. Neumann, TU Berlin; MIT for code, CC-BY-4.0 for content) and from the [PyPSA example notebooks](https://docs.pypsa.org/latest/examples/) (CC-BY-4.0, code included). The files in `data/` are extracted from the [TYNDP 2026 Scenarios data](https://2026.entsos-tyndp-scenarios.eu/download/) of ENTSO-E and ENTSOG; see the download page for its terms. The last section of the notebook, "Sources and licences", lists every source and its licence.
