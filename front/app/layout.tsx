import type { Metadata } from "next";
import { Manrope, Space_Grotesk } from "next/font/google";

import { AboutProject } from "@/components/about-project";
import "./globals.css";

const FALLBACK_SITE_URL = "https://localizate.pages.dev";
const SITE_TITLE = "Localízate Madrid | Mapa de oportunidades y supervivencia comercial";
const SITE_DESCRIPTION =
  "Explora un mapa interactivo de Madrid para detectar oportunidades comerciales y entender la supervivencia de cada zona mediante datos territoriales y análisis por hexágono.";
const PREVIEW_IMAGE_PATH = "/Preview.png";

function resolveMetadataBase() {
  const configuredSiteUrl = process.env.NEXT_PUBLIC_SITE_URL?.trim();

  if (!configuredSiteUrl) {
    return new URL(FALLBACK_SITE_URL);
  }

  try {
    return new URL(configuredSiteUrl);
  } catch {
    return new URL(`https://${configuredSiteUrl}`);
  }
}

const manrope = Manrope({
  subsets: ["latin"],
  variable: "--font-sans"
});

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-display"
});

export const metadata: Metadata = {
  metadataBase: resolveMetadataBase(),
  title: SITE_TITLE,
  description: SITE_DESCRIPTION,
  alternates: {
    canonical: "/"
  },
  robots: {
    index: true,
    follow: true
  },
  openGraph: {
    type: "website",
    locale: "es_ES",
    siteName: "Localízate Madrid",
    title: SITE_TITLE,
    description: SITE_DESCRIPTION,
    url: "/",
    images: [
      {
        url: PREVIEW_IMAGE_PATH,
        alt: "Vista previa del mapa interactivo de Localízate Madrid",
        width: 1200,
        height: 630
      }
    ]
  },
  twitter: {
    card: "summary_large_image",
    title: SITE_TITLE,
    description: SITE_DESCRIPTION,
    images: [PREVIEW_IMAGE_PATH]
  }
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body className={`${manrope.variable} ${spaceGrotesk.variable}`}>
        {children}
        <AboutProject />
      </body>
    </html>
  );
}
