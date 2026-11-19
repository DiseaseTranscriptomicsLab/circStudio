"""Figure 3: the circadian pacemaker models in circStudio.

Four panels:

    (a) two synthetic light schedules, built with the ``Light`` container
    (b) successive predicted DLMOs under the bright schedule, four models
    (c) the same four models under a dimmer schedule delayed by 4 h
    (d) a real recording, with scored rest intervals and predicted DLMOs

DLMO is dim-light melatonin onset, the standard marker of internal circadian
phase. Each model is a system of differential equations driven by light: give
it a light time series, integrate, and it reports when melatonin would rise.

Panels (b) and (c) make the point that the four models agree on the direction
of a phase shift but not on its size, so the choice of model matters.

Authored at the GigaByte text width (397 pt = 5.51 in) so LaTeX does not
rescale it; the font sizes below are the sizes that appear in print.

Run from the ``paper/`` directory:  ``python scripts/figure3_models.py``
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
from circstudio.io import read_awd, read_atr

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8,
                     'axes.linewidth': 0.7,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'savefig.bbox': 'tight',
                     'pdf.fonttype': 42})    # embed real glyphs, not outlines

INK = '#1b1b1b'; BLUE = '#2c6fbb'; ORANGE = '#d9722b'
GREEN = '#4a9c5b'; PURPLE = '#8459a5'; GREY = '#9a9a9a'


# =============================================================================
# Two synthetic light schedules
# =============================================================================
# When `low != high`, `Light.create` fills every light-on bin with an
# independent uniform draw between them -- so these are not square waves. With
# low=0, high=1000 the light-on block spans the full range and averages ~475
# lux, which stands in for the minute-to-minute variability of real light
# exposure rather than an idealised laboratory schedule.
#
# Two consequences worth knowing:
#   1. The draw is taken once, for a single day, and then tiled across all 16
#      days, so every day carries an identical pattern.
#   2. The generator is unseeded, so the pattern changes between runs and the
#      predicted DLMOs move by up to one 10-min bin. That changes no statement
#      in the paper but stops the figure being bit-for-bit reproducible, so the
#      generator is pinned for these two calls and restored immediately after.
_rng = np.random.default_rng(20260804)
_orig_default_rng = np.random.default_rng
np.random.default_rng = lambda *a, **k: _rng

# Bright reference: 16 h light drawn uniformly over 0-1000 lux, 8 h dark.
L_reg = cs.Light.create(total_days=16, light_on_hours=16, bins_per_hour=6, low=0, high=1000, schedule_starts_at=0)
# Same photoperiod, dimmer (0-150 lux) and starting 4 h later.
L_dim = cs.Light.create(total_days=16, light_on_hours=16, bins_per_hour=6, low=0, high=150,  schedule_starts_at=4)

# Restore the generator so nothing downstream is affected.
np.random.default_rng = _orig_default_rng

# Shared time axis, in hours from the start of the schedule.
t = np.asarray(L_reg.time_vector)

fig = plt.figure(figsize=(5.51, 6.6))
gs = GridSpec(3, 2, height_ratios=[0.72, 1.0, 0.85], hspace=0.78, wspace=0.42)


# =============================================================================
# (a) The two light schedules
# =============================================================================

ax = fig.add_subplot(gs[0, :])

# Divide by 24 to label the x axis in days rather than hours.
ax.plot(t / 24, np.asarray(L_reg.light_vector), color=ORANGE, lw=0.8,
        label='16 h : 8 h, uniform\n0-1000 lux (mean 475)')
ax.plot(t / 24, np.asarray(L_dim.light_vector), color=BLUE, lw=0.8,
        label='16 h : 8 h, uniform\n0-150 lux, onset delayed 4 h')
ax.set_xlim(0, 16); ax.set_xlabel('Days'); ax.set_ylabel('Illuminance (lux)')
# Legend to the right of the axis, as in panel (d), so it never covers the traces.
ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), fontsize=6.2, ncol=1,
          frameon=True, framealpha=1.0, edgecolor='#cccccc')
ax.set_ylim(0, 1100)
ax.set_title('(a)  Two synthetic light schedules used as model input',
             loc='left', fontsize=7.6, fontweight='bold')


# =============================================================================
# (b, c) Predicted DLMOs under each schedule
# =============================================================================
# Every model exposes the same interface, so the same loop drives all four.
# They start from their published initial conditions, which is why the first
# few DLMOs drift before settling: the models are entraining to the schedule.

models = [('Forger', cs.Forger, ORANGE), ('Jewett', cs.Jewett, BLUE),
          ('Hannay SP', cs.HannaySP, GREEN), ('Hannay TP', cs.HannayTP, PURPLE)]

# (b) bright schedule
ax = fig.add_subplot(gs[1, 0])
rows = []
for nm, M, c in models:
    m = M(inputs=np.asarray(L_reg.light_vector), time=t)
    m.integrate()
    d = np.asarray(m.dlmos())
    # Drop any marker before the schedule starts.
    d = d[(d > 0)]
    # DLMOs accumulate in hours since the start; mod 24 converts to clock time.
    ax.plot(np.arange(1, len(d) + 1), np.mod(d, 24), 'o-', color=c, ms=2.6,
            lw=1.0, label=nm)
    # Keep the last DLMO as the entrained steady-state phase.
    rows.append((nm, float(np.mod(d[-1], 24))))
ax.set_xlabel('Successive predicted DLMO'); ax.set_ylabel('Clock time (h)')
ax.legend(frameon=False, fontsize=6.5, ncol=2)
ax.set_title('(b)  Entrainment, bright', loc='left', fontsize=7.6,
             fontweight='bold')

# (c) dim and delayed schedule, identical procedure
ax = fig.add_subplot(gs[1, 1])
rows2 = []
for nm, M, c in models:
    m = M(inputs=np.asarray(L_dim.light_vector), time=t)
    m.integrate()
    d = np.asarray(m.dlmos())
    d = d[(d > 0)]
    ax.plot(np.arange(1, len(d) + 1), np.mod(d, 24), 'o-', color=c, ms=2.6,
            lw=1.0, label=nm)
    rows2.append((nm, float(np.mod(d[-1], 24))))
ax.set_xlabel('Successive predicted DLMO'); ax.set_ylabel('Clock time (h)')
ax.set_title('(c)  Entrainment, dim and delayed', loc='left', fontsize=7.6,
             fontweight='bold')


# =============================================================================
# (d) A real recording
# =============================================================================
# The bundled ActTrust recording (the same file as the code example in the
# manuscript) has a light channel, so the model is driven by the light the
# wearer actually received. The preprocessing matches the code example:
# inactivity longer than two hours is masked and imputed.

ax = fig.add_subplot(gs[2, :])

r = read_atr(str(Path(cs.__file__).parent / 'data' / 'test_sample_atr.txt'))
r.create_inactivity_mask(duration='120min')
r.apply_filters(apply_mask=True, impute_nan=True)
a, light = r.activity, r.light

# Forger model driven by the recorded light; the starting state is obtained by
# replaying the light record until the predicted DLMO stops changing.
mF = cs.Forger(data=light)
mF.get_initial_conditions(loop_number=10, data=light)
mF.initialize_model_states()
dl = np.asarray(mF.dlmos())          # hours from the start of the recording

# Model time axis in hours from the first sample.
tt = (a.index - a.index[0]).total_seconds().values / 3600.0
dl = dl[(dl > 0) & (dl < tt[-1])]

# Roenneberg scoring returns 1 for rest, 0 for activity.
rest = pd.Series(np.asarray(cs.Roenneberg(a), dtype=float), index=a.index)

GOLD = '#e0a526'
# Normalize by a high percentile so spikes do not flatten the traces.
ax.fill_between(tt, 0, np.clip(a.values / np.nanpercentile(a.values, 99.5), 0, 1.3),
                color=GREY, lw=0, alpha=0.8, label='activity (normalized)')
ax.plot(tt, np.clip(light.values / np.nanpercentile(light.values, 99), 0, 1.3),
        color=GOLD, lw=0.6, label='light (normalized)')
# Rest intervals as a band below the traces.
ax.fill_between(tt, -0.30, -0.06, where=rest.values > 0.5, color=BLUE, lw=0,
                label='rest (Roenneberg)')
# One vertical line per predicted DLMO.
for i, d0 in enumerate(dl):
    ax.axvline(d0, color=ORANGE, lw=1.0, alpha=0.9,
               label='predicted DLMO (Forger)' if i == 0 else None)

# Ticks at each midnight, labelled by clock date.
t0 = a.index[0]
midnights = pd.date_range(t0.normalize() + pd.Timedelta(days=1), a.index[-1], freq='D')
ax.set_xticks((midnights - t0).total_seconds() / 3600.0)
ax.set_xticklabels([f'day {i + 2}' for i in range(len(midnights))])
ax.set_xlim(0, tt[-1]); ax.set_ylim(-0.38, 1.45)
ax.set_xlabel('Time of recording (ticks at midnight)')
ax.set_ylabel('Normalized value')
ax.legend(loc='upper left', bbox_to_anchor=(1.0, 1.0), fontsize=6.2,
          frameon=True, framealpha=1.0, edgecolor='#cccccc')
ax.set_title('(d)  A real recording with a light channel: scored rest and predicted DLMO',
             loc='left', fontsize=7.6, fontweight='bold')
# Stop the spine at 1: the band below zero is a category, not a value.
ax.spines['left'].set_bounds(0, 1)


# =============================================================================
# Output
# =============================================================================
# PDF for LaTeX (vector), PNG for quick viewing.
fig.savefig('figures/fig3_models.pdf')
fig.savefig('figures/fig3_models.png', dpi=220)

# Echo the steady-state phases so they can be checked against the manuscript.
print('bright:', rows)
print('dim:', rows2)
print('n dlmo real', len(dl))
