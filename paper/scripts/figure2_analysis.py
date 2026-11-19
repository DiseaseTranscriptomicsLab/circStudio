"""Figure 2: descriptive analysis of one bundled actigraphy recording.

Five panels, all computed from the same 12.8-day wrist recording
(``example_01.AWD``, one-minute epochs, activity counts only):

    (a) double-plotted actogram
    (b) average daily activity profile with the L5 and M10 windows marked
    (c) rest intervals returned by three sleep-scoring algorithms
    (d) detrended fluctuation analysis
    (e) the circadian component recovered by singular spectrum analysis

Every number comes from a public circStudio function, so the figure doubles as
a check that the library's parts agree with one another on real data.

Authored at the GigaByte text width (397 pt = 5.51 in) so LaTeX does not
rescale it; the font sizes below are the sizes that appear in print.

Run from the ``paper/`` directory:  ``python scripts/figure2_analysis.py``
"""

import sys
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

# Use circStudio from this repository rather than any installed copy.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')          # write straight to file; no display needed
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

import circstudio as cs
from circstudio.io import read_awd

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8,
                     'axes.linewidth': 0.7,
                     'xtick.major.width': 0.7, 'ytick.major.width': 0.7,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'savefig.bbox': 'tight',
                     'pdf.fonttype': 42})    # embed real glyphs, not outlines

# One recording drives every panel; `activity` is counts per one-minute epoch.
r = read_awd('../src/circstudio/data/example_01.AWD')
a = r.activity

INK = '#1b1b1b'; BLUE = '#2c6fbb'; ORANGE = '#d9722b'; GREY = '#9a9a9a'

fig = plt.figure(figsize=(5.51, 6.9))
gs = GridSpec(3, 2, height_ratios=[1.25, 1.0, 1.0], hspace=0.62, wspace=0.36)


# =============================================================================
# (a) Double-plotted actogram
# =============================================================================
# Each row spans 48 h, so a rhythm drifting past midnight reads as a diagonal.

ax = fig.add_subplot(gs[0, :])

# Bin to 10 min (144 bins/day): fine enough to see structure, not solid ink.
s = a.resample('10min').sum()

# Anchor row 1 to midnight so rows align to clock time, not to recording start.
day0 = s.index[0].normalize()
ndays = int(np.floor((s.index[-1] - day0) / pd.Timedelta('1D'))) + 1

# Pad onto a complete grid so partial first/last days read as zero, not shift rows.
full = (s.reindex(pd.date_range(day0, periods=ndays * 144, freq='10min'))
         .fillna(0).values.reshape(ndays, 144))

# Scale by the 99.5th percentile so one movement spike cannot flatten every day.
mx = np.nanpercentile(full, 99.5)

for d in range(ndays):
    # Day 1 sits at the top, so row height counts down.
    base = ndays - d
    row = np.clip(full[d] / mx, 0, 1)
    # The right-hand half repeats the next day; the final row has no successor.
    if d + 1 < ndays:
        nxt = np.clip(full[d + 1] / mx, 0, 1)
    else:
        nxt = np.zeros(144)
    # 288 ten-minute bins laid out across 48 hours.
    x = np.arange(288) / 6.0
    y = np.concatenate([row, nxt])
    # 0.9 keeps the tallest bar just clear of the row above.
    ax.fill_between(x, base, base + 0.9 * y, color=INK, lw=0, step='mid')

ax.set_xlim(0, 48); ax.set_ylim(0.5, ndays + 1.1)
ax.set_xticks(np.arange(0, 49, 6))
# Relabel the second 24 h as 00-24 again, per the double-plot convention.
ax.set_xticklabels([f'{h % 24:02d}' for h in range(0, 49, 6)])
ax.set_yticks(np.arange(1, ndays + 1))
ax.set_yticklabels([str(ndays + 1 - p) for p in range(1, ndays + 1)], fontsize=6)
ax.set_xlabel('Clock time (h), double-plotted'); ax.set_ylabel('Day of recording')
ax.set_title('(a)  Double-plotted actogram of a 12.8-day wrist recording',
             loc='left', fontsize=7.6, fontweight='bold')
