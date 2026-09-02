export function revealOnMobile(element: HTMLElement | null) {
  if (!element || typeof window === "undefined" || !window.matchMedia("(max-width: 720px)").matches) {
    return;
  }

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  window.requestAnimationFrame(() => {
    element.scrollIntoView({
      behavior: reducedMotion ? "auto" : "smooth",
      block: "start",
    });
  });
}
