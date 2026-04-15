import { MapShell } from "@/components/map-shell";
import { loadMapSharedArtifacts, loadZoneBoundaryArtifacts } from "@/lib/data";

export const dynamic = "force-static";

export default async function HomePage() {
  const [sharedArtifacts, zoneBoundaries] = await Promise.all([
    loadMapSharedArtifacts(),
    loadZoneBoundaryArtifacts(),
  ]);

  return <MapShell initialArtifacts={{ ...sharedArtifacts, hexes: [] }} initialZoneBoundaries={zoneBoundaries} />;
}
