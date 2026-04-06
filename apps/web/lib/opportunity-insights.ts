import { isFiniteNumber } from "@/lib/horizon";
import type { OpportunityPoint, OpportunitySection } from "@/lib/types";

export const OPPORTUNITY_BENCHMARK_FIELDS = [
  "renta_effective_eur",
  "age_mean_start",
  "population_density_km2_start",
  "total_population_start",
  "share_foreign_start",
  "share_age_15_29_start",
  "share_age_65_plus_start",
  "section_turnover_rate_12m_start",
  "metro_distance_m_start",
  "metro_access_count_500m_start",
  "metro_access_count_1000m_start",
  "section_local_count_start",
  "section_unique_activity_category_count_start",
  "section_same_activity_category_share_start",
] as const;

export type OpportunityBenchmarkField = (typeof OPPORTUNITY_BENCHMARK_FIELDS)[number];

export type OpportunityFieldBenchmark = {
  value: number | null;
  cityMedian: number | null;
  districtMedian: number | null;
  barrioMedian: number | null;
  cityPercentile: number | null;
};

export type OpportunityRankBenchmark = {
  rank: number | null;
  total: number | null;
  topShare: number | null;
  betterThanShare: number | null;
};

export type OpportunityBenchmarkContext = {
  metrics: Record<OpportunityBenchmarkField, OpportunityFieldBenchmark>;
  ranks: {
    city: OpportunityRankBenchmark;
    district: OpportunityRankBenchmark;
    barrio: OpportunityRankBenchmark;
  };
};

type OpportunityBenchmarkTarget = Pick<
  OpportunityPoint,
  | OpportunityBenchmarkField
  | "district_code"
  | "barrio_code"
  | "city_rank"
  | "city_total_sections"
  | "district_rank"
  | "district_total_sections"
  | "barrio_rank"
  | "barrio_total_sections"
>;

type PercentileMode = "ascending" | "descending";

const FIELD_PERCENTILE_MODE: Record<OpportunityBenchmarkField, PercentileMode> = {
  renta_effective_eur: "ascending",
  age_mean_start: "ascending",
  population_density_km2_start: "ascending",
  total_population_start: "ascending",
  share_foreign_start: "ascending",
  share_age_15_29_start: "ascending",
  share_age_65_plus_start: "ascending",
  section_turnover_rate_12m_start: "ascending",
  metro_distance_m_start: "descending",
  metro_access_count_500m_start: "ascending",
  metro_access_count_1000m_start: "ascending",
  section_local_count_start: "ascending",
  section_unique_activity_category_count_start: "ascending",
  section_same_activity_category_share_start: "ascending",
};

export function buildOpportunityBenchmarkContext(
  sections: OpportunitySection[],
  selected: OpportunityBenchmarkTarget | OpportunitySection | null,
): OpportunityBenchmarkContext | null {
  if (!selected || sections.length === 0) {
    return null;
  }

  const districtSections = sections.filter((section) => section.district_code === selected.district_code);
  const barrioSections = sections.filter(
    (section) => section.district_code === selected.district_code && section.barrio_code === selected.barrio_code,
  );

  const metrics = Object.fromEntries(
    OPPORTUNITY_BENCHMARK_FIELDS.map((field) => [
      field,
      buildFieldBenchmark({
        sections,
        districtSections,
        barrioSections,
        value: selected[field],
        field,
      }),
    ]),
  ) as Record<OpportunityBenchmarkField, OpportunityFieldBenchmark>;

  return {
    metrics,
    ranks: {
      city: buildRankBenchmark(selected.city_rank, selected.city_total_sections),
      district: buildRankBenchmark(selected.district_rank, selected.district_total_sections),
      barrio: buildRankBenchmark(selected.barrio_rank, selected.barrio_total_sections),
    },
  };
}

function buildFieldBenchmark({
  sections,
  districtSections,
  barrioSections,
  value,
  field,
}: {
  sections: OpportunitySection[];
  districtSections: OpportunitySection[];
  barrioSections: OpportunitySection[];
  value: number | null;
  field: OpportunityBenchmarkField;
}): OpportunityFieldBenchmark {
  const numericValue = isFiniteNumber(value) ? value : null;
  const cityValues = collectValues(sections, field);
  const districtValues = collectValues(districtSections, field);
  const barrioValues = collectValues(barrioSections, field);

  return {
    value: numericValue,
    cityMedian: median(cityValues),
    districtMedian: median(districtValues),
    barrioMedian: median(barrioValues),
    cityPercentile: computePercentile(cityValues, numericValue, FIELD_PERCENTILE_MODE[field]),
  };
}

function buildRankBenchmark(rank: number | null, total: number | null): OpportunityRankBenchmark {
  if (!isFiniteNumber(rank) || !isFiniteNumber(total) || total <= 0) {
    return {
      rank: null,
      total: null,
      topShare: null,
      betterThanShare: null,
    };
  }

  return {
    rank,
    total,
    topShare: rank / total,
    betterThanShare: Math.max(0, (total - rank) / total),
  };
}

function collectValues(sections: OpportunitySection[], field: OpportunityBenchmarkField): number[] {
  return sections
    .map((section) => section[field])
    .filter(isFiniteNumber)
    .map((value) => Number(value));
}

function median(values: number[]): number | null {
  if (values.length === 0) {
    return null;
  }

  const sorted = [...values].sort((left, right) => left - right);
  const middle = Math.floor(sorted.length / 2);
  if (sorted.length % 2 === 1) {
    return sorted[middle];
  }
  return (sorted[middle - 1] + sorted[middle]) / 2;
}

function computePercentile(values: number[], value: number | null, mode: PercentileMode): number | null {
  if (!isFiniteNumber(value) || values.length === 0) {
    return null;
  }

  const favorableCount = values.filter((candidate) => {
    if (mode === "descending") {
      return candidate >= value;
    }
    return candidate <= value;
  }).length;

  return favorableCount / values.length;
}