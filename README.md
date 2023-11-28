# GraviPy: Measuring gravity anomalies from gravimeter field data

This package contains implementations of standard gravity corrections applied
to measured gravimeter data for the detection of gravity anomalies on Earth's 
surface.

For implementation reference, see this [textbook](https://www.eps.mcgill.ca/~courses/c510/%5BTurcotte_D.L.,_Schubert_G.%5D_Geodynamics(Bookos.org).pdf)

To calculate the geoid height, we use UNAVCO's [geoid height calculator](https://www.unavco.org/software/geodetic-utilities/geoid-height-calculator/geoid-height-calculator.html)

We also make use of [LongmanTide](https://github.com/jrleeman/LongmanTide), a 
fork of which can be pip installed using `pip install tidegravity` (see [PyPI](https://pypi.org/project/tidegravity/) for details).

## Git resources

This [lecture](https://missing.csail.mit.edu/2020/version-control/) is awesome, even if you've been using git for a while.

If you're having trouble pushing to the main branch, it's possible that someone
else has pushed to it already and your local copy of the main branch is not
up to date. An easy thing to try is running `git fetch` to get any updated
changes to the remote branch on github (i.e., `origin main`) and stack your
changes onto those changes by running `git rebase`. If this fails, it's probably
because you have a merge conflict. VSCode has a pretty good interface for
fixing merge conflicts.

## Getting started 

Open a terminal, navigate to a desired parent directory on your computer and clone this repository on your computer by running:

```
git clone https://github.com/maxfilter/gravipy.git
```

This will create a new directory on your computer called `gravipy` at the
location you ran the command.

Run `cd gravipy` from the terminal to enter into the newly created repository.

This repository uses [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) to manage python dependencies. To create a new development environment for this project with conda, run:

```sh
conda env create -f environment.yaml
```

You can activate this environment by calling:

```sh
conda activate gravipy
```

Next, to install the `gravipy` package, from the directory containing `setup.py` run:

```
pip install -e .
```

You should now be able to import `gravipy`. You can verify this by running `python3 -c "import gravipy"` in your terminal.


If you `conda install` or `pip install` any modules, you can add them to the `environment.yaml` by calling:

```sh
conda env export --from-history > environment.yaml
```

## Brief description of library files

- `correct.py`: The main method that runs all corrections on gravimeter data.
- `drift.py`:  Instrument drift corrections.
- `elevation.py`: Elevation corrections, including free-air, Bouguer plate, and latitude.
- `tidal.py`: Tidal corrections on measured gravity data.
- `normal.py`: Computes normal gravity from referenced ellipsoid.

