import pandas as pd
import numpy as np
import matplotlib.cm as cm

from scipy.stats import linregress
import os
import re

from scipy.ndimage import gaussian_filter1d

def find_closest(col, rs):
    dist = abs(col - rs)
    return np.argmin(dist)

import warnings
warnings.filterwarnings('ignore')
    
sweeps = {
    'backward': {'linreg': [True, False], 'ini': 61, 'fin': 182, 'ini_fit': 100,'fin_fit': 120},
    'forward': {'linreg': [True, False], 'ini': 182, 'fin': 303, 'ini_fit': 0,'fin_fit': 4},
    'hysteresis': {'linreg': [False], 'ini': 61, 'fin': 303, 'ini_fit': None,'fin_fit': None}
}

ab_val = {
    True: {
        'transform': lambda Ids: np.abs(Ids),
        'ylab_abs': '|'
    },
    False: {
        'transform': lambda Ids: Ids,
        'ylab_abs': ''
    }
    }

y_scale = {
   'linear': {
        'transform': lambda Ids: Ids * 1e9,
        'ylab_units': 'nA',
        'ymin': lambda x: np.min(x),
        'ymax': lambda x: np.max(x)
    },
    'log': {
        'transform': lambda Ids: Ids,
        'ylab_units': 'A',
        'ymin':lambda x: (
        np.min(pos_vals) if (pos_vals := np.array(x)[np.array(x) > 0]).size > 0 
        else 1e-15 ),
        'ymax': lambda x: np.max(x)
    } 
}

linreg_sqrt = {
    True: '$^{1/2}$',
    False: ''
}

norm = {
    True: {
        'transform': lambda Ids: Ids / np.max(np.abs(Ids)),
        'ylab_units': lambda ysc, lr: 'arb. units'
    },
    False: {
        'transform': lambda Ids: Ids,
        'ylab_units': lambda ysc, lr: f"{y_scale[ysc]['ylab_units']}{linreg_sqrt[lr]}"
    }
}

contacts = {
        'A': 'Pd-Pd',
        'B': 'Pd-Pd',
        'C': 'Pd-Pd',
        'D': 'Pd-Pd',
        'E': 'Ti-Ti',
        'F': 'Ti-Ti',
        'G': 'Ti-Pd',
        'H': 'Ti-Pd',
    }

Igs_plot_opt = {
    'Ids': {'Ids_plot': True, 'ls_Ids': '-', 'lab_Ids': lambda lab: lab,
            'Igs_plot': False, 'ls_Igs': None, 'lab_Igs': lambda lab: None,
        'ylab_name': lambda ab, lr: f"${ab_val[ab]['ylab_abs']}I_{{DS}}{ab_val[ab]['ylab_abs']}{linreg_sqrt[lr].strip('$')}$"
    },
    'Igs': {'Ids_plot': False, 'ls_Ids': None, 'lab_Ids': lambda lab: None,
            'Igs_plot': True,'ls_Igs': '-', 'lab_Igs': lambda lab: lab,
        'ylab_name': lambda ab, lr: f"${ab_val[ab]['ylab_abs']}I_{{GS}}{ab_val[ab]['ylab_abs']}{linreg_sqrt[lr].strip('$')}$"
    }
}

Igs_plot_opt['Both'] = {'Ids_plot': True,'ls_Ids': '-', 'lab_Ids': lambda lab: lab,
                        'Igs_plot': True,'ls_Igs': ':', 'lab_Igs': lambda lab: None,
    'ylab_name': lambda ab, lr: f"{Igs_plot_opt['Ids']['ylab_name'](ab, lr)} (—), {Igs_plot_opt['Igs']['ylab_name'](ab, lr)} ($\\cdot \\cdot \\cdot$)"
}




def idvg_fileinfo(filepath):
    filename = os.path.basename(filepath)
    match = re.search(r'^([A-Z])(\d)_(\d+)nm.*_vd_((?:-?[\d\.]+_)+)T_(\d+)K_L_([^_]+)_G_([^_]+)_', filename)
    
    if not match:
        raise ValueError(f"Filename does not match expected format: {filename}")

    dev_letter = match.group(1)
    dev_number = match.group(2)
    device = dev_letter + dev_number
    contact = contacts[dev_letter]

    l = int(match.group(3))
    vds_str = match.group(4)
    vds_values = [float(v) for v in vds_str.strip('_').split('_')]
    vds_values.sort()
    # .strip('_') removes all leading and trailing '_'
    # .split('_') cuts at each '_' and returns the parts in a list
    t = int(match.group(5))

    light = match.group(6)
    gas = match.group(7)
    
    return filename, dev_letter, dev_number, device, contact, l, t, vds_values, light, gas

def readexcel_at_vd(data, vd, ini, fin, read_Igs):
    mask = (data['Smu2.V[1][1]'] == vd)
    data_vd = data.loc[mask]
    Vgs = data_vd['Smu1.V[1][1]'][ini:fin].to_numpy()
    Ids = data_vd['Smu2.I[1][1]'][ini:fin].to_numpy().astype(np.float64)
    if read_Igs:
        Igs = data_vd['Smu1.I[1][1]'][ini:fin].to_numpy()
        return Vgs, Ids, Igs
    else:
        return Vgs, Ids


