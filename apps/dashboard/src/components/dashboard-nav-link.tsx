"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { cn } from "@skillayer/ui";

type DashboardNavLinkProps = {
  href: string;
  icon: React.ReactNode;
  label: string;
  badge?: string;
  badgeVariant?: "label" | "dot";
  unreadStorageKey?: string;
};

export function DashboardNavLink({ href, icon, label, badge, badgeVariant = "label", unreadStorageKey }: DashboardNavLinkProps) {
  const pathname = usePathname();
  const [unreadCount, setUnreadCount] = useState(0);
  const hrefPath = href.split("?")[0] ?? href;
  const exactMatchHrefs = new Set(["/dashboard/eval", "/dashboard/eval/ab-tests"]);
  const isActive = hrefPath === "/dashboard"
    ? pathname === hrefPath
    : exactMatchHrefs.has(hrefPath)
      ? pathname === hrefPath
      : pathname === hrefPath || pathname.startsWith(`${hrefPath}/`);
  useEffect(() => {
    if (!unreadStorageKey) return;
    const readCount = () => {
      const raw = window.localStorage.getItem(unreadStorageKey);
      const parsed = raw ? Number.parseInt(raw, 10) : 0;
      setUnreadCount(Number.isFinite(parsed) ? parsed : 0);
    };
    readCount();
    window.addEventListener("storage", readCount);
    const interval = window.setInterval(readCount, 5000);
    return () => {
      window.removeEventListener("storage", readCount);
      window.clearInterval(interval);
    };
  }, [unreadStorageKey]);

  return (
    <Link
      className={cn(
        "flex w-full cursor-pointer items-center gap-3 rounded-lg px-3 py-2 text-[14px] text-[color:var(--text-secondary)] transition-colors hover:bg-[color:var(--bg-surface)] hover:text-[color:var(--text-primary)]",
        isActive &&
          "border-l-2 border-[color:var(--accent-primary)] bg-[color:var(--bg-surface)] pl-2.5 text-[color:var(--text-primary)] hover:bg-[color:var(--bg-surface)] hover:text-[color:var(--text-primary)]"
      )}
      href={href}
    >
      {icon}
      <span className="min-w-0 flex-1">{label}</span>
      {unreadStorageKey && unreadCount > 0 ? (
        <span className="min-w-5 rounded-full bg-red-500 px-1.5 py-0.5 text-center text-[10px] font-bold text-white">{Math.min(99, unreadCount)}</span>
      ) : badge && badgeVariant === "dot" ? (
        <span aria-label={badge} className="h-2 w-2 animate-pulse rounded-full bg-[#f59e0b]" />
      ) : badge ? (
        <span className="rounded-full bg-[#C9973A]/15 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-[#e8b84b]">
          {badge}
        </span>
      ) : null}
    </Link>
  );
}
