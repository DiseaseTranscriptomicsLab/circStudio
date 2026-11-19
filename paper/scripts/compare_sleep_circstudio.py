"""Table 1: epoch-by-epoch agreement of circStudio's sleep scoring with pyActigraphy's.

Run ``compare_sleep_pyactigraphy.py`` first, in a pyActigraphy environment; it
writes ``pyact_sleep.pkl``. Then run this script in a circStudio environment.

For each algorithm the script reports the fraction of overlapping epochs on
which the two packages agree, and separately the fraction on which they agree
after inverting one of the two label sets. The second number is what exposes
the Crespo convention difference described in the manuscript: circStudio
returns 1 for rest, pyActigraphy returns 1 for activity, and the underlying
intervals are identical.
"""

import pickle
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import circstudio as cs  # noqa: E402
from circstudio.io import read_awd  # noqa: E402

DATA = Path(__file__).resolve().parents[2] / "src" / "circstudio" / "data"
FILES = ["example_01", "example_02", "example_03", "example_04", "example_05"]

with open(Path(__file__).with_name("pyact_sleep.pkl"), "rb") as handle:
    reference = pickle.load(handle)

RESULTS = Path(__file__).resolve().parents[1] / "results"
RESULTS.mkdir(exist_ok=True)
rows = []
print(f"{'recording':<12}{'algorithm':<12}{'epochs':>8}{'direct':>10}{'inverted':>10}")
total_epochs = 0
for name in FILES:
    raw = read_awd(str(DATA / f"{name}.AWD"))
    activity = raw.activity

    algorithms = {
        "CK": lambda: cs.Cole_Kripke(activity, settings="mean"),
        "Sadeh": lambda: cs.Sadeh(activity),
        "Scripps": lambda: cs.Scripps(activity),
        "Oakley": lambda: cs.Oakley(activity),
        "Roenneberg": lambda: cs.Roenneberg(activity),
        "Crespo": lambda: cs.Crespo(activity, frequency=raw.frequency),
    }

    for label, call in algorithms.items():
        target = reference[name].get(label)
        if target is None:
            print(f"{name:<12}{label:<12}{'--':>8}  no pyActigraphy reference")
            continue

        mine = call()
        mine = pd.Series(np.asarray(mine, dtype=float), index=mine.index)
        idx, values = target
        theirs = pd.Series(values, index=pd.to_datetime(idx))

        common = mine.index.intersection(theirs.index)
        a, b = mine.loc[common].values, theirs.loc[common].values
        usable = ~(np.isnan(a) | np.isnan(b))
        direct = float(np.mean(a[usable] == b[usable]))
        inverted = float(np.mean(a[usable] == (1 - b[usable])))
        total_epochs += int(usable.sum())
        print(f"{name:<12}{label:<12}{usable.sum():>8}{direct:>10.4f}{inverted:>10.4f}")
        rows.append({"recording": name, "algorithm": label, "epochs": int(usable.sum()),
                     "agreement_direct": direct, "agreement_inverted": inverted})

print(f"\ntotal epochs compared (all algorithms): {total_epochs}")
print(f"epochs per algorithm: {total_epochs // 6}")
pd.DataFrame(rows).to_csv(RESULTS / "agreement_sleep_scoring.csv", index=False)
print(f"written to {RESULTS / 'agreement_sleep_scoring.csv'}")
