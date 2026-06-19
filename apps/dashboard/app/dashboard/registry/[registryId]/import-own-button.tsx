"use client";

import { useState } from "react";

import { ImportSkillModal } from "../import-skill-modal";

type ImportOwnButtonProps = {
  orgId: string;
  accessToken: string;
};

export function ImportOwnButton({ orgId, accessToken }: ImportOwnButtonProps) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        className="inline-flex h-11 items-center rounded-md border border-[color:var(--bg-border)] px-4 text-[13px] font-semibold text-[color:var(--text-primary)] transition-colors hover:bg-[color:var(--bg-elevated)]"
        onClick={() => setOpen(true)}
        type="button"
      >
        Import your own
      </button>
      {open ? <ImportSkillModal accessToken={accessToken} onClose={() => setOpen(false)} orgId={orgId} /> : null}
    </>
  );
}
