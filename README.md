# GraviPy: Measuring gravity anomalies from gravimeter field data

This package contains implementations of standard gravity corrections applied
to measured gravimeter data for the detection of gravity anomalies on Earth's 
surface.

For implementation reference, see this [textbook](https://www.cambridge.org/core/books/fundamentals-of-geophysics/gravity-the-figure-of-the-earth-and-geodynamics/B593AA8DF4AD615E3F351CD065364488)

## Getting started

This repository uses conda for To create a new development environment with conda, run:

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

