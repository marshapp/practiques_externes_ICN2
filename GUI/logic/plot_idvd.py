import pandas as pd
import numpy as np
import matplotlib.cm as cm
import os
import re

cells = {
    'A': 'Pd-Pd',
    'B': 'Pd-Pd',
    'C': 'Pd-Pd',
    'D': 'Pd-Pd',
    'E': 'Ti-Ti',
    'F': 'Ti-Ti',
    'G': 'Ti-Pd',
    'H': 'Ti-Pd',
}

def plot(ax, legend, colormap, filepath, sweep, x_scale, y_scale, current, vg_format, vd_region, absolute_value, fs, lw, ms):

    filename = os.path.splitext(filepath)[0]
    extension = os.path.splitext(filepath)[1]

    if extension == '.xlsx':
        data = pd.read_excel(filepath)
    elif extension == '.csv':
        data = pd.read_csv(filepath)

    pattern = r'([A-Z])(\d+)_(\d+)nm_(?:[A-Z]-?[a-z]?-?_?)*idvd_([\+\-]?\d+)_([\+\-]?\d+)_([\+\-]?\d+)_([\+\-]?\d+)_([\+\-]?\d+)_(\d+\.\d+)_vg_((?:[\+\-]?\d+_?)+)_T_(\d+)K_L_([^_]+)_G_([^_]+)(?:_.*)?$'
    coincidence = re.search(pattern, filename)
    
    if coincidence is None:
        raise ValueError(f"El nombre del archivo no coincide con el patrón esperado: {filename}")

    cell = coincidence.group(1)
    column = coincidence.group(2)
    device = cell + column
    l = int(coincidence.group(3))
    vd_lim = float(coincidence.group(5))
    vd_step = float(coincidence.group(9))
    vg_raw = coincidence.group(10)
    T = int(coincidence.group(11))
    L = coincidence.group(12)
    G = coincidence.group(13)

    vg_values = []
    for i in vg_raw.split('_'):
        vg_values.append(int(i))  

    if vg_format == 'Voltage sweep':
        vg_fin, vg_ini, vg_step = vg_values
        vg = np.arange(vg_ini, vg_fin + vg_step, vg_step)[::-1]
    else:
        vg = vg_values
    
    ix1 = vd_lim / vd_step 
    ix2 = ix1 + 2 * ix1
    ix3 = ix2 + 2 * ix1
    
    sweep_lim = {
        'hysteresis': {'ini': int(ix1) + 1, 'fin': int(ix3) + 3},
        'backward': {'ini': int(ix1) + 1, 'fin': int(ix2) + 3},
        'forward': {'ini': int(ix2) + 1, 'fin': int(ix3) + 3}
    }
    
    ini = sweep_lim[sweep]['ini'] 
    fin = sweep_lim[sweep]['fin']

    vd = data['Smu2.V[1][1]'][ini:fin].to_numpy()
    ids_maxs = []
    ids_mins = []
    igs_maxs = []
    igs_mins = []
    
    color_distribution = np.linspace(0, 1, len(vg))
    colors = [getattr(cm, f"{colormap}")(i) for i in color_distribution]

    for i in range(len(vg)):
        igs = data[f"Smu1.I[{len(vg)-i}][1]"][ini:fin].to_numpy()
        ids = data[f"Smu2.I[{len(vg)-i}][1]"][ini:fin].to_numpy()
        
        if absolute_value:
            ids = np.abs(ids)
            igs = np.abs(igs)

        if vd_region == 'pos':
            mask = (vd >= 0) & (vd <= vd_lim)
        elif vd_region == 'neg':
            mask = (vd <= 0) & (vd >= -vd_lim)
        else:
            mask = np.abs(vd) <= vd_lim

        vd_plot = vd[mask]
        ids_plot = ids[mask]
        igs_plot = igs[mask]

        if current == 'ids':
            current_label = '$I_{DS}$'
        elif current == 'igs':
            current_label = '$I_{GS}$'
        elif current == 'both' and absolute_value == False:
            current_label = '$I_{DS}$ (—), $I_{GS}$ (---)'
        elif current == 'both' and absolute_value == True:
            current_label = '$|I_{DS}|$ (—), $|I_{GS}|$ (---)'
            
        if y_scale == 'log':
            if absolute_value == True and current != 'both':
                ax.set_ylabel(f'|{current_label}| (A)', fontsize=fs)
            else:
                ax.set_ylabel(f'{current_label} (A)', fontsize=fs)
        else: 
            ids_plot *= 1e9
            igs_plot *= 1e9
            if absolute_value:
                ax.set_ylabel(f'|{current_label}| (nA)', fontsize=fs)
            else:
                ax.set_ylabel(f'{current_label} (nA)', fontsize=fs)

        if x_scale == 'log':
            vd_plot = np.abs(vd_plot)
            ids_plot = ids_plot[vd_plot>0]
            igs_plot = igs_plot[vd_plot>0]
            vd_plot = vd_plot[vd_plot>0]
        
        ids_maxs.append(np.max(ids_plot))
        ids_mins.append(np.min(ids_plot))
        igs_maxs.append(np.max(igs_plot))
        igs_mins.append(np.min(igs_plot))
        
        if current == 'ids':
            ax.plot(vd_plot, ids_plot, label=str(vg[::-1][i]), marker='o', markersize=ms, linewidth=lw, color=colors[len(vg)-1-i])
        elif current == 'igs':
            ax.plot(vd_plot, igs_plot, label=str(vg[::-1][i]), marker='o', markersize=ms, linewidth=lw, color=colors[len(vg)-1-i])
        else:
            ax.plot(vd_plot, ids_plot, label=str(vg[::-1][i]), marker='o', markersize=ms, linewidth=lw, color=colors[len(vg)-1-i])
            ax.plot(vd_plot, igs_plot, ls='--', linewidth=lw, marker='o', markersize=ms, color=colors[len(vg)-1-i])

    if x_scale == 'log':
        ax.set_xlim(np.min(vd_plot), vd_lim)
    else:
        if vd_region == 'pos':
            ax.set_xlim(0, vd_lim)
        elif vd_region == 'neg':
            ax.set_xlim(-vd_lim, 0)
        else:
            ax.set_xlim(-vd_lim, vd_lim)

    if x_scale == 'log' and vd_region == 'neg':
        ax.set_xlabel('$|V_{DS}|$ (V)', fontsize=fs)
    else:
        ax.set_xlabel('$V_{DS}$ (V)', fontsize=fs)

    if current == 'ids':
        y_min = np.min(ids_mins)
        y_max = np.max(ids_maxs)
    elif current == 'igs':
        y_min = np.min(igs_mins)
        y_max = np.max(igs_maxs)
    elif current == 'both':
        y_min = min(np.min(igs_mins), np.min(ids_mins))
        y_max = max(np.max(igs_maxs), np.max(ids_maxs))
    
    if y_scale == 'log':
        ids_mins_array = np.array(ids_mins)
        ids_mins_pos = ids_mins_array[ids_mins_array>0]
        y_min = np.min(ids_mins_pos)


    ax.set_ylim(y_min, y_max)

    if x_scale == 'log' and vd_region == 'neg':
        ax.set_title(f"{device} ({cells[cell]}) {l}nm {T}K step={vd_step}V {G} {L} {sweep} {vd_region}", fontsize=fs)
    else:
        ax.set_title(f"{device} ({cells[cell]}) {l}nm {T}K step={vd_step}V {G} {L} {sweep}", fontsize=fs)
    ax.set_xscale(x_scale)
    ax.set_yscale(y_scale)
    if legend == True:    
        if y_scale == 'log':
            legend = ax.legend(title='$V_{GS}$ (V)', loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=fs, frameon=False, ncol=1)
        else:
            if len(vg_values)<4:
                ncol=1
            else:
                ncol=2
            legend = ax.legend(title='$V_{GS}$ (V)', loc='best', fontsize=fs, frameon=True, ncol=ncol)
        legend.get_title().set_fontsize(fs)
    ax.tick_params(labelsize=fs)
    ax.grid(True)
    
    return y_min, y_max

