import os, re
import numpy as np
import pandas as pd
from matplotlib import cm

def plot(ax, legend, colormap, filepath, y_scale, current, absolute_value, fs, lw, ms):

    filename = os.path.splitext(filepath)[0]
    extension = os.path.splitext(filepath)[1]

    if extension == '.xlsx':
        data = pd.read_excel(filepath)
    elif extension == '.csv':
        data = pd.read_csv(filepath)

    pattern = r'([A-Z])(\d+)_(\d+)nm_idtime_vg_([\+\-]?\d+)_vd_([\+\-]?\d+)_T_(\d+)K_L_([^_]+)_G_([^_]+)(?:_.*)?$'
    coincidence = re.search(pattern, os.path.basename(filename))

    if coincidence:
        cell = coincidence.group(1)
        column = coincidence.group(2)
        device = cell + column
        l = int(coincidence.group(3))
        vg = float(coincidence.group(4))
        vd = float(coincidence.group(5))
        T = int(coincidence.group(6))
        L = coincidence.group(7)
        G = coincidence.group(8)

    ids = data['Smu2.I[1][1]'].to_numpy()
    igs = data['Smu1.I[1][1]'].to_numpy()

    if absolute_value:
        ids = np.abs(ids)
        igs = np.abs(igs)

    time = data['Smu2.Time[1][1]'].to_numpy()

    if y_scale == 'log':
        ylabel_ids = f"$|I_{{DS}}|$ (A)" if absolute_value else "$I_{DS}$ (A)"
        ylabel_igs = f"$|I_{{GS}}|$ (A)" if absolute_value else "$I_{GS}$ (A)"
    else:
        ids *= 1e9
        igs *= 1e9
        ylabel_ids = f"$|I_{{DS}}|$ (nA)" if absolute_value else "$I_{DS}$ (nA)"
        ylabel_igs = f"$|I_{{GS}}|$ (nA)" if absolute_value else "$I_{GS}$ (nA)"

    color = getattr(cm, colormap)(0.5)

    if current == 'ids':
        ax.plot(time, ids, linewidth=lw, marker='o', markersize=ms, color=color,
                label=f'{str(int(vg)) if vg.is_integer() else str(vg)},  {str(int(vd)) if vd.is_integer() else str(vd)}')
        ax.set_ylabel(ylabel_ids, fontsize=fs)
        y_min, y_max = ids.min(), ids.max()
    elif current == 'igs':
        ax.plot(time, igs, linewidth=lw, marker='o', markersize=ms, color=color,
                label=f'{str(int(vg)) if vg.is_integer() else str(vg)},  {str(int(vd)) if vd.is_integer() else str(vd)}')
        ax.set_ylabel(ylabel_igs, fontsize=fs)
        y_min, y_max = igs.min(), igs.max()
    else:  
        ax.plot(time, ids, linewidth=lw, marker='o', markersize=ms, color=color,
                label=f'{str(int(vg)) if vg.is_integer() else str(vg)},  {str(int(vd)) if vd.is_integer() else str(vd)}')
        ax.plot(time, igs, ls='--', linewidth=lw, marker='o', markersize=ms, color=color)
        ax.set_ylabel("Corrientes", fontsize=fs)
        y_min = min(ids.min(), igs.min())
        y_max = max(ids.max(), igs.max())

    ax.set_xlabel("Time (s)", fontsize=fs)
    ax.set_title(f"{device} {l}nm {T}K {G} {L}", fontsize=fs)
    ax.set_yscale(y_scale)

    if y_scale == 'log':
        y_min = max(y_min, np.min([val for val in [ids.min(), igs.min()] if val > 0]))
    ax.set_ylim(y_min, y_max)

    ax.set_xlim(time.min(), time.max())

    ax.tick_params(labelsize=fs)
    ax.grid(True)

    if legend:
        legend = ax.legend(title="$V_{GS}, V_{DS}$ (V)", fontsize=fs)
        legend.get_title().set_fontsize(fs)

    return y_min, y_max