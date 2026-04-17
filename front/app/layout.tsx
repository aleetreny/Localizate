import type { Metadata } from "next";
import { Manrope, Space_Grotesk } from "next/font/google";

import { AboutProject } from "@/components/about-project";
import "./globals.css";

const manrope = Manrope({
  subsets: ["latin"],
  variable: "--font-sans"
});

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-display"
});

export const metadata: Metadata = {
  title: "Localizate Madrid",
  description: "Mapa de supervivencia comercial por hexágono en Madrid."
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
