# Reproducing the circStudio manuscript

This folder contains the code that produces every figure and every agreement
analysis reported in the GigaByte Technical Release describing circStudio
(version 1.1.3).

```
paper/
├── scripts/    code for the figures and the agreement analyses
├── figures/    the figures, as PDF (for the manuscript) and PNG (for viewing)
└── results/    expected outputs of the agreement analyses, as CSV
```

All commands below are run from this `paper/` folder. The scripts import
circStudio from `../src` and read the example recordings bundled with the
package in `../src/circstudio/data`.

## 1. Environment

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ..              # circStudio 1.1.3 and its dependencies
pip install circadian==1.0.3   # only for the model comparison (section 4)
```

## 2. Figures

```bash
python scripts/figure1_architecture.py        # Figure 1, architecture of circStudio
python scripts/figure2_analysis.py            # Figure 2, descriptive analysis
python scripts/figure_pacemaker_schematic.py  # Figure 3, structure of the pacemaker models
python scripts/figure3_models.py              # Figure 4, circadian models
```

Each script writes a PDF and a 220 dpi PNG into `figures/`. Figure 1 and the
schematic part of Figure 3 take no input data. Figure 2 reads `example_01.AWD`.
Figure 4 builds two synthetic light schedules with the `Light` container and,
in panel (d), reads the ActTrust recording `test_sample_atr.txt`, whose light
channel drives the Forger model.

`Light.create` draws its light-on intensities from an unseeded random
generator, so `figure3_models.py` pins the generator for the two calls that
build the schedules. Without this, the predicted onsets in panels (b) and (c)
could move by one sampling bin (10 minutes) between runs.

## 3. Agreement with pyActigraphy (Table 3)

circStudio requires NumPy 2 and pandas 2, while pyActigraphy 1.2.2 requires
NumPy 1 and pandas 1. They cannot be installed in the same environment, so each
comparison runs in two steps: a pyActigraphy script writes its results to a file
next to itself, and the matching circStudio script reads that file.

```bash
# Step 1: reference values, in a separate pyActigraphy environment (Python 3.10)
python3.10 -m venv .venv-pyact
./.venv-pyact/bin/pip install pyActigraphy==1.2.2 'numpy==1.23.5'
./.venv-pyact/bin/python scripts/compare_metrics_pyactigraphy.py      # -> scripts/pyact_metrics.json
./.venv-pyact/bin/python scripts/compare_sleep_pyactigraphy.py        # -> scripts/pyact_sleep.pkl
./.venv-pyact/bin/python scripts/compare_profile_dfa_pyactigraphy.py  # -> scripts/pyact_profile_dfa.pkl

# Step 2: circStudio values and the comparison, in the circStudio environment
python scripts/compare_metrics_circstudio.py      # -> results/agreement_metrics.csv
python scripts/compare_sleep_circstudio.py        # -> results/agreement_sleep_scoring.csv
python scripts/compare_profile_dfa_circstudio.py  # -> results/agreement_profile_midpoint_dfa.csv
```

pyActigraphy 1.2.2 pins NumPy 1.21, which its own dependency numba rejects;
installing NumPy 1.23.5 afterwards resolves this (pip reports the pin as a
conflict, which can be ignored for these scripts).

The intermediate files written in step 1 are not tracked in the repository;
the CSV files in `results/` contain both packages' values side by side and are
the expected outputs.

| Comparison | Recordings | Result |
|---|---|---|
| Interdaily stability, intradaily variability, L5, M10, relative amplitude, average daily total activity | 5 | identical (30 of 30 values) |
| Cole-Kripke, Sadeh, Scripps, Oakley, Roenneberg | 5 | identical on all 111,272 epochs |
| Crespo | 5 | identical after inverting the rest/activity label |
| Sleep propensity profile | 5 | maximum absolute difference 0 |
| Sleep midpoint | 5 | identical |
| Detrended fluctuation analysis, F(n) and scaling exponent | 5 | maximum relative difference 3.1 × 10⁻¹⁵ (F(n)); maximum absolute difference 5.6 × 10⁻¹⁶ (exponent) |

## 4. Agreement with the `circadian` package

```bash
python scripts/compare_models_circadian.py   # -> results/models_vs_circadian.csv
```

The Forger, Jewett, both Hannay and the Breslow models are driven with
identical light, time grid and initial state in circStudio and in `circadian`
1.0.3, using a regular schedule (16 h at 1000 lux, 8 h dark, 30 days) and the
light channel of the ActTrust example recording. All predicted dim-light
melatonin onsets fall on the same sample in both packages, and the oscillator
states differ by at most 10⁻³. The two packages integrate differently (SciPy's
`odeint` in circStudio, fixed-step fourth-order Runge-Kutta in `circadian`),
which accounts for the small differences in state.

For the Breslow model, the melatonin compartments differ by up to 0.68. After
bright light, `circadian`'s fixed-step scheme lets pineal melatonin overshoot
below zero (to -0.68 on the regular schedule), which the model's guard against
negative production is meant to prevent; circStudio keeps it at zero or above.
On the real recording, `circadian` also reports extra, closely spaced
temperature minima for this model because it imposes no minimum spacing
between them; each circStudio onset is matched to the nearest one.

The St Hilaire and Skeldon models, which include sleep-wake dynamics, are not
part of this comparison.

## 5. Test suite

```bash
pip install pytest pytest-mock pyexcel-ods
pytest ../tests -q
```

The suite runs automatically through GitHub Actions on Linux, macOS and Windows
with Python 3.12, 3.13 and 3.14.

## Versions used for the results reported in the manuscript

| Environment | Versions |
|---|---|
| circStudio | circStudio 1.1.3, Python 3.13.18, NumPy 2.5.5, pandas 2.3.3, SciPy 1.18.1, matplotlib 3.11.2 |
| circadian comparison | as above, plus circadian 1.0.3 |
| pyActigraphy reference | pyActigraphy 1.2.2, Python 3.10.12, NumPy 1.23.5, pandas 1.3.5 |
