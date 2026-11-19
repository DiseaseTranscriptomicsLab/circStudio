"""Agreement between circStudio's circadian models and the ``circadian`` package.

circStudio's light-driven pacemaker models build on the implementations in the
``circadian`` package (Arcascope). This script drives both implementations with
the same light input, the same time grid and the same initial state, and
compares the predicted times of dim-light melatonin onset (DLMO) and the model
state trajectories.

The two packages integrate the equations differently: circStudio uses SciPy's
adaptive ``odeint`` solver, while ``circadian`` uses a fixed-step fourth-order
Runge-Kutta scheme with one step per input sample. Both hold the light value
constant between consecutive samples. Small differences are therefore expected
and are reported, not hidden.

Two light inputs are used:

1. a regular schedule, 16 h of 1000 lux and 8 h of darkness, for 30 days,
   sampled every 6 minutes;
2. the light channel of the ActTrust example recording bundled with
   circStudio (four days, one sample per minute).

DLMOs are matched by pairing each circStudio DLMO with the nearest one from
``circadian``. For the Breslow model, ``circadian`` does not impose a minimum
spacing between temperature minima and reports additional, closely spaced
minima on the real recording; the matched DLMOs are still compared.

Both packages must be installed in the same environment::

    pip install -e ..        # circStudio, from this repository
    pip install circadian    # version used in the manuscript: 1.0.3

Run from the ``paper/`` directory::

    python scripts/compare_models_circadian.py

Results are printed and written to ``results/models_vs_circadian.csv``.
"""

import sys
import warnings
from importlib.metadata import version
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

# Use circStudio from this repository rather than any installed copy.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))

import circstudio as cs                       # noqa: E402
from circstudio.io import read_atr            # noqa: E402
import circadian.models as cm                 # noqa: E402

RESULTS = Path(__file__).resolve().parents[1] / 'results'
RESULTS.mkdir(exist_ok=True)

# circStudio class, circadian class, label
MODELS = [
    (cs.Forger, cm.Forger99, 'Forger (1999)'),
    (cs.Jewett, cm.Jewett99, 'Jewett (1999)'),
    (cs.HannaySP, cm.Hannay19, 'Hannay single population (2019)'),
    (cs.HannayTP, cm.Hannay19TP, 'Hannay two populations (2019)'),
    (cs.Breslow13, cm.Breslow13, 'Breslow (2013)'),
]


def regular_schedule():
    """16 h at 1000 lux, 8 h dark, lights on at 08:00, 30 days, 0.1 h steps."""
    time = np.arange(0.0, 30 * 24.0, 0.1)
    clock = time % 24.0
    light = np.where(clock >= 8.0, 1000.0, 0.0)
    return time, light


def acttrust_recording():
    """Light channel of the bundled ActTrust recording, in hours from start."""
    path = Path(cs.__file__).parent / 'data' / 'test_sample_atr.txt'
    raw = read_atr(str(path))
    light = raw.light.astype(float)
    time = (light.index - light.index[0]).total_seconds().values / 3600.0
    return time, np.nan_to_num(light.values, nan=0.0)


def match(reference, other):
    """Pair each reference DLMO with the nearest DLMO from the other package."""
    pairs = []
    for r in reference:
        if len(other) == 0:
            break
        j = int(np.argmin(np.abs(other - r)))
        pairs.append(other[j] - r)
    return np.asarray(pairs)


def compare(time, light, input_name):
    rows = []
    for cs_cls, cm_cls, label in MODELS:
        # circStudio: same time grid and light, its own published initial state
        m_cs = cs_cls(inputs=light, time=time)
        initial = np.asarray(m_cs.initial_conditions, dtype=float)
        m_cs.initialize_model_states()
        dl_cs = np.asarray(m_cs.dlmos(), dtype=float)

        # circadian: identical light, time grid and initial state
        m_cm = cm_cls()
        trajectory = m_cm(time, initial, light)
        dl_cm = np.asarray(m_cm.dlmos(), dtype=float)

        diffs = match(dl_cs, dl_cm)
        S_cs, S_cm = np.asarray(m_cs.model_states), np.asarray(trajectory.states)
        if cs_cls is cs.Breslow13:
            # Oscillator and photoreceptor states (x, xc, n) are compared
            # separately from the melatonin compartments: circadian's fixed-step
            # scheme lets pineal melatonin overshoot below zero after bright
            # light, which the model's guard is meant to prevent.
            core_diff = np.max(np.abs(S_cs[:, :3] - S_cm[:, :3]))
            mel_diff = np.max(np.abs(S_cs[:, 3:] - S_cm[:, 3:]))
            min_h1 = S_cm[:, 3].min()
        else:
            core_diff = np.max(np.abs(S_cs - S_cm))
            mel_diff = min_h1 = np.nan
        rows.append({
            'input': input_name,
            'model': label,
            'dlmo_circstudio': len(dl_cs),
            'dlmo_circadian': len(dl_cm),
            'max_abs_dlmo_difference_min': float(np.max(np.abs(diffs)) * 60.0) if len(diffs) else np.nan,
            'sampling_interval_min': float(np.median(np.diff(time)) * 60.0),
            'max_abs_difference_oscillator_states': float(core_diff),
            'max_abs_difference_melatonin': float(mel_diff),
            'min_pineal_melatonin_circadian': float(min_h1),
        })
    return rows


if __name__ == '__main__':
    rows = []
    rows += compare(*regular_schedule(), 'regular 16 h light : 8 h dark, 30 days')
    rows += compare(*acttrust_recording(), 'ActTrust example recording, 4 days')
    table = pd.DataFrame(rows)
    table.attrs['versions'] = {'circStudio': version('circStudio'),
                               'circadian': version('circadian')}

    pd.set_option('display.width', 160)
    print(f"circStudio {version('circStudio')}  |  circadian {version('circadian')}")
    print(table.to_string(index=False))
    table.to_csv(RESULTS / 'models_vs_circadian.csv', index=False)
    print(f"\nwritten to {RESULTS / 'models_vs_circadian.csv'}")