def idvg_plot(ax, filepath, s, ab, ysc, nrm, linreg, Igs_plot, fs, lw, ms, colormap, legend, smoothing, sgm=2, al=0.7):
    
    s_config = sweeps[s]
    ysc_config = y_scale[ysc]
    ab_config = ab_val[ab]
    norm_config = norm[nrm]
    Igs_plot_config = Igs_plot_opt[Igs_plot]

    transform_ab = ab_config['transform']
    transform_norm = norm_config['transform']
    transform_ysc = ysc_config['transform']
    
    ini, fin = s_config['ini'], s_config['fin']
    ini_fit, fin_fit = s_config['ini_fit'], s_config['fin_fit']
        
    filename, dev_letter, dev_number, device, contact, l, t, vds_values, light, gas = idvg_fileinfo(filepath)
    
    cc = np.linspace(0, 1, len(vds_values))
    if isinstance(colormap, str):
        if colormap == 'Default':
            colors = [cm.jet(x) for x in cc][::-1]
        else:
            cmap = getattr(cm, colormap)
            colors = [cmap(x) for x in cc][::-1]
    else:
        colors = [colormap(x) for x in cc][::-1]
    
    data = pd.read_excel(filepath)
    I_maxs, I_mins = [], []
    
    for vdx, vd in enumerate(vds_values):
        plot_label = str(int(vd)) if vd.is_integer() else str(vd)
        Vgs, Ids, Igs = readexcel_at_vd(data, vd, ini, fin, True)
        Ids = transform_norm(transform_ysc(transform_ab( Ids )))
        Igs = transform_norm(transform_ysc(transform_ab( Igs )))
        
        if Igs_plot_config['Igs_plot']:
            ax.plot(Vgs, Igs, label=Igs_plot_config['lab_Igs'](plot_label), linewidth=lw, marker='o', markersize=ms, ls=Igs_plot_config['ls_Igs'], color=colors[vdx])
            I_maxs.append(np.max(Igs))
            I_mins.append(np.min(Igs))
            
        if Igs_plot_config['Ids_plot']:
            
            if linreg:
                Ids = np.sqrt(np.abs((Ids)))
                x, y = Vgs[ini_fit:fin_fit], Ids[ini_fit:fin_fit]
                slope, intercept, *_ = linregress(x, y)
                Vth = -intercept/slope
                Vgs_fit = np.linspace(min(x), Vth, 100)
                Ids_fit = slope * Vgs_fit + intercept
                ax.plot(Vgs_fit, Ids_fit, color=colors[vdx], ls='--')
                plot_label += ', ' + str(round(Vth, 1))
                
            if smoothing:
                ax.scatter(Vgs, Ids, marker='o', s=ms, color=colors[vdx], alpha=1)
                Ids_sm = gaussian_filter1d(Ids, sigma=sgm)
                ax.plot(Vgs, Ids_sm, label=Igs_plot_config['lab_Ids'](plot_label), linewidth=lw, ls=Igs_plot_config['ls_Ids'], color=colors[vdx], alpha=al)
            else:
                ax.plot(Vgs, Ids, label=Igs_plot_config['lab_Ids'](plot_label), linewidth=lw, marker='o', markersize=ms, ls=Igs_plot_config['ls_Ids'], color=colors[vdx])
            I_maxs.append(np.max(Ids))
            I_mins.append(np.min(Ids))
            
    
    ax.set_title(f'{device} ({contact}) {l}nm {t}K step=0.5V {light} {gas} {s}', fontsize=fs)
    ax.set_xlabel('$V_{GS}$ (V)', fontsize=fs)
    ax.set_xlim(-30, 30)
    
    ylab_symbol = Igs_plot_config["ylab_name"](ab, linreg)
    ylab_units = norm_config["ylab_units"](ysc, linreg)
    ylab = f'{ylab_symbol} ({ylab_units})'
    ax.set_ylabel(ylab, fontsize=fs)
    y_min = ysc_config['ymin'](I_mins)
    y_max = ysc_config['ymax'](I_maxs)
    ax.set_ylim(y_min, y_max)
    ax.set_yscale(ysc)
    
    ax.tick_params(labelsize=fs)
    ax.grid(True)
    
    leg_title = '$V_{DS}$'
    if linreg:
        leg_title += ', $V_{th}$'
    leg_title += ' (V)'
    
        
    if legend == True:
        if ysc == 'log':
            legend = ax.legend(title=leg_title, loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=fs, frameon=False, ncol=1)
        else:
            if len(vds_values)<4:
                ncol=1
            else:
                ncol=2
            legend = ax.legend(title=leg_title, loc='best', fontsize=fs, frameon=True, ncol=ncol)

        legend.get_title().set_fontsize(fs)
    
    return y_min, y_max







