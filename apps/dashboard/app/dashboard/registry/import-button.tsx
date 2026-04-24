"use client";

import { useState } from "react";
import { Upload } from "lucide-react";

import { ImportSkillModal } from "./import-skill-modal";

type ImportButtonProps = {
  orgId: string;
  accessToken: string;
};

export function ImportButton({ orgId, accessToken }: ImportButtonProps) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        className="inline-flex h-9 items-center gap-2 rounded-md border border-[color:var(--bg-border)] px-3 text-[13px] font-semibold text-[color:var(--text-secondary)] transition-colors hover:bg-[color:var(--bg-elevated)]"
        onClick={() => setOpen(true)}
        type="button"
      >
        <Upload className="h-3.5 w-3.5" />
        Import from file
      </button>
      {open ? <ImportSkillModal accessToken={accessToken} onClose={() => setOpen(false)} orgId={orgId} /> : null}
    </>
  );
}
