"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const VIEWS = [
  { href: "/", label: "Histórico" },
  { href: "/oportunidades", label: "Oportunidades" },
];

export function ViewTabs() {
  const pathname = usePathname();

  return (
    <nav aria-label="Vistas del producto" className="view-switch">
      {VIEWS.map((view) => {
        const isActive = pathname === view.href;
        return (
          <Link className="view-switch-link" data-active={isActive} href={view.href} key={view.href}>
            {view.label}
          </Link>
        );
      })}
    </nav>
  );
}

type MobileAppHeaderProps = {
  title: string;
};

export function MobileAppHeader({ title }: MobileAppHeaderProps) {
  return (
    <header className="mobile-app-header panel">
      <div className="mobile-app-identity">
        <span className="mobile-app-brand">Localízate Madrid</span>
        <h1 className="mobile-app-title">{title}</h1>
      </div>
      <ViewTabs />
    </header>
  );
}