# The y axis counts days, so a spine would imply a scale that isn't there.
ax.spines['left'].set_visible(False); ax.tick_params(axis='y', length=0)


# =============================================================================
# (b) Average daily profile, with the L5 and M10 windows
# =============================================================================
# L5 and M10: mean activity over the 5 least and 10 most active hours of the
# average day. Their ratio is the relative amplitude, a standard rhythm measure.

ax = fig.add_subplot(gs[1, 0])

# Mean activity at each time of day across all days, smoothed over 30 min.
prof = cs.daily_profile(a, whs='30min')
# Some circStudio versions also return a plot handle; keep only the series.
if isinstance(prof, tuple):
    prof = prof[0]

# The profile index is a Timedelta since midnight; convert to decimal hours.
xs = np.array([t.total_seconds() / 3600 for t in prof.index])
ax.plot(xs, prof.values, color=INK, lw=1.1)

# Each call returns (window onset, mean activity over that window).
l5t, l5v = cs.l5(a)
m10t, m10v = cs.m10(a)
for t, v, c, lab in [(l5t, l5v, BLUE, 'L5'), (m10t, m10v, ORANGE, 'M10')]:
    h = t.total_seconds() / 3600
    span = 5 if lab == 'L5' else 10
    # Clip at 24 h: a late-starting window wraps past midnight, off this axis.
    ax.axvspan(h, min(h + span, 24), color=c, alpha=0.13, lw=0)
    ax.hlines(v, h, min(h + span, 24), color=c, lw=1.4)
    # Park the label near the top of the panel, clear of the activity trace.
    ax.text(h + span / 2, ax.get_ylim()[1] * 0.93, lab, color=c, fontsize=7.5,
            ha='center', va='top', fontweight='bold')

ax.set_xlim(0, 24); ax.set_xticks(range(0, 25, 6))
ax.set_xlabel('Time of day (h)'); ax.set_ylabel('Activity (counts / min)')
ax.set_title('(b)  Average daily profile', loc='left', fontsize=7.6,
             fontweight='bold')


# =============================================================================
# (c) Rest intervals from three scoring algorithms
# =============================================================================
# All three return 1 for rest, 0 for activity, one value per epoch.

ax = fig.add_subplot(gs[1, 1])

# Two days from the middle of the recording, skipping the partial first day.
seg = a.loc[a.index[0] + pd.Timedelta('1D'): a.index[0] + pd.Timedelta('3D')]
t = (seg.index - seg.index[0]).total_seconds() / 3600

ax.fill_between(t, 0, seg.values / seg.values.max(), color=GREY, lw=0, alpha=0.75)

# Score the whole recording, then crop: each algorithm uses a rolling window
# and would answer differently near the edges of a short segment.
# Cole-Kripke needs 'mean' here; its default settings require epochs <= 30 s.
algos = [('Roenneberg', cs.Roenneberg(a)),
         ('Cole-Kripke', cs.Cole_Kripke(a, settings='mean')),
         ('Sadeh', cs.Sadeh(a))]

for i, (nm, v) in enumerate(algos):
    v = pd.Series(np.asarray(v, dtype=float), index=a.index).loc[seg.index]
    # Stack the three algorithms as bands below the activity trace.
    ax.fill_between(t, -0.16 * (i + 1) - 0.115, -0.16 * (i + 1) + 0.015,
                    where=v.values > 0.5, color=[BLUE, ORANGE, '#4a9c5b'][i], lw=0)
    # Names sit past 48 h, in the margin created by the wider xlim below.
    ax.text(49.5, -0.16 * (i + 1) - 0.05, nm, fontsize=6.2, ha='left',
            va='center', color=[BLUE, ORANGE, '#4a9c5b'][i])

