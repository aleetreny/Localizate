import { MapShell } from "@/components/map-shell";
import { loadMapSharedArtifacts, loadZoneBoundaryArtifacts } from "@/lib/data";
import { HAS_EXTERNAL_PUBLIC_DATA_BASE_URL } from "@/lib/runtime-config";

export const dynamic = "force-static";

export default async function HomePage() {
  if (HAS_EXTERNAL_PUBLIC_DATA_BASE_URL) {
    return <MapShell />;
  }

  const [sharedArtifacts, zoneBoundaries] = await Promise.all([
    loadMapSharedArtifacts(),
    loadZoneBoundaryArtifacts(),
  ]);

  return <MapShell initialArtifacts={{ ...sharedArtifacts, hexes: [] }} initialZoneBoundaries={zoneBoundaries} />;
}
