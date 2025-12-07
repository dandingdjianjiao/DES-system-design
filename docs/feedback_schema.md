# Experimental Feedback Schema (Long-Table Ready)

This document captures the S0 agreement for experimental feedback. It keeps legacy single-solubility fields while enabling multi-solute x multi-timepoint data.

## Top-Level Shape

```jsonc
{
  "recommendation_id": "REC_20251016_123456",
  "experiment_result": {
    "is_liquid_formed": true,
    "conditions": {
      "temperature_C": 25,
      "solid_liquid_ratio": {
        "solid_mass_g": 1,
        "liquid_volume_ml": 10,
        "ratio_text": "1:10 g:mL"
      }
    },
    "measurements": [
      {"target_material": "cellulose", "time_h": 1,  "leaching_efficiency": 12.0, "unit": "%"},
      {"target_material": "cellulose", "time_h": 3,  "leaching_efficiency": 25.0, "unit": "%"},
      {"target_material": "cellulose", "time_h": 6,  "leaching_efficiency": 38.0, "unit": "%"},
      {"target_material": "cellulose", "time_h": 12, "leaching_efficiency": 40.0, "unit": "%"},
      {"target_material": "lignin",    "time_h": 6,  "leaching_efficiency": 4.0,  "unit": "%", "observation": "turbid"},
      {"target_material": "lignin",    "time_h": 12, "leaching_efficiency": 5.0,  "unit": "%"}
    ],
    "properties": {"viscosity": "45 cP"},
    "notes": "Cellulose cleared after 6h; lignin remains mostly insoluble."
  }
}
```

## Compatibility Rules

- Aggregate solubility fields are **removed** to avoid misleading usage.
- `temperature` (legacy) is still accepted but `conditions.temperature_C` is preferred.
- Long-table fields:
  - `conditions.temperature_C` — experimental temperature
  - `conditions.solid_liquid_ratio` — structured solid/liquid ratio
  - `measurements[]` — each row is (target_material, time_h, leaching_efficiency, unit (% default), observation)

**Current frontend (production path)** only exposes the long-table mode; simple mode UI has been removed for clarity (backend still accepts legacy fields for compatibility if ever needed).

## Files Touched in S0

- `src/web_backend/models/schemas.py`
  - Added `SolidLiquidRatio`, `ExperimentConditions`, `DissolutionMeasurement`
  - Extended `ExperimentResultRequest` / `ExperimentResultData`
- `src/web_frontend/src/types/index.ts`
  - Synced TS types so frontend matches backend

## Next Steps (for later stages)

- S1: Frontend long-table / CSV / JSON input UI; keep simple mode
- S2: Backend parsing + compatibility logic; auto-fill measurements from legacy fields
- S3: Agent-side programmatic summarization + prompt tweaks
