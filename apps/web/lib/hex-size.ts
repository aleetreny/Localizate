export type HexSize = "small" | "medium" | "large";

export const DEFAULT_HEX_SIZE: HexSize = "small";

export const HEX_SIZE_OPTIONS: ReadonlyArray<{ value: HexSize; label: string }> = [
  { value: "small", label: "Pequeño" },
  { value: "medium", label: "Medio" },
  { value: "large", label: "Grande" }
] as const;

export function formatHexSizeLabel(hexSize: HexSize) {
  return HEX_SIZE_OPTIONS.find((option) => option.value === hexSize)?.label ?? hexSize;
}
