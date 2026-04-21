"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@skillayer/ui";

type DashboardNavLinkProps = {
  href: string;
  icon: React.ReactNode;
  label: string;
};

export function DashboardNavLink({ href, icon, label }: DashboardNavLinkProps) {
  const pathname = usePathname();
  const isActive = pathname === href;

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
      <span>{label}</span>
    </Link>
  );
}
