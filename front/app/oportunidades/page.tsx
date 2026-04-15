import { OpportunityShell } from "@/components/opportunity-shell";
import { loadOpportunityArtifacts, loadOpportunitySectionIndexArtifacts } from "@/lib/data";

export const dynamic = "force-static";

export default async function OpportunityPage() {
  const [initialArtifacts, initialSectionIndex] = await Promise.all([
    loadOpportunityArtifacts(),
    loadOpportunitySectionIndexArtifacts(),
  ]);

  return <OpportunityShell initialArtifacts={initialArtifacts} initialSectionIndex={initialSectionIndex} />;
}
