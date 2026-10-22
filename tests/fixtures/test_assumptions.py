"""Placeholder values for engine tests ONLY. They are not inputs, not assumptions and
not facts about Kuwait; they exist so the engines can be exercised before the
assumption file is sourced."""

TEST_ASSUMPTIONS = {k: {"value": v, "status": "test", "source": "test placeholder"} for k, v in {
    "albedo.desert": 0.3, "thermal.pvsyst_uc": 29.0, "thermal.pvsyst_uc_tracker": 29.0, "thermal.pvsyst_uv": 0.0,
    "layout.collector_width_1p": 2.4, "soiling.kuwait_rate_by_month": [0.2] * 12,
    "soiling.rain_cleaning_threshold": 5.0, "soiling.max_loss": 30.0, "cleaning.effectiveness": 0.95,
    "cleaning.cost": 50.0, "losses.dc_mismatch_pct": 1.0, "losses.dc_wiring_pct": 1.0,
    "availability.plant": 0.99, "availability.inverter": 0.99, "availability.storage": 0.98,
    "storage.hvac_load": 2.0, "degradation.pv_annual": 0.5, "degradation.pv_first_year": 1.0,
    "wacc.kuwait_ipp": 0.06, "fx.kwd_per_usd": 0.3, "finance.inflation": 0.02}.items()}
