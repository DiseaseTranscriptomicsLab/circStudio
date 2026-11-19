"""Reference sleep scoring for Table 1, computed with pyActigraphy.

Run this in a pyActigraphy environment (see paper/README.md). It writes
``pyact_sleep.pkl`` next to itself; ``compare_sleep_circstudio.py`` then reads
that file and reports the epoch-by-epoch agreement.

Two notes on the algorithm settings:

* ``CK`` is called with ``settings='mean'``. The bundled recordings are sampled
  at one minute, and pyActigraphy's default Cole-Kripke settings require an
  epoch of 30 s or shorter.
* Everything else runs at its package default.
"""

import pickle
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from pyActigraphy.io import read_raw_awd  # noqa: E402

DATA = Path(__file__).resolve().parents[2] / "src" / "circstudio" / "data"
FILES = ["example_01", "example_02", "example_03", "example_04", "example_05"]

store = {}
for name in FILES:
    r = read_raw_awd(str(DATA / f"{name}.AWD"))
    scored = {}
    algorithms = [
        ("CK", lambda: r.CK(settings="mean")),
        ("Sadeh", lambda: r.Sadeh()),
        ("Scripps", lambda: r.Scripps()),
        ("Oakley", lambda: r.Oakley()),
        ("Roenneberg", lambda: r.Roenneberg()),
        ("Crespo", lambda: r.Crespo()),
    ]
    for label, call in algorithms:
        try:
            series = call()
            scored[label] = pd.Series(np.asarray(series, dtype=float), index=series.index)
        except Exception as exc:  # noqa: BLE001 - report and carry on
            scored[label] = None
            print(f"{name} {label} FAILED: {type(exc).__name__}: {exc}")
    store[name] = scored

# Pickle plain arrays rather than pandas objects: the two environments run
# incompatible pandas versions and cannot unpickle each other's frames.
payload = {
    name: {
        label: None if s is None else (s.index.astype("int64").values, s.values)
        for label, s in scored.items()
    }
    for name, scored in store.items()
}

target = Path(__file__).with_name("pyact_sleep.pkl")
with open(target, "wb") as handle:
    pickle.dump(payload, handle)
print(f"wrote {target}")
