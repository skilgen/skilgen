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
        className="rounded-md border border-[rgb(var(--accent-primary-rgb)/0.4)] px-3 py-1.5 text-[13px] font-semibold text-[color:var(--accent-primary)] transition-colors hover:bg-[rgb(var(--accent-primary-rgb)/0.08)]"
        onClick={() => setOpen(true)}
        type="button"
      >
        Publish
      </button>
      {open ? <PublishSkillModal accessToken={accessToken} domain={domain} onClose={() => setOpen(false)} skillId={skillId} /> : null}
    </>
  );
}
