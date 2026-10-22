"""Write and execute notebooks/0*.ipynb. Run: uv run python scripts/make_notebooks.py
Each notebook runs offline from the repository's committed inputs in a few minutes."""

from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "notebooks"
REPO = "ahmedelshazly27/mizan-kuwait-energy-toolkit"

SETUP = f"""# On Colab: clone the repository and install it (inputs are committed, no credentials needed).
import os, sys
if "google.colab" in sys.modules and not os.path.exists("mizan-kuwait-energy-toolkit"):
    !git clone --depth 1 https://github.com/{REPO}.git
    %pip install -q -e "mizan-kuwait-energy-toolkit[pv,econ,system]" matplotlib
    os.chdir("mizan-kuwait-energy-toolkit")
elif os.path.basename(os.getcwd()) == "notebooks":
    os.chdir("..")
import warnings; warnings.filterwarnings("ignore")
import pandas as pd, numpy as np, matplotlib.pyplot as plt
from kwtk import viz; viz.style()"""


def badge(name):
    return (f"[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)]"
            f"(https://colab.research.google.com/github/{REPO}/blob/main/notebooks/{name})")


NOTEBOOKS = {
"01-quickstart.ipynb": [
("md", """# 1. Quickstart: evaluate a plant

A plant is a YAML file. `validate` checks it and explains problems in sentences;
`evaluate` simulates it hour by hour under Kuwaiti weather, costs it, and places it
in Kuwait's power system. Every input is listed with its origin."""),
("code", "from kwtk.config.validate import validate\nprint(validate('configs/examples/shagaya-scale-pv-tracker.yaml').text())"),
("md", "A broken file fails with sentences, not a stack trace:"),
("code", """import yaml, tempfile
cfg = yaml.safe_load(open('configs/examples/shagaya-scale-pv-tracker.yaml'))
cfg['inverters']['dc_ac_ratio'] = 2.5
cfg['site']['location']['lat'] = 31.0
cfg['pv']['arrays'][0]['layout']['gcr'] = 0.33
cfg['pv']['arrays'][0]['mountng'] = cfg['pv']['arrays'][0].pop('mounting')
f = tempfile.NamedTemporaryFile('w', suffix='.yaml', delete=False); yaml.safe_dump(cfg, f); f.close()
print(validate(f.name).text())"""),
("code", """from kwtk.plant.evaluate import evaluate
run = evaluate('configs/examples/shagaya-scale-pv-tracker.yaml')
r = run['result']
pd.DataFrame(r['energy_by_year']).set_index('year').round(1)"""),
("code", """e = r['economics']
print(f"LCOE (real): {e['lcoe_real_fils_per_kwh']:.1f} fils/kWh  ({e['lcoe_real_usd_per_kwh']*100:.2f} US cents)")
print(f"System: fuel cost avoided {r['system_context']['fuel_cost_avoided_kd_per_mwh']:.1f} KD/MWh, "
      f"curtailed by the system {r['system_context']['system_curtailment_mwh']/1e3:.0f} GWh/yr")
print('Unverified inputs:', ', '.join(x.split(':')[1] for x in r['unverified_inputs']))"""),
("md", "Every input and where it came from:"),
("code", "pd.DataFrame(r['inputs']).T[['value', 'origin', 'status']].fillna('')"),
],
"02-kuwaiti-inputs.ipynb": [
("md", """# 2. The Kuwaiti inputs

Measured data come from the Kuwait Electricity Open Dataset, copied unchanged into
`inputs/dataset/` and pinned to a dataset commit. Loaders never choose between
sources: a series call names its source, and open conflicts are reported."""),
("code", "from kwtk.inputs import dataset as d\nimport yaml\nprint(yaml.safe_load(open('inputs/dataset/MANIFEST.yaml'))['commit'][:12], d.verify() or 'snapshot verified')"),
("code", """f = d.fleet('mew-yb-2023')
print(len(f), 'units,', f.capacity_mw.sum(), 'MW')
f.pivot_table(index='plant_id', columns='technology', values='capacity_mw', aggfunc='sum', fill_value=0).round(1)"""),
("code", """p = d.series('peak_load', 'national', 'annual', series='mew-yb')
p = p.sort_values('source_id').groupby('period_start').last()
fig, ax = plt.subplots(figsize=(8, 3.2))
ax.plot(pd.to_datetime(p.index).year, p.value, marker='o', ms=4)
ax.set_title('System peak load (MEW yearbooks, newest edition per year)'); ax.set_ylabel('MW')
plt.show()"""),
("code", """cap = d.series('installed_capacity', 'national', 'annual', series='mew-yb')
print(len(d.open_conflicts(cap.id)), 'open conflicts on national capacity (listed, not resolved):')
d.open_conflicts(cap.id)[['key', 'values']].head()"""),
("code", "pd.DataFrame(yaml.safe_load(open('inputs/assumptions.yaml'))['assumptions']).T[['value', 'unit', 'status']].fillna('')"),
],
"03-demand-reconstruction.ipynb": [
("md", """# 3. Hourly demand: a reconstruction

No hourly Kuwaiti load is published. The series in `inputs/demand/` is modelled from
monthly energy, annual peaks and population-weighted ERA5 temperature, fitted to
MEW's daily data, and checked against the four half-hourly curves the yearbooks print
for the yearly peak day, which the fit never sees (decisions D1-D3)."""),
("code", """import json
from kwtk.inputs import demand
meta = json.load(open('inputs/demand/kuwait-gross-load-reconstructed.json'))
print(meta['label']); pd.DataFrame(meta['validation_peak_days']).round(3)"""),
("code", """L = demand.load_series()
c = demand.peak_curves(); c = c[c.source_id == 'mew-yb-2023'].set_index('t').mw
c = c[c.index.normalize() == c.index[0].normalize()]      # the printed closing 0:00 belongs to the next day
fig, ax = plt.subplots(figsize=(8, 3.4))
ax.plot(c.index.hour + c.index.minute / 60, c.values, label='MEW printed (half-hourly)')
m = L['2023-08-02']; ax.plot(m.index.hour, m.values, label='reconstruction (hourly)')
ax.set_title('2 August 2023, the yearly peak day: held-out check'); ax.set_ylabel('MW'); ax.set_xlabel('hour (Kuwait time)')
ax.legend(); plt.show()"""),
("code", """y = L['2023']
fig, ax = plt.subplots(figsize=(8, 3.2))
ax.plot(np.arange(len(y)) / len(y) * 100, np.sort(y.values)[::-1])
ax.set_title('Load duration, 2023 (reconstruction)'); ax.set_ylabel('MW'); ax.set_xlabel('% of hours')
plt.show()"""),
("md", "Known defects (night too high, a large peak stretch, a non-summer shape that is an assumption) are listed in `docs/demand-reconstruction.md`."),
],
"04-weather.ipynb": [
("md", """# 4. Weather and solar resource

ERA5 reanalysis for every 0.25° cell over Kuwait (45 cells, hourly 2013-2024), stored
in `inputs/weather/grid/`. A plant uses its nearest cell."""),
("code", """from kwtk.inputs import era5
rows = []
for la, lo in era5.CELLS:
    if era5._cell_file(la, lo).exists():
        w = era5.site_weather(la, lo, [2019, 2020, 2021, 2022, 2023])
        rows.append({'lat': la, 'lon': lo, 'ghi_kwh_m2_yr': w.ghi.sum() / 1000 / 5, 'dni_kwh_m2_yr': w.dni.sum() / 1000 / 5,
                     'mean_temp_c': w.temp_air.mean(), 'rain_mm_yr': w.precip_mm.sum() / 5})
g = pd.DataFrame(rows); g.describe().round(1)"""),
("code", """fig, ax = plt.subplots(figsize=(6, 5))
sc = ax.scatter(g.lon, g.lat, c=g.ghi_kwh_m2_yr, cmap='Blues', s=380, marker='s')
plt.colorbar(sc, label='GHI, kWh/m² per year (2019-2023 mean)')
ax.set_title('Global horizontal irradiance by ERA5 cell'); ax.set_xlabel('longitude'); ax.set_ylabel('latitude'); ax.grid(False)
plt.show()"""),
("code", """w = era5.site_weather(29.2055, 47.0524, [2023])
m = w.groupby(w.index.month).agg(ghi=('ghi', 'sum'), temp=('temp_air', 'mean'))
fig, ax = plt.subplots(figsize=(8, 3))
ax.bar(m.index, m.ghi / 1000, width=0.7); ax.set_title('Shagaya: monthly GHI, 2023'); ax.set_ylabel('kWh/m²'); ax.set_xticks(range(1, 13))
plt.show()"""),
],
"05-pv-losses.ipynb": [
("md", """# 5. PV yield and losses

The PV engine steps from irradiance to the connection, recording each loss. Here:
the 1.1 GW tracker example, and the Shagaya Phase I approximation compared with
the yield reported for the real plant (1,805-1,810 kWh/kWp, not verified)."""),
("code", """from kwtk.plant.evaluate import evaluate
runs = {k: evaluate(f'configs/examples/{k}.yaml') for k in ['shagaya-scale-pv-tracker', 'shagaya-pv1-approximation']}
w = pd.DataFrame(runs['shagaya-scale-pv-tracker']['result']['waterfall_mwh']).set_index('year').mean()
(w / w['front_poa'] * 100).round(1).rename('% of front POA')"""),
("code", """steps = w.drop('nameplate_x_ghi'); delta = steps.diff().fillna(steps.iloc[0])
fig, ax = plt.subplots(figsize=(9, 3.6))
ax.bar(range(len(steps)), steps.values / 1e3, width=0.7, color=viz.SERIES[0])
NAMES = {'front_poa': 'sunlight on modules', 'after_iam': 'after reflection', 'after_soiling': 'after soiling',
         'after_bifacial_gain': 'with rear gain', 'after_temperature': 'after heat', 'after_dc_losses': 'after DC losses',
         'after_inverter_efficiency': 'after inverters', 'after_clipping': 'after clipping', 'after_ac_losses': 'after AC losses',
         'after_availability': 'after outages'}
ax.set_xticks(range(len(steps))); ax.set_xticklabels([NAMES[s] for s in steps.index], rotation=35, ha='right')
ax.set_title('Energy after each stage, 1.1 GW tracker (mean year)'); ax.set_ylabel('GWh')
plt.show()"""),
("code", """y = pd.DataFrame(runs['shagaya-pv1-approximation']['result']['energy_by_year']).set_index('year')
y[['export_mwh', 'specific_yield_kwh_per_kwp']].round(0)"""),
("code", """s = runs['shagaya-scale-pv-tracker']['pv']['soiling_ratio']
fig, ax = plt.subplots(figsize=(8, 3))
ax.plot((1 - s['2023']) * 100, lw=1)
ax.set_title('Soiling loss, 2023 (cleaning every 14 days, rain above 6 mm cleans)'); ax.set_ylabel('%')
plt.show()"""),
],
"06-storage-and-controls.ipynb": [
("md", """# 6. Storage, controls and curtailment

Three designs with the same PV: no storage; a battery behind a 900 MW connection
storing what the limit would curtail; a battery behind a 1,350 MW connection shaving
the system's net peak."""),
("code", """from kwtk.plant.evaluate import evaluate
from kwtk.plant import report
ids = ['shagaya-scale-pv-tracker', 'shagaya-scale-pv-storage-export-limit', 'shagaya-scale-pv-storage-peak-shaving']
runs = {k: evaluate(f'configs/examples/{k}.yaml') for k in ids}
report.compare([r['result'] for r in runs.values()]).round(2)"""),
("code", """h = runs['shagaya-scale-pv-storage-export-limit']['hourly']
d = h['2023-06-15':'2023-06-17']; t = d.index.tz_convert('Asia/Kuwait')
fig, ax = plt.subplots(figsize=(9, 3.4))
ax.plot(t, d.pv_ac, label='PV at inverters'); ax.plot(t, d.export, label='export (900 MW limit)'); ax.plot(t, d.battery, label='battery (+ discharge)')
ax.set_title('Three June days, export-limit design'); ax.set_ylabel('MW'); ax.legend(ncol=3, loc='lower left'); plt.show()"""),
],
"07-economics.ipynb": [
("md", """# 7. Economics

PySAM Single Owner on the lifetime hourly export, with real costs and the Kuwait
WACC. The verified capital costs are NREL's US benchmarks; Gulf costs are lower
(IRENA's global 2024 average and Saudi battery auctions, both unverified). This
notebook shows how much that choice moves the answer."""),
("code", """import yaml, tempfile
from kwtk.plant.evaluate import evaluate
def with_capex(pv_key, label):
    cfg = yaml.safe_load(open('configs/examples/shagaya-scale-pv-tracker.yaml'))
    cfg['economics']['capex'] = {'pv_total_usd_per_kwac': f'assumption:{pv_key}'}
    cfg['id'] = label; cfg['evaluation']['system_context'] = None; cfg['evaluation']['years'] = [2023]
    f = tempfile.NamedTemporaryFile('w', suffix='.yaml', delete=False); yaml.safe_dump(cfg, f); f.close()
    return evaluate(f.name)['result']['economics']
rows = {'NREL ATB 2025 (US, verified)': with_capex('capex.pv_atb2025_usd_per_kw', 'atb'),
        'IRENA 2024 global average (unverified)': with_capex('capex.pv_irena2024_global_usd_per_kw', 'irena')}
pd.DataFrame(rows).T[['capex_usd', 'lcoe_real_fils_per_kwh', 'lcoe_real_usd_per_kwh', 'breakeven_ppa_fils_per_kwh']].round(3)"""),
("md", "For context, reported Gulf PV tariffs are 1.04-2.34 US cents/kWh (not verified). The LCOE uses PySAM; an independent capital-recovery calculation agrees to within 0.3 %."),
],
"08-system-and-water.ipynb": [
("md", """# 8. Kuwait's system and water

The system model dispatches Kuwait's fleet in three zones with MEW's measured fuel
costs and must-run floors for distillation. A plant's value to the system is the fuel
it avoids; its limit is the hours the system cannot absorb it."""),
("code", """from kwtk.engines import system, water
st = system.station_table(2023)
st[['gen_mwh', 'kd_per_mwh', 'mmbtu_per_mwh', 'min_monthly_avg_mw']].round(2).sort_values('kd_per_mwh')"""),
("code", "system.zone_shares().round(3)"),
("code", """from kwtk.plant.evaluate import evaluate
r = evaluate('configs/examples/shagaya-scale-pv-tracker.yaml')['result']['system_context']
pd.Series(r['displaced_mwh_by_station']).div(1e3).round(0).rename('GWh displaced').sort_values(ascending=False)"""),
("code", """p = water.seasonal_profile()
fig, ax = plt.subplots(figsize=(8, 3))
ax.bar(p.index, p.values * 100, width=0.7); ax.set_xticks(range(1, 13))
ax.set_title('Distilled-water production by month, % of the highest month (MEW 2020-2021)'); ax.set_ylabel('%')
plt.show()"""),
("code", """ro = evaluate('configs/examples/shagaya-scale-pv-ro.yaml')['result']
ro['storage']['water']"""),
],
}


def main(only=()):
    NB.mkdir(exist_ok=True)
    for name, cells in NOTEBOOKS.items():
        if only and not any(name.startswith(o) for o in only):
            continue
        nb = nbformat.v4.new_notebook()
        nb.cells = [nbformat.v4.new_markdown_cell(badge(name)), nbformat.v4.new_code_cell(SETUP)]
        for kind, src in cells:
            nb.cells.append(nbformat.v4.new_markdown_cell(src) if kind == "md" else nbformat.v4.new_code_cell(src))
        nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
        NotebookClient(nb, timeout=900, kernel_name="python3", resources={"metadata": {"path": str(NB)}}).execute()
        nbformat.write(nb, NB / name)
        print("executed", name)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
