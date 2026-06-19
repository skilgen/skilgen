"use client";

import { Github } from "lucide-react";
import { useState } from "react";

import { AddReposModal } from "./add-repos-modal";

export function AddReposButton({
  orgId,
  accessToken,
  label,
  hasInstallation,
}: {
  orgId: string;
  accessToken: string;
  label: string;
  hasInstallation: boolean;
}) {
  const [open, setOpen] = useState(false);

  if (!hasInstallation) {
    return (
      <a className="inline-flex h-10 items-center justify-center rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] transition-colors hover:bg-[color:var(--accent-bright)]" href="https://github.com/apps/skillayer/installations/new" rel="noreferrer" target="_blank">
        <Github className="mr-2 h-4 w-4" />
        {label}
      </a>
    );
  }

  return (
    <>
      <button className="inline-flex h-10 items-center justify-center rounded-md bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] transition-colors hover:bg-[color:var(--accent-bright)]" onClick={() => setOpen(true)} type="button">
        <Github className="mr-2 h-4 w-4" />
        {label}
      </button>
      {open ? <AddReposModal accessToken={accessToken} onClose={() => setOpen(false)} orgId={orgId} /> : null}
    </>
  );
}
