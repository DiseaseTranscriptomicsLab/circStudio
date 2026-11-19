"""Figure 1: circStudio workflow, from device file to descriptive measures and
model-predicted circadian phase.

Authored at the true GigaByte text width (397 pt = 5.51 in) so that
\\includegraphics[width=\\textwidth] does not rescale it and the type sizes
below are the sizes that appear in print.

The small traces are illustrative (synthetic), not data.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8,
                     'pdf.fonttype': 42})

INK = '#1b1b1b'; GREY = '#6e6e6e'; LIGHTGREY = '#b9b9b9'
BLUE = '#2c6fbb'; ORANGE = '#c8641f'; GREEN = '#3d8a4e'; PURPLE = '#7a4fa0'
FILL = {BLUE: '#eaf1fa', ORANGE: '#fcefe4', GREEN: '#eaf4ec', PURPLE: '#f1ebf7',
        GREY: '#f4f4f4'}

W, H = 100.0, 119.0
fig = plt.figure(figsize=(5.51, 5.51 * H / W))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')

LH = 2.45      # body line height (canvas units)
FS = 6.2       # body font size
rng = np.random.default_rng(7)


def panel(x, y, w, h, c):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle='round,pad=0,rounding_size=1.5',
                                fc=FILL[c], ec=c, lw=0.9))


def step(x, y, n, title, module, c):
    """Numbered step title with the sub-package name underneath."""
    ax.add_patch(Circle((x + 2.1, y - 2.0), 1.75, fc=c, ec='none'))
    ax.text(x + 2.1, y - 2.05, str(n), ha='center', va='center',
            fontsize=6.4, fontweight='bold', color='white')
    ax.text(x + 5.0, y - 2.0, title, ha='left', va='center',
            fontsize=7.6, fontweight='bold', color=c)
    if module:
        ax.text(x + 5.0, y - 5.3, module, ha='left', va='center',
                fontsize=5.2, color=GREY, family='DejaVu Sans Mono')


def lines(x, y, items, fs=FS, color=INK, lh=LH):
    for i, t in enumerate(items):
        ax.text(x, y - i * lh, t, ha='left', va='top', fontsize=fs, color=color)
    return y - len(items) * lh


def group(x, y, heading, items, c):
    """Small coloured heading followed by plain lines; returns next y."""
    ax.text(x, y, heading, ha='left', va='top', fontsize=6.3,
            fontweight='bold', color=c)
    return lines(x, y - LH - 0.2, items) - 1.7


def arrow(x1, y1, x2, y2, c=GREY):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>',
                                 mutation_scale=7, lw=0.9, color=c,
                                 shrinkA=0, shrinkB=0))


def day_trace(n_days, kind):
    """Synthetic activity or light trace, one point per 10 minutes."""
    t = np.arange(0, 24 * n_days, 1 / 6)
    hod = t % 24
    awake = (hod > 7.5) & (hod < 23.2)
    if kind == 'activity':
        y = np.where(awake, 0.35 + 0.65 * rng.random(t.size) ** 1.5,
                     0.04 * rng.random(t.size))
    else:
        sun = np.clip(np.sin((hod - 7.0) / 12.5 * np.pi), 0, None)
        y = np.where(awake, 0.12 + 0.88 * sun * (0.5 + 0.5 * rng.random(t.size)), 0.0)
    return t, y


def inset(x, y, w, h, t, v, c, bars=True):
    """Draw a small trace inside the canvas rectangle (x, y, w, h)."""
    xs = x + (t - t.min()) / (t.max() - t.min()) * w
    ys = y + v / v.max() * h
    if bars:
        ax.vlines(xs, y, ys, color=c, lw=0.35)
    else:
        ax.fill_between(xs, y, ys, color=c, lw=0, alpha=0.85)
    ax.plot([x, x + w], [y, y], color=LIGHTGREY, lw=0.5)
    return xs


# =============================================================================
# Row 1: record -> read -> clean
# =============================================================================
BW, BH, Y1 = 31.2, 22.0, H - 23.0
X = [1.0, 34.4, 67.8]

# 1 Record --------------------------------------------------------------------
panel(X[0], Y1, BW, BH, GREY)
step(X[0] + 1.6, Y1 + BH - 1.6, 1, 'Record', None, GREY)
ax.text(X[0] + 2.6, Y1 + BH - 6.4, 'wrist-worn device, days to weeks',
        fontsize=FS, color=INK, va='top')
t, a = day_trace(3, 'activity'); _, l = day_trace(3, 'light')
inset(X[0] + 9.5, Y1 + 8.6, BW - 12.0, 4.0, t, a, INK)
inset(X[0] + 9.5, Y1 + 2.8, BW - 12.0, 4.0, t, l, '#e0a526', bars=False)
ax.text(X[0] + 2.6, Y1 + 10.4, 'activity', fontsize=5.4, color=GREY, va='center')
ax.text(X[0] + 2.6, Y1 + 4.6, 'light', fontsize=5.4, color=GREY, va='center')

# 2 Read ----------------------------------------------------------------------
panel(X[1], Y1, BW, BH, BLUE)
step(X[1] + 1.6, Y1 + BH - 1.6, 2, 'Read', 'circstudio.io', BLUE)
lines(X[1] + 2.6, Y1 + BH - 8.6, [
    'Seven device formats:',
    'ActTrust, Actiwatch, Respironics,',
    'ActiGraph, Daqtometer,',
    'Tempatilumi, MESA',
    'Sleep diaries and mask logs'])

# 3 Clean ---------------------------------------------------------------------
panel(X[2], Y1, BW, BH, ORANGE)
step(X[2] + 1.6, Y1 + BH - 1.6, 3, 'Clean', None, ORANGE)
# Two sub-packages: io.mask (masking, resampling, imputation) and
# preprocessing (non-wear detection); set slightly smaller to fit the box.
ax.text(X[2] + 1.6 + 5.0, Y1 + BH - 1.6 - 5.3,
        'circstudio.io.mask, .preprocessing', ha='left', va='center',
        fontsize=4.6, color=GREY, family='DejaVu Sans Mono')
lines(X[2] + 2.6, Y1 + BH - 8.6, [
    'Detect non-wear (Troiano, Choi)',
    'Mask invalid periods',
    'Trim incomplete start and end',
    'Resample and binarize',
    'Impute gaps'])

for i in (0, 1):
    arrow(X[i] + BW + 0.3, Y1 + BH / 2, X[i + 1] - 0.3, Y1 + BH / 2)

# =============================================================================
# The shared series
# =============================================================================
YS, HS = Y1 - 10.6, 5.4
ax.add_patch(FancyBboxPatch((18.0, YS), 64.0, HS,
                            boxstyle='round,pad=0,rounding_size=2.7',
                            fc='white', ec=INK, lw=0.9))
ax.text(50.0, YS + HS / 2 - 0.1,
        'One cleaned recording: activity and light on a single time axis',
        ha='center', va='center', fontsize=6.4, fontweight='bold', color=INK)
# clean -> series (elbow)
xc = X[2] + BW / 2
ax.plot([xc, xc], [Y1 - 0.3, YS + HS / 2], color=GREY, lw=0.9,
        solid_capstyle='butt')
arrow(xc, YS + HS / 2, 82.3, YS + HS / 2)

# =============================================================================
# Row 2: two analyses of the same series
# =============================================================================
CW, CH = 48.0, 48.0
Y2 = YS - 7.4 - CH
XL, XR = 1.0, 51.0

arrow(XL + CW / 2, YS - 0.3, XL + CW / 2, Y2 + CH + 0.3)
arrow(XR + CW / 2, YS - 0.3, XR + CW / 2, Y2 + CH + 0.3)
ax.text(XL + CW / 2 + 1.4, YS - 3.7, 'activity and light', fontsize=5.4,
        color=GREY, va='center')
ax.text(XR + CW / 2 + 1.4, YS - 3.7, 'light', fontsize=5.4, color=GREY,
        va='center')
# St Hilaire 2007 also takes the sleep-wake state scored from activity
ax.text(XR + CW / 2 - 1.4, YS - 3.7,
        'and, for St Hilaire 2007,\nactivity scored as sleep or wake',
        fontsize=5.0, color=GREY, va='center', ha='right', linespacing=1.1)

# 4a Describe -----------------------------------------------------------------
panel(XL, Y2, CW, CH, GREEN)
step(XL + 1.6, Y2 + CH - 1.6, 4, 'Describe the recording',
     'circstudio.analysis', GREEN)
y = Y2 + CH - 10.2
y = group(XL + 2.6, y, 'Rest-activity rhythm', [
    'Interdaily stability, intradaily variability,',
    'relative amplitude (L5, M10), daily profiles,',
    'light exposure summaries'], GREEN)
y = group(XL + 2.6, y, 'Sleep', [
    'Seven sleep-scoring algorithms (Cole-Kripke,',
    'Sadeh, Scripps, Oakley, Crespo, Roenneberg,',
    'Condor), sleep regularity index, sleep',
    'midpoint, wake after sleep onset'], GREEN)
y = group(XL + 2.6, y, 'Signal structure', [
    'Cosinor, singular spectrum analysis,',
    'functional linear modeling, detrended',
    'fluctuation analysis'], GREEN)

# 4b Simulate -----------------------------------------------------------------
panel(XR, Y2, CW, CH, PURPLE)
step(XR + 1.6, Y2 + CH - 1.6, 5, 'Simulate the circadian clock',
     'circstudio.analysis.models', PURPLE)
y = Y2 + CH - 10.2
y = group(XR + 2.6, y, 'Seven published models', [
    'Forger 1999, Jewett 1999, Hannay 2019',
    '(one and two populations), St Hilaire 2007,',
    'Breslow 2013, Skeldon 2023'], PURPLE)
y = group(XR + 2.6, y, 'Predicted', [
    'Dim-light melatonin onset, circadian phase',
    'and amplitude, core body temperature',
    'minimum'], PURPLE)
# small oscillator sketch with onset markers
ox, oy, ow, oh = XR + 4.0, Y2 + 6.6, CW - 8.0, 8.0
tt = np.linspace(0, 3, 400)
osc = np.sin(2 * np.pi * (tt - 0.30))
ax.plot(ox + tt / 3 * ow, oy + (osc + 1) / 2 * oh, color=PURPLE, lw=1.0)
ax.plot([ox, ox + ow], [oy + oh / 2] * 2, color=LIGHTGREY, lw=0.5, zorder=0)
for d in range(3):
    xm = ox + (d + 0.30 + 0.56) / 3 * ow
    ym = oy + (np.sin(2 * np.pi * 0.56) + 1) / 2 * oh
    ax.plot([xm], [ym], marker='v', ms=3.6, color=PURPLE, mec='white', mew=0.4)
ax.text(ox, oy - 2.6, 'Clock state over three days; markers: predicted melatonin onset', fontsize=4.9, color=GREY, va='center')

# =============================================================================
# Row 3: both views on one time axis
# =============================================================================
Y3, H3 = 1.0, Y2 - 7.4 - 1.0
arrow(XL + CW / 2, Y2 - 0.3, XL + CW / 2, Y3 + H3 + 0.3)
arrow(XR + CW / 2, Y2 - 0.3, XR + CW / 2, Y3 + H3 + 0.3)
panel(1.0, Y3, 98.0, H3, GREY)
step(2.6, Y3 + H3 - 1.6, 6, 'Compare both views on the same time axis', None, INK)

tx, ty, tw, th = 5.0, Y3 + 4.0, 90.0, 7.6
t, a = day_trace(3, 'activity')
xs = inset(tx, ty, tw, th, t, a, '#8a8a8a')
for d in range(3):
    # scored rest interval (shaded) and model-predicted melatonin onset (marker)
    r0, r1 = 24 * d + 23.2, 24 * d + 31.5
    x0 = tx + r0 / 72 * tw; x1 = tx + min(r1, 72) / 72 * tw
    ax.add_patch(plt.Rectangle((x0, ty), x1 - x0, th, fc=GREEN, alpha=0.28, lw=0))
    if d == 0:
        ax.add_patch(plt.Rectangle((tx, ty), 7.5 / 72 * tw, th, fc=GREEN,
                                   alpha=0.28, lw=0))
    xm = tx + (24 * d + 21.0) / 72 * tw
    ax.plot([xm, xm], [ty, ty + th + 0.8], color=PURPLE, lw=0.9)
    ax.plot([xm], [ty + th + 1.3], marker='v', ms=3.8, color=PURPLE,
            mec='white', mew=0.4)
for d in range(4):
    ax.text(tx + d * 24 / 72 * tw, ty - 1.5, f'day {d + 1}' if d < 3 else '',
            fontsize=5.0, color=GREY, ha='left', va='center')

# legend, right-aligned on the title line
ly = Y3 + H3 - 3.6
ax.add_patch(plt.Rectangle((56.0, ly - 0.9), 3.0, 1.8, fc=GREEN, alpha=0.35, lw=0))
ax.text(60.0, ly, 'scored rest interval', fontsize=5.4, color=INK, va='center')
ax.plot([74.6], [ly + 0.1], marker='v', ms=3.8, color=PURPLE, mec='white', mew=0.4)
ax.text(76.0, ly, 'predicted melatonin onset', fontsize=5.4, color=INK, va='center')

fig.savefig('figures/fig1_architecture.pdf')
fig.savefig('figures/fig1_architecture.png', dpi=220)
print('ok', fig.get_size_inches())
