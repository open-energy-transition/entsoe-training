# entsoe-training

Material for the hands-on workshops of the ENTSO-E training by [Open Energy Transition](https://openenergytransition.org), November 2026.

## Folder structure

```
diagrams/                   # Sequence diagrams and other visual aids
notebooks/                  # Python refresher notebooks
02-hands-on-pypsa/          # Hands on with PyPSA components: notebook, data and build scripts
quality/                    # Code quality exercise (own conda environment)
03-reproducible-workflows/  # Reproducible and automatable workflows: script, Make and Snakemake
```

Each session folder has its own README with the steps of the session. The sessions `02-hands-on-pypsa` and `03-reproducible-workflows` share the Python environment of the [Setup](#setup).

## Setup

### Requirements

- Windows, macOS or Linux.
- Python 3.11, 3.12 or 3.13.
- Internet access to `pypi.org`, `github.com` and `raw.githubusercontent.com`. The sessions download the technology cost data from the last one.

No solver licence is needed: the sessions use [HiGHS](https://highs.dev) (open source).

### 1 · Download this repository

Clone it with git:

```bash
git clone https://github.com/open-energy-transition/entsoe-training.git
cd entsoe-training
```

Or click **Code › Download ZIP** and extract it. On Windows, extract it to a short path such as `C:\entsoe-training` to avoid the 260-character path limit.

### 2 · Create the environment

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

To come back later, open a terminal in the folder of this repository and activate the environment again (second line of the block for your system).

### Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `'py' is not recognized` | Python installed without the launcher, or the Microsoft Store stub | Reinstall Python from python.org with the py launcher |
| `Activate.ps1 cannot be loaded` | PowerShell execution policy | Run `Set-ExecutionPolicy -Scope Process Bypass`, or use `cmd` |
| pip cannot connect, or `URLError` when the costs download | Corporate proxy | Set the `HTTPS_PROXY` environment variable to your proxy address (ask your IT department), then retry |
| pip `SSL: CERTIFICATE_VERIFY_FAILED` | Corporate TLS inspection | Add `--trusted-host pypi.org --trusted-host files.pythonhosted.org`, or ask IT for the certificate bundle |
| Long path error during `pip install` | Windows 260-character path limit | Move the folder to a short path such as `C:\entsoe-training` |
| `ModuleNotFoundError: No module named 'pypsa'` | The code runs on another Python | Activate `.venv`, or select the `.venv` kernel in a notebook |

## Generate diagrams

Use pixi to create images from the diagrams.

    pixi install       # Install the environment
    pixi run diagrams  # Create the diagram png and svg files
    pixi run clean     # Remove the generated diagrams
