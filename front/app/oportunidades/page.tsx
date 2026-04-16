import { OpportunityShell } from "@/components/opportunity-shell";
import { loadOpportunityArtifacts } from "@/lib/data";

export const dynamic = "force-static";

export default async function OpportunityPage() {
  const initialArtifacts = await loadOpportunityArtifacts();

  return <OpportunityShell initialArtifacts={initialArtifacts} />;
}
