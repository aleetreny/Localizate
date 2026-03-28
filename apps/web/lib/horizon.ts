import type { HexAggregate, ZoneAggregate } from "@/lib/types";

export type Horizon = "12m" | "24m";

type HorizonCarrier = Pick<HexAggregate, "survival_12m" | "survival_24m" | "support_12m" | "support_24m">;
type ZoneHorizonCarrier = Pick<ZoneAggregate, "survival_12m" | "survival_24m" | "support_12m" | "support_24m">;

export function getHorizonSurvival(item: HorizonCarrier | ZoneHorizonCarrier, horizon: Horizon): number | null {
  return horizon === "24m" ? item.survival_24m : item.survival_12m;
}

export function getHorizonSupport(item: HorizonCarrier | ZoneHorizonCarrier, horizon: Horizon): number {
  return horizon === "24m" ? item.support_24m : item.support_12m;
}

export function formatHorizonShortLabel(horizon: Horizon): string {
  return horizon;
}

export function formatHorizonLongLabel(horizon: Horizon): string {
  return horizon === "24m" ? "24 meses" : "12 meses";
}

export function isFiniteNumber(value: number | null | undefined): value is number {
  return typeof value === "number" && Number.isFinite(value);
}