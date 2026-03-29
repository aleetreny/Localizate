export type TooltipPosition = {
  left: number;
  top: number;
};

type TooltipAnchor = {
  x: number;
  y: number;
};

type TooltipSize = {
  width: number;
  height: number;
};

type TooltipViewport = {
  width: number;
  height: number;
};

type Rect = {
  left: number;
  top: number;
  right: number;
  bottom: number;
};

type AxisPlacement = "start" | "end" | "center";

export function computeTooltipPosition({
  anchor,
  tooltip,
  viewport,
  padding = 12,
  gap = 20,
  pointerClearance = 14
}: {
  anchor: TooltipAnchor;
  tooltip: TooltipSize;
  viewport: TooltipViewport;
  padding?: number;
  gap?: number;
  pointerClearance?: number;
}): TooltipPosition {
  const maxLeft = Math.max(padding, viewport.width - tooltip.width - padding);
  const maxTop = Math.max(padding, viewport.height - tooltip.height - padding);
  const horizontalOrder: readonly AxisPlacement[] = viewport.width - anchor.x >= anchor.x ? ["end", "start"] : ["start", "end"];
  const verticalOrder: readonly AxisPlacement[] = viewport.height - anchor.y >= anchor.y ? ["end", "start"] : ["start", "end"];
  const avoidRect: Rect = {
    left: anchor.x - pointerClearance,
    top: anchor.y - pointerClearance,
    right: anchor.x + pointerClearance,
    bottom: anchor.y + pointerClearance
  };

  const candidates: TooltipPosition[] = [];

  for (const vertical of verticalOrder) {
    for (const horizontal of horizontalOrder) {
      candidates.push(buildCandidate(anchor, tooltip, horizontal, vertical, gap));
    }
  }

  for (const horizontal of horizontalOrder) {
    candidates.push(buildCandidate(anchor, tooltip, horizontal, "center", gap));
  }

  for (const vertical of verticalOrder) {
    candidates.push(buildCandidate(anchor, tooltip, "center", vertical, gap));
  }

  let bestCandidate: { left: number; top: number; overlap: number; distance: number; index: number } | null = null;

  for (const [index, candidate] of candidates.entries()) {
    const left = clamp(candidate.left, padding, maxLeft);
    const top = clamp(candidate.top, padding, maxTop);
    const rect: Rect = {
      left,
      top,
      right: left + tooltip.width,
      bottom: top + tooltip.height
    };
    const overlap = computeOverlapArea(rect, avoidRect);
    const distance = computeDistanceSquared(rect, anchor);

    if (
      !bestCandidate
      || overlap < bestCandidate.overlap
      || (overlap === bestCandidate.overlap && distance > bestCandidate.distance)
      || (overlap === bestCandidate.overlap && distance === bestCandidate.distance && index < bestCandidate.index)
    ) {
      bestCandidate = { left, top, overlap, distance, index };
    }
  }

  if (!bestCandidate) {
    return { left: padding, top: padding };
  }

  return {
    left: bestCandidate.left,
    top: bestCandidate.top
  };
}

function buildCandidate(anchor: TooltipAnchor, tooltip: TooltipSize, horizontal: AxisPlacement, vertical: AxisPlacement, gap: number) {
  return {
    left: computeAxisPosition(anchor.x, tooltip.width, horizontal, gap),
    top: computeAxisPosition(anchor.y, tooltip.height, vertical, gap)
  };
}

function computeAxisPosition(anchor: number, size: number, placement: AxisPlacement, gap: number) {
  if (placement === "end") {
    return anchor + gap;
  }
  if (placement === "start") {
    return anchor - gap - size;
  }
  return anchor - size / 2;
}

function computeOverlapArea(rect: Rect, avoidRect: Rect) {
  const width = Math.max(0, Math.min(rect.right, avoidRect.right) - Math.max(rect.left, avoidRect.left));
  const height = Math.max(0, Math.min(rect.bottom, avoidRect.bottom) - Math.max(rect.top, avoidRect.top));
  return width * height;
}

function computeDistanceSquared(rect: Rect, anchor: TooltipAnchor) {
  const centerX = rect.left + (rect.right - rect.left) / 2;
  const centerY = rect.top + (rect.bottom - rect.top) / 2;
  return (centerX - anchor.x) ** 2 + (centerY - anchor.y) ** 2;
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max);
}