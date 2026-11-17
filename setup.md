# Setup

You can set up the Python environment in one of three ways:

- **`conda`** (from Anaconda or Miniconda)
- **`uv`**, a fast Python package and project manager
- **`pip`** with a virtual environment (requires Python 3.12 or newer)

Pick the one you are most familiar with. If you have none of them, we recommend `uv`.

The steps are:

1. Get the training material (Git clone or ZIP download).
2. Create the Python environment with `conda`, `uv` or `pip`.
3. Activate the environment.
4. Start Jupyter Lab.

## 1. Get the training material

### Option A: Git clone (recommended)

Git lets you update the material later with one command. Open a terminal
(on Windows, the *Anaconda Prompt* if you use `conda`, otherwise *PowerShell*) and run:

```sh
cd path/to/your/directory
git clone https://github.com/open-energy-transition/entsoe-training.git
cd entsoe-training
```

To get the latest changes later, run `git pull` inside the `entsoe-training`
folder.

### Option B: ZIP download

1. Open https://github.com/open-energy-transition/entsoe-training.
2. Click the green **Code** button, then **Download ZIP**.
3. Extract the ZIP file to a directory of your choice.

> **Warning:** A ZIP download does not update. To get new material, download
> and extract the ZIP file again.

### Navigating in the terminal

You run all commands below from the root folder of the training material,
the `entsoe-training` folder. These commands help you get there:

- `cd my_directory`: go into `my_directory`
- `cd ..`: go up one directory
- `ls` (Linux/MacOS) or `dir` (Windows): list the files in the current directory

## 2. Create the environment

Follow **one** of the three options below.

### Option A: `conda`

Check that `conda` works:

```sh
conda --version
```

Create the environment from the relevant subfolder of the training material:

```sh
conda env create -f 01-python-recap/environment.yaml
## Alternatively
cd 01-python-recap
conda env create -f environment.yaml
```

This creates an environment named `01-python-recap`. It can take a few minutes.

### Option B: `uv`

If you do not have `uv` yet, install it:

```sh
# Linux/MacOS
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Open a new terminal and check that `uv` works:

```sh
uv --version
```

Create a virtual environment and install the packages:

```sh
uv venv --python 3.12
uv pip install -r 01-python-recap/requirements.txt
```

This creates a `.venv` folder in `entsoe-training`. `uv` downloads Python 3.12
for you if it is not installed.

### Option C: `pip`

Check that Python 3.12 or newer works:

```sh
python --version
```

On some Linux/MacOS systems the command is `python3` instead of `python`.

Create a virtual environment and install the packages:

```sh
python -m venv .venv
```

Activate it as described in step 3, then run:

```sh
python -m pip install --upgrade pip
python -m pip install -r 01-python-recap/requirements.txt
```

## 3. Activate the environment

**`conda`:**

```sh
conda activate 01-python-recap
```

Your prompt now starts with `(01-python-recap)`.

**`uv` or `pip`:**

```sh
# Linux/MacOS
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (Command Prompt)
.venv\Scripts\activate.bat
```

Your prompt now starts with `(.venv)` or `(entsoe-training)`.

> **Warning:** Activation does not persist. Run the activation command
> again in every new terminal.

> **Tip (`uv` only):** Instead of activating, you can prefix commands with
> `uv run`, for example `uv run jupyter lab`.

## 4. Start Jupyter Lab

```sh
jupyter lab
```

Jupyter Lab opens in your web browser. Open the `01-python-recap/` folder and start
with `01-workshop-python.ipynb`.

## Fallback: Google Colab

If none of the options above work on your computer, you can run the notebooks in your
browser with [Google Colab](https://colab.research.google.com/). This requires
a Google account.

1. Open https://colab.research.google.com/.
2. Select **File** → **Open notebook** → **GitHub**.
3. Enter `open-energy-transition/entsoe-training` and select the notebook.
