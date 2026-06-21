import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "OmniCore AI",
  description: "AI-powered commerce and operations intelligence platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full bg-background text-foreground">{children}</body>
    </html>
  );
}
