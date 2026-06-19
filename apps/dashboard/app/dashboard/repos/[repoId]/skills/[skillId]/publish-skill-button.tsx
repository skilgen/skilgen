"use client";

import { useState } from "react";

import { PublishSkillModal } from "./publish-skill-modal";

type PublishSkillButtonProps = {
  skillId: string;
  domain: string;
  accessToken: string;
};

export function PublishSkillButton({ skillId, domain, accessToken }: PublishSkillButtonProps) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        className="rounded-full bg-[color:var(--accent-primary)] px-4 py-2 text-[13px] font-semibold text-black shadow-sm transition-colors hover:bg-[color:var(--accent-bright)]"
        onClick={() => setOpen(true)}
        type="button"
      >
        Publish to Registry
      </button>
      {open ? <PublishSkillModal accessToken={accessToken} domain={domain} onClose={() => setOpen(false)} skillId={skillId} /> : null}
    </>
  );
}
