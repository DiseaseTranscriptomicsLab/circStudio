"""Reference values for Table 1: non-parametric rhythm metrics from pyActigraphy.

Run this in a pyActigraphy environment (see paper/README.md). It writes
``pyact_metrics.json`` next to itself; ``compare_metrics_circstudio.py`` then
reads that file and reports the agreement.

pyActigraphy's metric methods carry their own preprocessing arguments. The
defaults used here are the package defaults: IS and IV resample to 1 h and
binarize at a threshold of 4 counts; L5, M10, RA and ADAT binarize at 4 without
resampling. ``compare_metrics_circstudio.py`` reproduces exactly this
preprocessing through ``Raw.apply_filters`` before calling the circStudio
metric functions.
"""

import json
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

from pyActigraphy.io import read_raw_awd  # noqa: E402

DATA = Path(__file__).resolve().parents[2] / "src" / "circstudio" / "data"
FILES = ["example_01", "example_02", "example_03", "example_04", "example_05"]

out = {}
for name in FILES:
    r = read_raw_awd(str(DATA / f"{name}.AWD"))
    out[name] = dict(
        IS=r.IS(),          # freq='1H', binarize=True, threshold=4
        IV=r.IV(),          # freq='1H', binarize=True, threshold=4
        L5=r.L5(),          # binarize=True, threshold=4
        M10=r.M10(),        # binarize=True, threshold=4
        RA=r.RA(),          # binarize=True, threshold=4
        ADAT=r.ADAT(),
        length=int(r.length()),
        freq=str(r.frequency),
        duration=str(r.duration()),
    )

target = Path(__file__).with_name("pyact_metrics.json")
target.write_text(json.dumps(out, indent=1, default=str))
print(f"wrote {target}")
print(json.dumps(out, indent=1, default=str))