def idvg_alldevs_mean_plot(ax, filepaths, s, ab, ysc, fs, lw, ms, colormap):
    nrm_F = False
    linreg_F = False
    Igs_plot_Ids = 'Ids'
    s_config = sweeps[s]
    ysc_config = y_scale[ysc]
    ab_config = ab_val[ab]
    norm_config = norm[nrm_F]
    Igs_plot_config = Igs_plot_opt[Igs_plot_Ids]
    transform_ab = ab_config['transform']
    transform_norm = norm_config['transform']
    transform_ysc = ysc_config['transform']
    ini, fin = s_config['ini'], s_config['fin']
    
    all_curves = []
    devices = []
    for fx, filepath in enumerate(filepaths):
        filename, dev_letter, dev_number, device, contact, l, t, vds_values, light, gas = idvg_fileinfo(filepath)
        data = pd.read_excel(filepath)
        devices.append(device)
        if fx==0:
            contact_fix=contact
            l_fix=l
            t_fix=t
        
        for vd in vds_values:
            if s == 'hysteresis':
                for sw in ['backward','forward']:
                    Vgs, Ids = readexcel_at_vd(data, vd, sweeps[sw]['ini'], sweeps[sw]['fin'], False)
                    Ids = transform_norm(transform_ysc(transform_ab( Ids )))
                    df_curve = pd.DataFrame({"device": device, "sw": sw, "vd": vd, "Vgs": Vgs, "Ids": Ids})
                    all_curves.append(df_curve)
            else:
                Vgs, Ids = readexcel_at_vd(data, vd, ini, fin, False)
                Ids = transform_norm(transform_ysc(transform_ab( Ids )))
                df_curve = pd.DataFrame({"device": device, "Vds": vd, "Vgs": Vgs, "Ids": Ids})
                all_curves.append(df_curve)
            
    df_all = pd.concat(all_curves, ignore_index=True)
        
    vds_values = df_all["Vds"].unique()
    cc = np.linspace(0, 1, len(vds_values))
    if isinstance(colormap, str):
        if colormap == 'Default':
            colors = [cm.jet(x) for x in cc][::-1]
        else:
            cmap = getattr(cm, colormap)
            colors = [cmap(x) for x in cc][::-1]
    else:
        colors = [colormap(x) for x in cc][::-1]
    
    Ids_mins = []
    Ids_maxs = []
    
    for vdx,vd in enumerate(vds_values):
        color = colors[vdx]
        df_vd = df_all[df_all["Vds"] == vd]
        labvd = str(int(vd)) if vd.is_integer() else str(vd)
        
        if s=='hysteresis':
            lab = [labvd, None]
            for swx, sw in enumerate(['backward','forward']):
                df_sw = df_vd[df_vd["sw"] == sw]
                mean_df = df_sw.groupby("Vgs")["Ids"].mean()
                std_df = df_sw.groupby("Vgs")["Ids"].std()
                x_vals = mean_df.index.to_numpy()
                y_vals = mean_df.to_numpy()
                y_err = std_df.to_numpy()
                ax.plot(x_vals, y_vals, color=color, linewidth=lw, marker='o', markersize=ms, label=lab[swx])
                ax.fill_between(x_vals, y_vals - y_err, y_vals + y_err, color=color, alpha=0.2)
                Ids_mins.append((mean_df - std_df).min())
                Ids_maxs.append((mean_df + std_df).max())
        else:
            mean_df = df_vd.groupby("Vgs")["Ids"].mean()
            std_df = df_vd.groupby("Vgs")["Ids"].std()
            x_vals = mean_df.index.to_numpy()
            y_vals = mean_df.to_numpy()
            y_err = std_df.to_numpy()
            ax.plot(x_vals, y_vals, color=color, linewidth=lw, marker='o', markersize=ms, label=labvd)
            ax.fill_between(x_vals, y_vals - y_err, y_vals + y_err, color=color, alpha=0.2)
            Ids_mins.append((mean_df - std_df).min())
            Ids_maxs.append((mean_df + std_df).max())

    def sort_key(s):
        letter = s[0]
        number = int(s[1:])
        return (letter, number)
    devices.sort(key=sort_key)

    title = ''
    for device in devices:
        title += f' {device}'
    title += f' ({contact_fix}) {l_fix}nm {t_fix}K step=0.5V {light} {gas} {s}'
    ax.set_title(title, fontsize=fs)
    
    if len(vds_values)<4:
        ncol=1
    else:
        ncol=2
        
    legend = ax.legend(title="$V_{DS}$ (V)", loc='best', fontsize=fs, frameon = True, ncol=ncol)
    legend.get_title().set_fontsize(fs)
    
    ax.set_xlabel('$V_{GS}$ (V)', fontsize=fs)
    ax.set_xlim(-30, 30)
    
    ylab_symbol = Igs_plot_config["ylab_name"](ab, linreg_F)
    ylab_units = norm_config["ylab_units"](ysc, linreg_F)
    ylab = f'{ylab_symbol} ({ylab_units})'
    ax.set_ylabel(ylab,fontsize=fs)
    ax.set_yscale(ysc)
    #ax.set_ylim(min(Ids_mins), max(Ids_maxs))
    
    ax.tick_params(labelsize=fs)
    ax.grid(True)