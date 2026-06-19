import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { AuthKitProvider } from "@workos-inc/authkit-nextjs/components";

import { PostHogProvider } from "@/components/posthog-provider";
import "./globals.css";

const geistSans = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

const geistMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
});

export const metadata: Metadata = {
  title: "Skillayer Dashboard",
  description: "Skillayer dashboard",
};

const workOSRedirectUri = process.env.NEXT_PUBLIC_WORKOS_REDIRECT_URI || process.env.WORKOS_REDIRECT_URI || "";

const isWorkOSConfigured = Boolean(
  process.env.WORKOS_API_KEY &&
    process.env.WORKOS_CLIENT_ID &&
    process.env.WORKOS_COOKIE_PASSWORD &&
    process.env.WORKOS_COOKIE_PASSWORD.length >= 32 &&
    workOSRedirectUri,
);

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const content = (
    <>
      <PostHogProvider />
      {children}
    </>
  );

  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable}`}>
        {isWorkOSConfigured ? <AuthKitProvider>{content}</AuthKitProvider> : content}
      </body>
    </html>
  );
}
