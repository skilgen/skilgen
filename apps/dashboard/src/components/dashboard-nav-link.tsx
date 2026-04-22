"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@skillayer/ui";

type DashboardNavLinkProps = {
  href: string;
  icon: React.ReactNode;
  label: string;
  badge?: string;
};

export function DashboardNavLink({ href, icon, label, badge }: DashboardNavLinkProps) {
  const pathname = usePathname();
  const isActive = href === "/dashboard" ? pathname === href : pathname === href || pathname.startsWith(`${href}/`);

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
      {badge ? (
        <span className="rounded-full bg-[#C9973A]/15 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-[#e8b84b]">
          {badge}
        </span>
      ) : null}
    </Link>
  );
}