def mean(ax, filepaths, sweep, vg_format, colormap, y_scale, fs, lw, ms, legend, absolute_value):
    
    len_vg = 0
    
    for filepath in filepaths:
        
        filename = os.path.basename(filepath)
        data = pd.read_excel(filepath)
        
        if len_vg == 0:

            pattern = r'([A-Z])(\d+)_(\d+)nm_(?:[A-Z]-?[a-z]?-?_?)*idvd_([\+\-]?\d+)_([\+\-]?\d+)_([\+\-]?\d+)_([\+\-]?\d+)_([\+\-]?\d+)_(\d+\.\d+)_vg_((?:[\+\-]?\d+_?)+)_T_(\d+)K_L_([A-Z]+)_G_([A-Z]+)(?:_.*)?\.xlsx$'
            coincidence = re.search(pattern, filename)
            
            if coincidence:
                cell = coincidence.group(1)
                column = coincidence.group(2)
                device = cell + column
                vg_raw = coincidence.group(10)
                vd_lim = float(coincidence.group(5))
                vd_step = float(coincidence.group(9))
                T = int(coincidence.group(11))
                L = coincidence.group(12)
                G = coincidence.group(13)
                l = int(coincidence.group(3))
                
                vg_values = []
                for i in vg_raw.split('_'):
                    vg_values.append(int(i))  
            
                if vg_format == 'Voltage Sweep':
                    vg_fin, vg_ini, vg_step = vg_values
                    vg = np.arange(vg_ini, vg_fin + vg_step, vg_step)[::-1]
                else:
                    vg = vg_values
            else:
                print("Filename doesn't meet the requirements")
        else: continue
    
        len_vg = len(vg)    
    
        ix1 = vd_lim / vd_step 
        ix2 = ix1 + 2 * ix1
        ix3 = ix2 + 2 * ix1
        
        sweep_lim = {
            'hysteresis': {'ini': int(ix1) + 1, 'fin': int(ix3) + 3},
            'backward': {'ini': int(ix1) + 1, 'fin': int(ix2) + 3},
            'forward': {'ini': int(ix2) + 1, 'fin': int(ix3) + 3}
        }
        
        ini = sweep_lim[sweep]['ini'] 
        fin = sweep_lim[sweep]['fin']
        
        
        cells = {
            'A': 'Pd-Pd',
            'B': 'Pd-Pd',
            'C': 'Pd-Pd',
            'D': 'Pd-Pd',
            'E': 'Ti-Ti',
            'F': 'Ti-Ti',
            'G': 'Ti-Pd',
            'H': 'Ti-Pd',
        }
        
        vd = data['Smu2.V[1][1]'][ini:fin].to_numpy()
        ids_maxs = []
        ids_mins = []
        
        color_distribution = np.linspace(0, 1, len_vg)
        colors = [getattr(cm, f"{colormap}")(i) for i in color_distribution]
    
    rows = len(filepaths) * len_vg
    cols = len(vd)
    
    matriz = np.zeros((rows, cols))
    
    row = 0
    for i in range(len_vg):
        for filepath in filepaths:
            data = pd.read_excel(filepath)
            ids = data[f"Smu2.I[{len_vg-i}][1]"][ini:fin].to_numpy()
            if absolute_value:
                ids = np.abs(ids)
            matriz[row, :] = ids
            row += 1
    
    for i in range(len_vg):
        grupo = matriz[i*len(filepaths):i*len(filepaths)+len(filepaths), :]
        mean = np.mean(grupo, axis=0)
        std = np.std(grupo, axis=0)
        
        if absolute_value == True:
            if y_scale == 'log':
                if absolute_value:
                    ax.set_ylabel("$|I_{DS}|$ (A)", fontsize=fs)
            else: 
                mean *= 1e9
                std *= 1e9
                ax.set_ylabel("$|I_{DS}|$ (nA)", fontsize=fs)
        else:
            mean *= 1e9
            std *= 1e9
            ax.set_ylabel("$I_{DS}$ (nA)", fontsize=fs)
        
        ids_maxs.append(np.max(mean+std))
        ids_mins.append(np.min(mean-std))
        
        ax.plot(vd, mean, label=str(vg[::-1][i]), linewidth=lw, marker='o', markersize=ms, color=colors[len_vg-1-i])
        ax.fill_between(vd, mean - std, mean + std, color=colors[len_vg-1-i], alpha = 0.2)
    
    
    y_max = np.max(ids_maxs) #SHAURIA DE FER TMHB PEL MAX....
    
    if y_scale == 'log':
        ids_mins_array = np.array(ids_mins)
        ids_mins_pos = ids_mins_array[ids_mins_array>0]
        y_min = np.min(ids_mins_pos)
    else:
        y_min = np.min(ids_mins)
        


    ax.set_ylim(y_min, y_max)
    
    ax.set_xlabel('$V_{DS}$ (V)', fontsize=fs)
    ax.set_title(f"{cells[cell]} {l}nm {T}K step={vd_step}V {G} {L} {sweep}", fontsize=fs)
    ax.set_yscale(y_scale)
    ax.set_xlim(-vd_lim, vd_lim)
    if legend == True:    
        if y_scale == 'log':
            legend = ax.legend(title='$V_{GS}$ (V)', loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=fs, frameon=False, ncol=1)
        else:
            if len_vg<4:
                ncol=1
            else:
                ncol=2
            legend = ax.legend(title='$V_{GS}$ (V)', loc='best', fontsize=fs, frameon=True, ncol=ncol)
        legend.get_title().set_fontsize(fs)
    ax.tick_params(labelsize=fs)
    ax.grid(True)
    
    return y_min, y_max
        
            
            
            
            
        
    
    
