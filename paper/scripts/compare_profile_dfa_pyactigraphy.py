"""Reference sleep profile, sleep midpoint and DFA values, computed with pyActigraphy.

Covers the last three rows of the agreement table in the manuscript (sleep
propensity profile, sleep midpoint and detrended fluctuation analysis) for all
five example recordings.

Run this in a pyActigraphy environment (see paper/README.md). It writes
``pyact_profile_dfa.pkl`` next to itself; ``compare_profile_dfa_circstudio.py``
then reads that file and reports the differences.

All functions run at their package defaults (Roenneberg scoring for the sleep
profile and midpoint). Detrended fluctuation analysis uses first-order
detrending on the raw one-minute counts, over 20 window sizes spaced
logarithmically between 10 and 2000 epochs.
"""

import pickle
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import numpy as np  # noqa: E402
from pyActigraphy.io import read_raw_awd  # noqa: E402
from pyActigraphy.analysis import Fractal  # noqa: E402

DATA = Path(__file__).resolve().parents[2] / "src" / "circstudio" / "data"
FILES = ["example_01", "example_02", "example_03", "example_04", "example_05"]

# Window sizes for DFA, defined here (not with a package helper) so that both
# scripts use exactly the same values.
N_ARRAY = np.unique(np.geomspace(10, 2000, 20).astype(int))

payload = {"n_array": N_ARRAY}
for name in FILES:
    r = read_raw_awd(str(DATA / f"{name}.AWD"))
    profile = r.SleepProfile()
    midpoint = r.SleepMidPoint(to_td=False)
    F_n = np.asarray(Fractal.dfa(r.data.astype(float), N_ARRAY, deg=1))
    alpha = Fractal.generalized_hurst_exponent(F_n, N_ARRAY)[0]
    # Plain arrays only: the two environments run incompatible pandas versions.
    payload[name] = {
        "profile_index": np.asarray([str(t) for t in profile.index]),
        "profile_values": np.asarray(profile.values, dtype=float),
        "midpoint": float(midpoint),
        "F_n": F_n,
        "alpha": float(alpha),
    }
    print(f"{name}: midpoint={midpoint!r} alpha={alpha!r}")

target = Path(__file__).with_name("pyact_profile_dfa.pkl")
with open(target, "wb") as handle:
    pickle.dump(payload, handle)
print(f"wrote {target}")
