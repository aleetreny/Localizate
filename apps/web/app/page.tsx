import { MapShell } from "@/components/map-shell";
import { loadMapArtifacts } from "@/lib/data";

export const dynamic = "force-static";

export default async function HomePage() {
  const artifacts = await loadMapArtifacts();

  return <MapShell initialArtifacts={artifacts} />;
}