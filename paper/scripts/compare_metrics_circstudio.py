"""Table 1: agreement of circStudio's rhythm metrics with pyActigraphy's.

Run ``compare_metrics_pyactigraphy.py`` first, in a pyActigraphy environment;
it writes ``pyact_metrics.json``. Then run this script in a circStudio
environment.

The preprocessing that pyActigraphy applies inside each metric is reproduced
here as an explicit ``apply_filters`` call, which is the design difference
described in the manuscript.
"""

import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import circstudio as cs  # noqa: E402
from circstudio.io import read_awd  # noqa: E402

DATA = Path(__file__).resolve().parents[2] / "src" / "circstudio" / "data"
FILES = ["example_01", "example_02", "example_03", "example_04", "example_05"]

reference = json.loads(Path(__file__).with_name("pyact_metrics.json").read_text())
RESULTS = Path(__file__).resolve().parents[1] / "results"
RESULTS.mkdir(exist_ok=True)
rows = []

print(f"{'recording':<12}{'metric':<7}{'circStudio':>24}{'pyActigraphy':>24}  match")
worst = 0.0
for name in FILES:
    raw = read_awd(str(DATA / f"{name}.AWD"))

    # IS and IV: pyActigraphy resamples to 1 h and binarizes at 4 by default.
    raw.apply_filters(new_freq="1h", binarize=True, threshold=4)
    mine = {"IS": cs.IS(raw.activity), "IV": cs.IV(raw.activity)}

    # L5, M10, RA, ADAT: binarized at 4, no resampling.
    raw.reset_filters()
    raw.apply_filters(binarize=True, threshold=4)
    activity = raw.activity
    mine.update(
        {
            "L5": cs.l5(activity)[1],
            "M10": cs.m10(activity)[1],
            "RA": cs.ra(activity),
            "ADAT": cs.adat(activity),
        }
    )

    for metric in ("IS", "IV", "L5", "M10", "RA", "ADAT"):
        got = float(mine[metric])
        want = float(reference[name][metric])
        same = repr(got) == repr(want)
        rel = abs(got - want) / abs(want) if want else abs(got - want)
        worst = max(worst, rel)
        print(f"{name:<12}{metric:<7}{got:>24.17g}{want:>24.17g}  {'exact' if same else f'{rel:.2e}'}")
        rows.append({"recording": name, "metric": metric, "circstudio": repr(got),
                     "pyactigraphy": repr(want), "identical": same,
                     "relative_difference": rel})

print(f"\nworst relative difference across all metrics and recordings: {worst:.3e}")

import csv  # noqa: E402
with open(RESULTS / "agreement_metrics.csv", "w", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print(f"written to {RESULTS / 'agreement_metrics.csv'}")
