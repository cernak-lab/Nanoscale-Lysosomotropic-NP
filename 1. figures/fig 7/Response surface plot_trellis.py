# =========================================================
# Trellis 2×2: Loewe (same-axis) + Emax analytic surfaces
# Reagent fixed at REAGENT_MOL_PCT of assay concentration
# with a full-height colorbar
# Author: Yu-Ting Kao | Final 2025-11 version
# =========================================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.colors import Normalize
from mpl_toolkits.axes_grid1 import make_axes_locatable

# ----------------------------
# Global settings
# ----------------------------
ASSAY_CONC_uM   = 5.0        # test concentration (µM)
HILL            = 1.0        # Hill coefficient for Emax
REAGENT_MOL_PCT = 5.0        # reagent loading (mol%)
XMIN_NM, XMAX_NM = 1e1, 1e5  # Product IC50 axis range (nM)
YMIN_PCT, YMAX_PCT = 0, 100  # Yield axis (%)
GRID_N          = 500        # grid resolution

plt.rc('font', family='Arial', size=10)
CMAP = 'plasma'
NORM = Normalize(vmin=0, vmax=100)

ASSAY_CONC_nM = ASSAY_CONC_uM * 1000.0
REAGENT_CONC_nM = ASSAY_CONC_nM * (REAGENT_MOL_PCT / 100.0)  # fixed per well

# ----------------------------
# Loewe + Emax helper
# ----------------------------
def loewe_emax_same_axis(prod_C, prod_IC50,
                         sm_C=None, sm_IC50=None,
                         extra_C=None, extra_IC50=None,
                         hill=1.0):
    """Loewe additivity with Emax single-agent saturation."""
    if abs(hill - 1.0) < 1e-12:
        S = prod_C / prod_IC50
        if (sm_C is not None) and (sm_IC50 is not None):
            S += sm_C / sm_IC50
        if (extra_C is not None) and (extra_IC50 is not None):
            S += extra_C / extra_IC50
        return 100.0 * (S / (1.0 + S))
    else:
        S = (prod_C / prod_IC50)**hill
        if (sm_C is not None) and (sm_IC50 is not None):
            S += (sm_C / sm_IC50)**hill
        if (extra_C is not None) and (extra_IC50 is not None):
            S += (extra_C / extra_IC50)**hill
        return 100.0 * (S / (1.0 + S))

# ----------------------------
# Surface builder
# ----------------------------
def build_surface(sm_ic50_uM=None, reagent_ic50_uM=None):
    """Create analytic surface for one condition."""
    x_vals = np.logspace(np.log10(XMIN_NM), np.log10(XMAX_NM), GRID_N)
    y_vals = np.linspace(YMIN_PCT, YMAX_PCT, GRID_N)
    x_mesh, y_mesh = np.meshgrid(x_vals, y_vals)

    # Concentrations in-well
    prod_conc = ASSAY_CONC_nM * (y_mesh / 100.0)          # product fraction
    sm_conc = sm_IC50_nM = None
    if sm_ic50_uM is not None:
        sm_conc    = ASSAY_CONC_nM * (1.0 - y_mesh / 100.0)
        sm_IC50_nM = sm_ic50_uM * 1000.0

    extra_conc = extra_IC50_nM = None
    if reagent_ic50_uM is not None:
        extra_conc    = REAGENT_CONC_nM                   # fixed amount per well
        extra_IC50_nM = reagent_ic50_uM * 1000.0

    z = loewe_emax_same_axis(prod_conc, x_mesh,
                             sm_conc, sm_IC50_nM,
                             extra_conc, extra_IC50_nM,
                             hill=HILL)
    return x_mesh, y_mesh, np.clip(z, 0, 100)

# ----------------------------
# Define the four conditions
# ----------------------------
panels = [
    ("Inactive SM",                     None,  None),
    ("Active SM (IC50 = 1 µM)",         1.0,   None),
    ("Active SM (IC50 = 5 µM)",         5.0,   None),
    ("ActiveSM 5 µM + Bioactive Reagent 1 µM (5 mol%)", 5.0, 1),
]
surfaces = [build_surface(sm, rg) for _, sm, rg in panels]

# ----------------------------
# Plot 2×2 grid
# ----------------------------

# Adjust subplot margins and vertical spacing
fig.subplots_adjust(left=0.10, right=0.88, top=0.93, bottom=0.10, hspace=0.4, wspace=0.1)

fig, axs = plt.subplots(2, 2, figsize=(12, 10))

def sci(x, pos):
    return f'$10^{{{int(np.log10(x))}}}$' if x > 0 else '0'

for ax, (title, _, _), (x_mesh, y_mesh, z_grid) in zip(axs.ravel(), panels, surfaces):
    pcm = ax.pcolormesh(x_mesh, y_mesh, z_grid,
                        cmap=CMAP, shading='auto', norm=NORM)
    ax.set_xscale('log')
    ax.set_xlim(XMIN_NM, XMAX_NM)
    ax.set_ylim(YMIN_PCT, YMAX_PCT)
    ax.xaxis.set_major_formatter(FuncFormatter(sci))
    ax.set_xlabel('Product IC50 (nM)')
    ax.set_ylabel('Yield (%)')
    ax.set_title(title)

# ----------------------------
# Add one full-height colorbar
# ----------------------------
# adjust right margin to leave space for colorbar
fig.subplots_adjust(right=0.88)
# [left, bottom, width, height] in figure coordinates
cbar_ax = fig.add_axes([0.90, 0.11, 0.02, 0.77])
cb = fig.colorbar(pcm, cax=cbar_ax)
cb.set_label('D2B Activity (%)')

# ----------------------------
# Global title & show
# ----------------------------
plt.suptitle(
    f'D2B Total Activity @ {ASSAY_CONC_uM:g} µM (Loewe + Emax; Hill={HILL:g}; Reagent={REAGENT_MOL_PCT:g} mol% fixed)',
    fontsize=14, y=0.95
)

# Optional save
plt.savefig('Trellis_2D_LoeweEmax_fixedReagent_reagetn1µM-2.png',dpi=300, bbox_inches='tight')
plt.show()





