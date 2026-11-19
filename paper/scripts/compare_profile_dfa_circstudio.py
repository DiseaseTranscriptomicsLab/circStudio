"""Agreement of circStudio's sleep profile, sleep midpoint and DFA with pyActigraphy's.

Run ``compare_profile_dfa_pyactigraphy.py`` first, in a pyActigraphy
environment; it writes ``pyact_profile_dfa.pkl``. Then run this script in a
circStudio environment. Results are printed and written to
``results/agreement_profile_midpoint_dfa.csv``.
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
RESULTS = Path(__file__).resolve().parents[1] / "results"
RESULTS.mkdir(exist_ok=True)

with open(Path(__file__).with_name("pyact_profile_dfa.pkl"), "rb") as handle:
    reference = pickle.load(handle)

n_array = np.asarray(reference["n_array"])
rows = []
for name in FILES:
    ref = reference[name]
    raw = read_awd(str(DATA / f"{name}.AWD"))
    activity = raw.activity

    # Sleep propensity profile (Roenneberg scoring, 15-min bins by default)
    profile = cs.SleepProfile(activity)
    mine = pd.Series(np.asarray(profile.values, dtype=float),
                     index=[str(t) for t in profile.index])
    theirs = pd.Series(ref["profile_values"], index=ref["profile_index"])
    common = mine.index.intersection(theirs.index)
    profile_diff = float(np.nanmax(np.abs(mine.loc[common].values - theirs.loc[common].values)))

    # Sleep midpoint, in minutes after midnight
    midpoint = float(cs.SleepMidPoint(activity, to_td=False))
    midpoint_diff_ns = abs(midpoint - ref["midpoint"]) * 60e9

    # Detrended fluctuation analysis on the raw counts
    F_n = np.asarray(cs.Fractal.dfa(activity.astype(float), n_array, deg=1))
    alpha = float(cs.Fractal.generalized_hurst_exponent(F_n, n_array)[0])
    F_rel = float(np.max(np.abs(F_n - ref["F_n"]) / np.abs(ref["F_n"])))
    alpha_abs = abs(alpha - ref["alpha"])

    rows.append({
        "recording": name,
        "profile_bins_compared": len(common),
        "profile_max_abs_difference": profile_diff,
        "midpoint_circstudio_min": midpoint,
        "midpoint_pyactigraphy_min": ref["midpoint"],
        "midpoint_abs_difference_ns": midpoint_diff_ns,
        "alpha_circstudio": alpha,
        "alpha_pyactigraphy": ref["alpha"],
        "alpha_abs_difference": alpha_abs,
        "F_n_max_relative_difference": F_rel,
    })

table = pd.DataFrame(rows)
pd.set_option("display.width", 200)
print(table.to_string(index=False))
print(f"\nsleep profile, max abs difference: {table.profile_max_abs_difference.max():.3g}")
print(f"sleep midpoint, max difference:    {table.midpoint_abs_difference_ns.max():.3g} ns")
print(f"DFA F(n), max relative difference: {table.F_n_max_relative_difference.max():.3g}")
print(f"DFA alpha, max abs difference:     {table.alpha_abs_difference.max():.3g}")
table.to_csv(RESULTS / "agreement_profile_midpoint_dfa.csv", index=False)
print(f"written to {RESULTS / 'agreement_profile_midpoint_dfa.csv'}")
