"""Schematic of the light-driven pacemaker models implemented in circStudio,
after the two-process formulation of Kronauer and colleagues.

Light acts on a pool of photoreceptors (Process L), which sends a drive B to a
limit-cycle oscillator (Process P). Markers of circadian timing are read from
the state of the oscillator.

The curves are not illustrations: the phase-plane trajectory and the lower
trace are a simulation of circStudio's ``Forger`` model under the light
schedule drawn in the "Light" box, started from a small amplitude.

Authored at the GigaByte text width (397 pt = 5.51 in) so that
\\includegraphics[width=\\textwidth] does not rescale it.

Run from the ``paper`` directory:  python scripts/figure_pacemaker_schematic.py
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

import circstudio as cs

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8,
                     'mathtext.fontset': 'dejavusans',
                     'pdf.fonttype': 42})

INK = '#1b1b1b'; GREY = '#6e6e6e'; LIGHTGREY = '#b9b9b9'
BLUE = '#2c6fbb'; ORANGE = '#c8641f'; PURPLE = '#7a4fa0'; YELLOW = '#e0a526'
FILL = {BLUE: '#eaf1fa', ORANGE: '#fcefe4', PURPLE: '#f1ebf7',
        YELLOW: '#fdf6e3'}

# ----------------------------------------------------------------------------
# Simulation: Forger model, 16 h of light (500 lux, 07:00-23:00) and 8 h of
# darkness, 15 days, started close to the origin of the phase plane.
# ----------------------------------------------------------------------------
DT = 1 / 6                                  # hours
LIGHT_ON, LIGHT_OFF, LUX = 7.0, 23.0, 500.0
N_DAYS = 15                                 # the last 2.5 days are shown

time = np.arange(0, 24 * N_DAYS, DT)
hour = time % 24
light = np.where((hour >= LIGHT_ON) & (hour < LIGHT_OFF), LUX, 0.0)

model = cs.Forger(inputs=light, time=time,
                  initial_condition=np.array([0.15, 0.0, 0.0]))
x, xc = model.model_states[:, 0], model.model_states[:, 1]
cbtmin = model.cbt()                        # hours since start
dlmo = model.dlmos()                        # hours since start

# ----------------------------------------------------------------------------
# Canvas
# ----------------------------------------------------------------------------
W, H = 100.0, 70.0
fig = plt.figure(figsize=(5.51, 5.51 * H / W))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis('off')


def panel(x0, y0, w, h, c):
    ax.add_patch(FancyBboxPatch((x0, y0), w, h,
                                boxstyle='round,pad=0,rounding_size=1.5',
                                fc=FILL[c], ec=c, lw=0.9))


def heading(x0, y0, title, subtitle, c):
    ax.text(x0, y0, title, ha='left', va='top', fontsize=7.8,
            fontweight='bold', color=c)
    ax.text(x0, y0 - 3.6, subtitle, ha='left', va='top', fontsize=5.6,
            color=GREY)


def arrow(x1, y1, x2, y2, c=GREY, style='-|>', ls='-', rad=0.0, lw=0.9):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=7, lw=lw, color=c, ls=ls,
                                 connectionstyle=f'arc3,rad={rad}',
                                 shrinkA=0, shrinkB=0))


def inset(x0, y0, w, h):
    """Axes placed in canvas units."""
    return fig.add_axes([x0 / W, y0 / H, w / W, h / H])


TOP, BOT = 67.0, 31.0          # top row of panels
PH = TOP - BOT

# ---- Light ------------------------------------------------------------------
LX, LW = 2.0, 15.0
panel(LX, BOT, LW, PH, YELLOW)
heading(LX + 1.8, TOP - 2.0, 'Light', 'intensity $I(t)$', YELLOW)
a = inset(LX + 2.0, BOT + 9.0, LW - 4.0, 9.0)
two_days = time < 48
a.fill_between(time[two_days], light[two_days], step='post', color=YELLOW,
               lw=0, alpha=0.85)
a.set_xlim(0, 48); a.set_ylim(0, LUX * 1.15)
a.set_xticks([0, 24, 48]); a.set_xticklabels(['0', '24', '48'], fontsize=4.8)
a.set_yticks([])
a.tick_params(length=2, width=0.5, pad=1.5, colors=GREY)
for s in ('top', 'right', 'left'):
    a.spines[s].set_visible(False)
a.spines['bottom'].set_color(LIGHTGREY); a.spines['bottom'].set_linewidth(0.6)
a.patch.set_alpha(0)
ax.text(LX + LW / 2, BOT + 4.2, 'time (h)', ha='center', va='center',
        fontsize=4.8, color=GREY)
ax.text(LX + LW / 2, BOT + 21.5, f'{LUX:.0f} lux for 16 h,\ndark for 8 h',
        ha='center', va='center', fontsize=5.2, color=GREY, linespacing=1.3)

# ---- Process L --------------------------------------------------------------
PLX, PLW = 22.0, 35.0
panel(PLX, BOT, PLW, PH, ORANGE)
heading(PLX + 1.8, TOP - 2.0, 'Process L',
        'light acts on a pool of photoreceptors', ORANGE)

R = 5.8
cy = BOT + 14.0
c_ready = (PLX + 8.6, cy)
c_used = (PLX + PLW - 8.6, cy)
for (cx, cyy), name, frac in ((c_ready, 'ready', 'fraction $1-n$'),
                              (c_used, 'used', 'fraction $n$')):
    ax.add_patch(Circle((cx, cyy), R, fc='white', ec=ORANGE, lw=1.0))
    ax.text(cx, cyy + 1.3, name, ha='center', va='center', fontsize=6.2,
            color=INK)
    ax.text(cx, cyy - 1.9, frac, ha='center', va='center', fontsize=5.0,
            color=GREY)

# activation (ready -> used) and recovery (used -> ready)
arrow(c_ready[0] + 3.2, cy + R - 0.2, c_used[0] - 3.2, cy + R - 0.2,
      c=ORANGE, rad=-0.38)
arrow(c_used[0] - 3.2, cy - R + 0.2, c_ready[0] + 3.2, cy - R + 0.2,
      c=GREY, rad=-0.38)
mid = PLX + PLW / 2
ax.text(mid, cy + R + 5.0, r'activated by light, rate $\alpha(I)$',
        ha='center', va='center', fontsize=5.6, color=ORANGE)
ax.text(mid, cy - R - 5.0, r'recovery, rate $\beta$', ha='center',
        va='center', fontsize=5.6, color=GREY)

# ---- Process P --------------------------------------------------------------
PPX, PPW = 63.0, 35.0
panel(PPX, BOT, PPW, PH, BLUE)
heading(PPX + 1.8, TOP - 2.0, 'Process P',
        'circadian pacemaker: a limit-cycle oscillator', BLUE)
ax.text(PPX + 1.8, TOP - 8.6,
        'Each point is the state of the clock at one\n'
        'moment, given by two numbers, $x$ and $x_c$.\n'
        'It travels round the loop once a day.',
        ha='left', va='top', fontsize=5.0, color=INK, linespacing=1.25)

SIDE = 16.5
p = inset(PPX + 2.6, BOT + 2.4, SIDE, SIDE)
settled = time >= 24 * (N_DAYS - 2.5)
p.plot(x[~settled], xc[~settled], color=LIGHTGREY, lw=0.6)
p.plot(x[settled], xc[settled], color=BLUE, lw=1.4)
p.plot(x[0], xc[0], 'o', ms=2.2, color=GREY)
last = np.flatnonzero(time >= 24 * (N_DAYS - 1))
j = last[np.argmin(x[last])]
p.plot(x[j], xc[j], 'v', ms=3.6, color=BLUE, zorder=5)
k = last[np.argmax(xc[last])]                       # direction of travel
p.annotate('', xy=(x[k + 9], xc[k + 9] + 0.2), xytext=(x[k - 9], xc[k - 9] + 0.2),
           arrowprops=dict(arrowstyle='->', color=BLUE, lw=0.8,
                           mutation_scale=6))
lim = 1.45
p.set_xlim(-lim, lim); p.set_ylim(-lim, lim); p.set_aspect('equal')
p.axhline(0, color=LIGHTGREY, lw=0.5, zorder=0)
p.axvline(0, color=LIGHTGREY, lw=0.5, zorder=0)
p.set_xticks([]); p.set_yticks([])
for s in p.spines.values():
    s.set_visible(False)
p.patch.set_alpha(0)
p.text(lim, -0.02, '$x$', ha='right', va='top', fontsize=6.0, color=GREY)
p.text(-0.08, -lim, '$x_c$', ha='right', va='bottom', fontsize=6.0,
       color=GREY)

tx = PPX + SIDE + 6.6
rows = [BOT + 16.6, BOT + 13.0, BOT + 9.0, BOT + 4.4]
ax.plot([tx - 1.3], [rows[0]], 'o', ms=2.2, color=GREY)
ax.text(tx, rows[0], 'start', ha='left', va='center', fontsize=5.0,
        color=GREY)
ax.plot([tx - 2.2, tx - 0.5], [rows[1]] * 2, color=LIGHTGREY, lw=0.8)
ax.text(tx, rows[1], 'first days', ha='left', va='center', fontsize=5.0,
        color=GREY)
ax.plot([tx - 2.2, tx - 0.5], [rows[2] + 0.9] * 2, color=BLUE, lw=1.4)
ax.text(tx, rows[2], 'stable rhythm,\none lap = 24 h', ha='left', va='center',
        fontsize=5.0, color=BLUE, linespacing=1.2)
ax.plot([tx - 1.3], [rows[3] + 0.9], 'v', ms=3.6, color=BLUE)
ax.text(tx, rows[3], 'temperature\nminimum', ha='left', va='center',
        fontsize=5.0, color=INK, linespacing=1.2)

# ---- Links between the top panels ------------------------------------------
ym = cy
arrow(LX + LW, ym, PLX, ym, c=GREY)
arrow(PLX + PLW, ym, PPX, ym, c=GREY)
ax.text((PLX + PLW + PPX) / 2, ym + 2.4, '$B$', ha='center', va='center',
        fontsize=6.6, color=INK)
ax.text((LX + LW + PLX) / 2, ym + 2.4, '$I$', ha='center', va='center',
        fontsize=6.6, color=INK)

# what the drive depends on, in words (the equations are in the caption)
EQ = BOT - 3.2
ax.text(PLX + PLW / 2, EQ,
        'the drive $B$ is stronger in brighter light and\n'
        'when more photoreceptors are ready',
        ha='center', va='center', fontsize=5.4, color=INK, linespacing=1.25)
ax.text(PPX + PPW / 2 - 2.5, EQ,
        'the effect of light depends on where the\n'
        'clock is on its loop (evening light delays,\n'
        'morning light advances)',
        ha='center', va='center', fontsize=5.4, color=BLUE, linespacing=1.25)
arrow(PPX + 3.0, BOT, (PLX + PLW + PPX) / 2, ym - 1.0, c=BLUE, ls=(0, (2.5, 2)),
      rad=-0.25, lw=0.8)

# ---- Predicted markers ------------------------------------------------------
MY, MH = 2.0, 19.5
panel(2.0, MY, 96.0, MH, PURPLE)
heading(3.8, MY + MH - 1.8, 'Predicted markers',
        'read from the state of the pacemaker', PURPLE)
arrow(PPX + PPW - 2.6, BOT, PPX + PPW - 2.6, MY + MH, c=GREY)

m = inset(36.0, MY + 5.8, 59.0, 10.2)
t0 = 24 * (N_DAYS - 2.5)                    # noon, 2.5 days before the end
sel = (time >= t0) & (time <= t0 + 48)
ts = time[sel] - t0
dark = light[sel] == 0
m.fill_between(ts, -1.6, 1.6, where=dark, step='post', color='#d9d9d9',
               lw=0, alpha=0.8)
m.plot(ts, x[sel], color=BLUE, lw=1.2)
for c0 in cbtmin[(cbtmin >= t0) & (cbtmin <= t0 + 48)]:
    i = int(round((c0 - t0) / DT))
    m.plot(c0 - t0, x[sel][i], 'v', ms=3.6, color=BLUE)
for d0 in dlmo[(dlmo >= t0) & (dlmo <= t0 + 48)]:
    m.axvline(d0 - t0, ymin=0.08, ymax=0.92, color=ORANGE, lw=1.1)
m.set_xlim(0, 48); m.set_ylim(-1.6, 1.6)
ticks = np.arange(0, 49, 6)
m.set_xticks(ticks)
m.set_xticklabels([f'{int((h + 12) % 24):02d}:00' for h in ticks],
                  fontsize=4.8)
m.set_yticks([])
m.tick_params(length=2, width=0.5, pad=1.5, colors=GREY)
for s in ('top', 'right', 'left'):
    m.spines[s].set_visible(False)
m.spines['bottom'].set_color(LIGHTGREY); m.spines['bottom'].set_linewidth(0.6)
m.patch.set_alpha(0)
m.text(-0.8, x[sel][0], '$x$', ha='right', va='center', fontsize=6.0,
       color=BLUE)

# legend for the markers
lx, ly = 4.2, MY + 10.2
ax.plot([lx + 0.8], [ly], 'v', ms=3.6, color=BLUE)
ax.text(lx + 2.6, ly, 'core body temperature\nminimum (minimum of $x$)',
        ha='left', va='center', fontsize=5.2, color=INK, linespacing=1.2)
ax.plot([lx + 0.8] * 2, [ly - 6.3, ly - 3.9], color=ORANGE, lw=1.1)
ax.text(lx + 2.6, ly - 5.1, 'dim-light melatonin onset\n(placed 7 h earlier)', ha='left',
        va='center', fontsize=5.2, color=INK, linespacing=1.2)
ax.text(65.5, MY + 2.3, 'clock time over two days; grey bands: darkness',
        ha='center', va='center', fontsize=4.8, color=GREY)

fig.savefig('figures/fig_pacemaker_schematic.pdf')
fig.savefig('figures/fig_pacemaker_schematic.png', dpi=220)
