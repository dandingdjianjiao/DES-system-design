/**
 * Formulation-related type definitions
 */

export interface ComponentData {
  name: string;
  role: string;
  function?: string;
}

export interface FormulationData {
  // Binary formulation fields (backward compatible)
  HBD?: string;
  HBA?: string;

  // Multi-component formulation fields
  components?: ComponentData[];
  num_components?: number;

  // Common fields
  molar_ratio: string;
}
