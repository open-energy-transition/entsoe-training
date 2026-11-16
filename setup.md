# Setup

You need `conda` (from Anaconda or Miniconda) installed on your computer.
The steps are:

1. Get the training material (Git clone or ZIP download).
2. Create the `conda` environment from `environment.yaml`.
3. Activate the environment.
4. Start Jupyter Lab.

## 1. Get the training material

### Option A: Git clone (recommended)

Git lets you update the material later with one command. Open a terminal
(on Windows, the *Anaconda Prompt*) and run:

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
the folder that contains `environment.yaml`. These commands help you get there:

- `cd my_directory`: go into `my_directory`
- `cd ..`: go up one directory
- `ls` (Linux/MacOS) or `dir` (Windows): list the files in the current directory

## 2. Create the `conda` environment

Check that `conda` works:

```sh
conda --version
```

Create the environment from the root folder of the training material:

```sh
conda env create -f environment.yaml
```

This creates an environment named `entsoe-training`. It can take a few
minutes.

## 3. Activate the environment

```sh
conda activate entsoe-training
```

Your prompt now starts with `(entsoe-training)`.

> **Warning:** Activation does not persist. Run `conda activate entsoe-training`
> again in every new terminal.

## 4. Start Jupyter Lab

```sh
jupyter lab
```

Jupyter Lab opens in your web browser. Open the `notebooks/` folder and start
with `01-workshop-python.ipynb`.

## Fallback: Google Colab

If `conda` does not work on your computer, you can run the notebooks in your
browser with [Google Colab](https://colab.research.google.com/). This requires
a Google account.

1. Open https://colab.research.google.com/.
2. Select **File** → **Open notebook** → **GitHub**.
3. Enter `open-energy-transition/entsoe-training` and select the notebook.