# xlim runs to 62 only to make room for the labels; the data end at 48 h.
ax.set_xlim(0, 62); ax.set_ylim(-0.66, 1.05); ax.set_yticks([0, 0.5, 1])
ax.set_xticks(range(0, 49, 12)); ax.set_xlabel('Hours from start of day 2')
ax.set_ylabel('Normalized activity')
ax.set_title('(c)  Rest intervals, three algorithms', loc='left', fontsize=7.6,
             fontweight='bold')
# Stop both spines at the meaningful range so the margin reads as empty space.
ax.spines['left'].set_bounds(0, 1)
ax.spines['bottom'].set_bounds(0, 48)


# =============================================================================
# (d) Detrended fluctuation analysis
# =============================================================================
# How fast activity fluctuations grow with window size: F(n) ~ n^alpha, so
# alpha is the log-log slope. 0.5 is uncorrelated noise; healthy human activity
# sits near 1, meaning correlations persist across timescales.

ax = fig.add_subplot(gs[2, 0])

# Windows from 10 min to ~33 h, log-spaced so large windows don't dominate the fit.
narr = cs.Fractal.equally_spaced_logscale_range(20, start=10, stop=2000).astype(int)
# Rounding to whole epochs can produce duplicates.
narr = np.unique(narr)

# deg=1 removes a linear trend within each window before measuring fluctuation.
F = np.asarray(cs.Fractal.dfa(a, narr, deg=1))
alpha, err = cs.Fractal.generalized_hurst_exponent(F, narr)

ax.loglog(narr, F, 'o', ms=3.2, color=INK, mfc='none', mew=0.8)

# Draw the fitted power law, anchoring the line through the first data point.
fitx = np.array([narr.min(), narr.max()])
c = np.log10(F[0]) - alpha * np.log10(narr[0])
ax.loglog(fitx, 10 ** (c + alpha * np.log10(fitx)), '-', color=ORANGE, lw=1.2)

ax.text(0.05, 0.88, r'$\alpha$ = %.3f $\pm$ %.3f' % (alpha, err),
        transform=ax.transAxes, fontsize=7.5, color=ORANGE)
ax.set_xlabel('Window size $n$ (epochs)'); ax.set_ylabel('Fluctuation $F(n)$')
ax.set_title('(d)  Detrended fluctuation analysis', loc='left', fontsize=7.6,
             fontweight='bold')


# =============================================================================
# (e) Singular spectrum analysis
# =============================================================================
# SSA splits the series into additive components; with a 24 h window the
# leading ones carry the circadian rhythm.

ax = fig.add_subplot(gs[2, 1])

ssa = cs.SSA(a, window_length='24h')
ssa.fit()
# Summing the first three components recovers a smooth daily cycle.
rec = ssa.reconstruct_signal([0, 1, 2])

# The reconstruction can be marginally shorter, so trim the index to match.
rr = pd.Series(np.asarray(rec), index=a.index[:len(np.asarray(rec))])

# Four days shows the recovered cycle without crowding the panel.
w = rr.loc[a.index[0]:a.index[0] + pd.Timedelta('4D')]
raw = a.loc[w.index]
tw = (w.index - w.index[0]).total_seconds() / 3600

ax.plot(tw, raw.values, color=GREY, lw=0.35, alpha=0.85, label='raw')
ax.plot(tw, w.values, color=BLUE, lw=1.3, label='SSA (3 components)')
ax.set_xlim(0, 96); ax.set_xticks(range(0, 97, 24))
ax.set_xlabel('Hours from start'); ax.set_ylabel('Activity (counts / min)')
ax.legend(frameon=False, fontsize=6.5, loc='upper right')
ax.set_title('(e)  Singular spectrum analysis', loc='left', fontsize=7.6,
             fontweight='bold')


# =============================================================================
# Output
# =============================================================================
# PDF for LaTeX (vector), PNG for quick viewing.
fig.savefig('figures/fig2_analysis.pdf')
fig.savefig('figures/fig2_analysis.png', dpi=220)

# Echo the headline numbers so they can be checked against the manuscript.
print('IS=%.4f IV=%.4f RA=%.4f alpha=%.4f' % (cs.IS(a), cs.IV(a), cs.ra(a), alpha))
print('saved')
