"""Write library/ entries from the California Energy Commission module and inverter
lists as bundled with pvlib (SAM library files dated 2019-03-05). Run:
    uv run python scripts/library_from_cec.py
Each entry records the CEC name and file it came from. Inverter efficiency curves are
computed with the Sandia inverter model (pvlib.inverter.sandia) from the CEC
coefficients, at the rated DC voltage."""

from pathlib import Path

import numpy as np
import pvlib
import yaml

ROOT = Path(__file__).resolve().parents[1]
MODULES = {"jinko-jkm315pp-72": "Jinko_Solar_Co___Ltd_JKM315PP_72", "solar-frontier-sf160-s": "Solar_Frontier_SF160_S"}
INVERTERS = {"sma-sc-2500-ev": "SMA_America__SC_2500_EV_US__550V_"}
SRC = "California Energy Commission list via SAM library {f} (bundled with pvlib {v}), entry {n}"

mods = pvlib.pvsystem.retrieve_sam("CECMod")
for key, name in MODULES.items():
    m = mods[name]
    d = {"id": key, "kind": "module", "generic": False, "stc_power_w": round(float(m.STC), 2), "technology": m.Technology,
         "vmp_v": float(m.V_mp_ref), "imp_a": float(m.I_mp_ref), "voc_v": float(m.V_oc_ref), "isc_a": float(m.I_sc_ref),
         "temp_coeff_pmax_pct_per_c": float(m.gamma_r), "bifaciality": 0.0, "area_m2": float(m.A_c),
         "length_m": float(m.Length), "width_m": float(m.Width),
         "source": SRC.format(f="sam-library-cec-modules-2019-03-05.csv", v=pvlib.__version__, n=name)}
    (ROOT / "library" / "modules" / f"{key}.yaml").write_text(yaml.safe_dump(d, sort_keys=False))

invs = pvlib.pvsystem.retrieve_sam("CECInverter")
for key, name in INVERTERS.items():
    p = invs[name]
    loads = [0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0]
    pdc = np.array(loads) * p.Pdco
    pac = pvlib.inverter.sandia(np.full_like(pdc, p.Vdco), pdc, p)
    curve = [[round(l * p.Pdco / p.Paco, 4), round(float(a / dc), 4)] for l, a, dc in zip(loads, pac, pdc)]
    d = {"id": key, "kind": "inverter", "ac_rating_kva": round(float(p.Paco) / 1000, 2), "efficiency_curve": curve,
         "mppt_count": 1, "temperature_derate": None,
         "source": SRC.format(f="sam-library-cec-inverters-2019-03-05.csv", v=pvlib.__version__, n=name)
         + "; efficiency curve from the Sandia model at Vdco (load = DC power / AC rating)"}
    (ROOT / "library" / "inverters" / f"{key}.yaml").write_text(yaml.safe_dump(d, sort_keys=False))
print("written")
