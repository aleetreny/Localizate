import { OpportunityShell } from "@/components/opportunity-shell";
import { loadOpportunityArtifacts } from "@/lib/data";
import { HAS_EXTERNAL_PUBLIC_DATA_BASE_URL } from "@/lib/runtime-config";

export const dynamic = "force-static";

export default async function OpportunityPage() {
  if (HAS_EXTERNAL_PUBLIC_DATA_BASE_URL) {
    return <OpportunityShell />;
  }

  const initialArtifacts = await loadOpportunityArtifacts();

  return <OpportunityShell initialArtifacts={initialArtifacts} />;
}
