"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { X, ChevronDown, ChevronRight, Wand2, CheckCircle2, Copy } from "lucide-react";

import type { OrgRedFlags, RedFlag, RedFlagDismissal } from "../../../lib/data";

const CLIENT_API_URL = process.env.NEXT_PUBLIC_API_URL || "https://api.skillayer.com";

// ─── helpers ────────────────────────────────────────────────────────────────

function severityColor(s: RedFlag["severity"]) {
  if (s === "critical") return "bg-red-500";
  if (s === "high") return "bg-amber-500";
  return "bg-blue-500";
}

function flagTypeMeta(flag_type: RedFlag["flag_type"]): { label: string; pill: string; icon: string } {
  switch (flag_type) {
    case "stale_but_active":
      return { label: "Stale & Active", pill: "bg-red-500/20 text-red-300", icon: "🔴" };
    case "freshness_critical":
      return { label: "Zero Freshness", pill: "bg-red-500/20 text-red-300", icon: "🔴" };
    case "conflict":
      return { label: "Conflicting Skills", pill: "bg-orange-500/20 text-orange-300", icon: "⚡" };
    case "missing_security":
      return { label: "Missing Security Skill", pill: "bg-amber-500/20 text-amber-300", icon: "🛡" };
    default:
      return { label: "Dead Skill", pill: "bg-blue-500/20 text-blue-300", icon: "💤" };
  }
}

/** Auto-fix suggestion for each flag type */
function autoFixSuggestion(flag: RedFlag): { title: string; steps: string[]; skillTemplate?: string } {
  switch (flag.flag_type) {
    case "missing_security":
      return {
        title: "Generate a security skill for this repo",
        steps: [
          "Run `skilgen analyse --domain security --project-root .` in the repo root",
          "Review the generated `.skilgen/skills/security/SKILL.md`",
          "Commit and push — Skillayer will auto-import on next push",
        ],
        skillTemplate: `# security

## Domain summary
Security and compliance rules for ${flag.repo_name}. Approved libraries, forbidden patterns, and PII handling.

## Key patterns
- Use parameterised queries — never string-concatenate SQL
- Sanitise all user inputs before processing
- Never log PII (emails, passwords, tokens) in plain text
- Store secrets in environment variables, never in source code
- Use HTTPS for all external service calls

## Anti-patterns
- Raw SQL string concatenation → SQL injection risk
- Hardcoded API keys in source files
- console.log(user) or similar PII leakage

## Last verified
${new Date().toLocaleString("default", { month: "long", year: "numeric" })}`,
      };
    case "stale_but_active":
      return {
        title: `Refresh the "${flag.domain}" skill`,
        steps: [
          `Run \`skilgen analyse --domain ${flag.domain} --project-root .\``,
          "The skill will be updated and versioned automatically",
          "Agents will load the fresh version on their next session",
        ],
      };
    case "freshness_critical":
      return {
        title: `Add a "Last verified" timestamp to "${flag.domain}"`,
        steps: [
          `Open \`.skilgen/skills/${flag.domain}/SKILL.md\``,
          `Add at the bottom: \`## Last verified\\n${new Date().toLocaleString("default", { month: "long", year: "numeric" })}\``,
          "Commit — the freshness score will jump immediately",
        ],
      };
    case "conflict":
      return {
        title: "Reconcile conflicting skill instructions",
        steps: [
          `Open both skill files and identify the contradicting lines`,
          "Pick the canonical rule and delete the conflicting one",
          "Add a note in the winning skill explaining the decision",
        ],
      };
    default:
      return {
        title: `Add "${flag.domain}" to your CLAUDE.md`,
        steps: [
          `Make sure the skill path is referenced in your CLAUDE.md or AGENTS.md`,
          "Run one agent session — the skill will be marked as active",
        ],
      };
  }
}

// ─── grouped flag card ───────────────────────────────────────────────────────

type GroupedFlag = {
  flag_type: RedFlag["flag_type"];
  severity: RedFlag["severity"];
  flags: RedFlag[];
};

function groupFlags(flags: RedFlag[]): GroupedFlag[] {
  const map = new Map<string, GroupedFlag>();
  for (const flag of flags) {
    const key = flag.flag_type;
    if (!map.has(key)) {
      map.set(key, { flag_type: flag.flag_type, severity: flag.severity, flags: [] });
    }
    map.get(key)!.flags.push(flag);
  }
  return Array.from(map.values()).sort((a, b) => {
    const order = { critical: 0, high: 1, medium: 2 };
    return order[a.severity] - order[b.severity];
  });
}

// ─── fix modal ───────────────────────────────────────────────────────────────

function FixModal({ flag, onClose }: { flag: RedFlag; onClose: () => void }) {
  const fix = autoFixSuggestion(flag);
  const [copied, setCopied] = useState(false);

  function copyTemplate() {
    if (fix.skillTemplate) {
      navigator.clipboard.writeText(fix.skillTemplate);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 sm:items-center" onClick={onClose}>
      <div
        className="relative w-full max-w-lg rounded-t-2xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] p-6 shadow-2xl sm:rounded-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          className="absolute right-4 top-4 inline-flex h-8 w-8 items-center justify-center rounded-full text-[color:var(--text-tertiary)] hover:bg-white/10 hover:text-[color:var(--text-primary)]"
          onClick={onClose}
          type="button"
        >
          <X className="h-4 w-4" />
        </button>

        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[rgb(var(--accent-primary-rgb)/0.15)]">
            <Wand2 className="h-4 w-4 text-[color:var(--accent-primary)]" />
          </div>
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Recommended Fix</div>
            <h2 className="text-[16px] font-semibold text-[color:var(--text-primary)]">{fix.title}</h2>
          </div>
        </div>

        <ol className="mb-5 space-y-3">
          {fix.steps.map((step, i) => (
            <li className="flex gap-3 text-[13px] text-[color:var(--text-secondary)]" key={i}>
              <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-[rgb(var(--accent-primary-rgb)/0.15)] text-[11px] font-bold text-[color:var(--accent-primary)]">
                {i + 1}
              </span>
              <span className="font-mono text-[12px] leading-5">{step}</span>
            </li>
          ))}
        </ol>

        {fix.skillTemplate ? (
          <div className="mb-5 overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-base)]">
            <div className="flex items-center justify-between border-b border-[color:var(--bg-border)] px-4 py-2">
              <span className="text-[11px] font-semibold uppercase tracking-widest text-[color:var(--text-tertiary)]">Starter SKILL.md template</span>
              <button
                className="inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-[11px] font-semibold text-[color:var(--accent-primary)] hover:bg-white/5"
                onClick={copyTemplate}
                type="button"
              >
                {copied ? <CheckCircle2 className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
                {copied ? "Copied!" : "Copy"}
              </button>
            </div>
            <pre className="max-h-48 overflow-y-auto p-4 text-[11px] leading-5 text-[color:var(--text-secondary)]">{fix.skillTemplate}</pre>
          </div>
        ) : null}

        <div className="flex gap-3">
          {flag.action_url ? (
            <Link
              className="inline-flex h-9 items-center justify-center rounded-full bg-[color:var(--accent-primary)] px-4 text-[13px] font-semibold text-[color:var(--bg-base)] hover:bg-[color:var(--accent-bright)]"
              href={flag.action_url}
              onClick={onClose}
            >
              Open skill →
            </Link>
          ) : null}
          <button
            className="inline-flex h-9 items-center justify-center rounded-full border border-[color:var(--bg-border)] px-4 text-[13px] font-semibold text-[color:var(--text-secondary)] hover:border-[color:var(--accent-primary)] hover:text-[color:var(--text-primary)]"
            onClick={onClose}
            type="button"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── grouped card ────────────────────────────────────────────────────────────

function GroupedFlagCard({
  group,
  dismissedIds,
  onDismissFlag,
  onOpenFix,
}: {
  group: GroupedFlag;
  dismissedIds: Set<string>;
  onDismissFlag: (flag: RedFlag) => void;
  onOpenFix: (flag: RedFlag) => void;
}) {
  const meta = flagTypeMeta(group.flag_type);
  const visibleFlags = group.flags.filter((f) => !dismissedIds.has(flagId(f)));
  const [expanded, setExpanded] = useState(true);

  if (visibleFlags.length === 0) return null;

  const isSingleRepo = visibleFlags.length === 1;

  return (
    <article className="overflow-hidden rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]">
      {/* Group header */}
      <div className="flex items-center justify-between px-5 py-4">
        <div className="flex items-center gap-3">
          <div className={`h-2.5 w-2.5 rounded-full ${severityColor(group.severity)}`} />
          <span className={`rounded-full px-2.5 py-1 text-[12px] font-semibold ${meta.pill}`}>
            {meta.icon} {meta.label}
          </span>
          <span className="text-[13px] text-[color:var(--text-tertiary)]">
            {visibleFlags.length} {visibleFlags.length === 1 ? "repo" : "repos"} affected
          </span>
        </div>
        <div className="flex items-center gap-2">
          {/* Fix first flag (most representative) */}
          <button
            className="inline-flex items-center gap-1.5 rounded-full border border-[color:var(--accent-primary)] px-3 py-1 text-[12px] font-semibold text-[color:var(--accent-primary)] hover:bg-[rgb(var(--accent-primary-rgb)/0.1)]"
            onClick={() => onOpenFix(visibleFlags[0])}
            type="button"
          >
            <Wand2 className="h-3 w-3" />
            Fix
          </button>
          <button
            className="inline-flex h-7 w-7 items-center justify-center rounded-full text-[color:var(--text-tertiary)] hover:bg-white/10"
            onClick={() => setExpanded((e) => !e)}
            type="button"
          >
            {expanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Affected repos list */}
      {expanded ? (
        <div className="border-t border-[color:var(--bg-border)]">
          {isSingleRepo ? (
            // Single repo — show full detail
            <SingleFlagRow flag={visibleFlags[0]} onDismiss={onDismissFlag} />
          ) : (
            // Multi-repo — compact rows
            visibleFlags.map((flag) => (
              <MultiRepoFlagRow flag={flag} key={flagId(flag)} onDismiss={onDismissFlag} onFix={onOpenFix} />
            ))
          )}
        </div>
      ) : null}
    </article>
  );
}

function flagId(flag: RedFlag): string {
  return `${flag.flag_type}-${flag.repo_id}-${flag.skill_id ?? ""}`;
}

function dismissalId(dismissal: Pick<RedFlagDismissal, "flag_type" | "repo_id" | "skill_id">): string {
  return `${dismissal.flag_type}-${dismissal.repo_id}-${dismissal.skill_id ?? ""}`;
}

function buildHeaders(accessToken: string): HeadersInit {
  return {
    "Content-Type": "application/json",
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
  };
}

function SingleFlagRow({
  flag,
  onDismiss,
}: {
  flag: RedFlag;
  onDismiss: (flag: RedFlag) => void;
}) {
  return (
    <div className="px-5 py-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-[14px] font-semibold text-[color:var(--text-primary)]">{flag.title}</p>
          <p className="mt-1 text-[13px] text-[color:var(--text-secondary)]">{flag.description}</p>
          <p className="mt-2 text-[12px] italic text-[color:var(--accent-primary)]">{flag.action}</p>
          <p className="mt-1 text-[11px] text-[color:var(--text-tertiary)]">{flag.repo_name} · {flag.loads_30d} loads (30d)</p>
        </div>
        <DismissButton onDismiss={() => onDismiss(flag)} />
      </div>
    </div>
  );
}

function MultiRepoFlagRow({
  flag,
  onDismiss,
  onFix,
}: {
  flag: RedFlag;
  onDismiss: (flag: RedFlag) => void;
  onFix: (flag: RedFlag) => void;
}) {
  return (
    <div className="flex items-center justify-between border-t border-[color:var(--bg-elevated)] px-5 py-3 first:border-t-0">
      <div className="flex items-center gap-3 min-w-0">
        <span className="inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[rgb(var(--accent-primary-rgb)/0.12)] text-[11px] font-bold text-[color:var(--accent-primary)]">
          {flag.repo_name.charAt(0).toUpperCase()}
        </span>
        <div className="min-w-0">
          <span className="truncate text-[13px] font-semibold text-[color:var(--text-primary)]">{flag.repo_name}</span>
          {flag.loads_30d > 0 ? (
            <span className="ml-2 text-[11px] text-[color:var(--text-tertiary)]">{flag.loads_30d} loads (30d)</span>
          ) : null}
        </div>
      </div>
      <div className="flex items-center gap-2">
        <button
          className="text-[12px] font-semibold text-[color:var(--accent-primary)] hover:underline"
          onClick={() => onFix(flag)}
          type="button"
        >
          Fix →
        </button>
        <DismissButton onDismiss={() => onDismiss(flag)} />
      </div>
    </div>
  );
}

function DismissButton({ onDismiss }: { onDismiss: () => void }) {
  return (
    <button
      className="group inline-flex shrink-0 items-center gap-1 rounded-full border border-transparent px-2 py-1 text-[11px] font-semibold text-[color:var(--text-tertiary)] hover:border-[color:var(--bg-border)] hover:text-[color:var(--text-secondary)]"
      onClick={onDismiss}
      title="Dismiss — mark as not a risk"
      type="button"
    >
      <X className="h-3 w-3" />
      Not a risk
    </button>
  );
}

// ─── risk type matrix (summary bar) ─────────────────────────────────────────

function RiskMatrix({ groups }: { groups: GroupedFlag[] }) {
  const cells = [
    { label: "Stale & Active", type: "stale_but_active" },
    { label: "Zero Freshness", type: "freshness_critical" },
    { label: "Conflicting", type: "conflict" },
    { label: "Missing Security", type: "missing_security" },
    { label: "Dead Skills", type: "dead_high_quality" },
  ] as const;

  const countByType = new Map(groups.map((g) => [g.flag_type, g.flags.length]));

  return (
    <div className="mb-6 grid grid-cols-5 gap-2">
      {cells.map((cell) => {
        const count = countByType.get(cell.type) ?? 0;
        const meta = flagTypeMeta(cell.type);
        return (
          <div
            className={`rounded-xl border p-3 text-center ${count > 0 ? "border-[color:var(--bg-border)] bg-[color:var(--bg-surface)]" : "border-[color:var(--bg-elevated)] bg-[color:var(--bg-elevated)] opacity-40"}`}
            key={cell.type}
          >
            <div className={`text-[22px] font-bold ${count > 0 ? (meta.pill.includes("red") ? "text-red-400" : meta.pill.includes("amber") ? "text-amber-400" : "text-blue-400") : "text-[color:var(--text-tertiary)]"}`}>
              {count}
            </div>
            <div className="mt-1 text-[10px] font-semibold uppercase leading-tight tracking-wide text-[color:var(--text-tertiary)]">
              {cell.label}
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ─── main shell ──────────────────────────────────────────────────────────────

const DISMISSED_KEY = "skillayer_dismissed_flags_v1";

export function RedFlagsShell({ accessToken, orgId, redFlags }: { accessToken: string; orgId: string; redFlags: OrgRedFlags }) {
  const [dismissedIds, setDismissedIds] = useState<Set<string>>(new Set());
  const [fixModalFlag, setFixModalFlag] = useState<RedFlag | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function loadDismissals() {
      const ids = new Set<string>();
      try {
        const raw = localStorage.getItem(DISMISSED_KEY);
        if (raw) {
          for (const id of JSON.parse(raw) as string[]) ids.add(id);
        }
      } catch {
        // Local fallback can be absent or malformed.
      }

      if (orgId) {
        try {
          const response = await fetch(`${CLIENT_API_URL}/orgs/${orgId}/red-flags/dismissed`, {
            headers: buildHeaders(accessToken),
          });
          if (response.ok) {
            const dismissals = (await response.json()) as RedFlagDismissal[];
            for (const dismissal of dismissals) ids.add(dismissalId(dismissal));
          }
        } catch {
          // Keep localStorage-only dismissals when the API is unavailable.
        }
      }

      if (!cancelled) setDismissedIds(ids);
    }
    void loadDismissals();
    return () => {
      cancelled = true;
    };
  }, [accessToken, orgId]);

  useEffect(() => {
    try {
      localStorage.setItem(DISMISSED_KEY, JSON.stringify(Array.from(dismissedIds)));
    } catch {
      // ignore local fallback write
    }
  }, [dismissedIds]);

  const dismissFlag = useCallback((flag: RedFlag) => {
    const id = flagId(flag);
    setDismissedIds((prev) => {
      const next = new Set(prev);
      next.add(id);
      return next;
    });
    if (orgId) {
      fetch(`${CLIENT_API_URL}/orgs/${orgId}/red-flags/dismiss`, {
        method: "POST",
        headers: buildHeaders(accessToken),
        body: JSON.stringify({ flag_type: flag.flag_type, repo_id: flag.repo_id, skill_id: flag.skill_id, reason: "not_a_risk" }),
      }).catch(() => {
        // localStorage already holds fallback state.
      });
    }
  }, [accessToken, orgId]);

  const restoreAll = useCallback(() => {
    const currentDismissedIds = new Set(dismissedIds);
    setDismissedIds(new Set());
    try {
      localStorage.removeItem(DISMISSED_KEY);
    } catch {
      // ignore
    }
    if (orgId) {
      redFlags.flags
        .filter((flag) => currentDismissedIds.has(flagId(flag)))
        .forEach((flag) => {
          fetch(`${CLIENT_API_URL}/orgs/${orgId}/red-flags/dismiss`, {
            method: "DELETE",
            headers: buildHeaders(accessToken),
            body: JSON.stringify({ flag_type: flag.flag_type, repo_id: flag.repo_id, skill_id: flag.skill_id }),
          }).catch(() => {
            // Local restore has already completed.
          });
        });
    }
  }, [accessToken, dismissedIds, orgId, redFlags.flags]);

  const groups = groupFlags(redFlags.flags);
  const activeGroups = groups.map((g) => ({
    ...g,
    flags: g.flags.filter((f) => !dismissedIds.has(flagId(f))),
  })).filter((g) => g.flags.length > 0);

  const dismissedCount = dismissedIds.size;
  const totalActive = activeGroups.reduce((sum, g) => sum + g.flags.length, 0);

  if (redFlags.flags.length === 0) {
    return (
      <div className="rounded-xl border border-[rgb(var(--accent-green-rgb)/0.25)] bg-[rgb(var(--accent-green-rgb)/0.12)] px-5 py-4 text-[13px] font-semibold text-[color:var(--accent-green)]">
        ✓ No red flags detected across your org.
      </div>
    );
  }

  return (
    <div>
      <RiskMatrix groups={groups} />

      {totalActive === 0 ? (
        <div className="rounded-xl border border-[rgb(var(--accent-green-rgb)/0.25)] bg-[rgb(var(--accent-green-rgb)/0.12)] px-5 py-6 text-center">
          <div className="text-[15px] font-semibold text-[color:var(--accent-green)]">✓ All flags dismissed</div>
          <p className="mt-1 text-[13px] text-[color:var(--text-tertiary)]">
            You've reviewed all flags. {dismissedCount} dismissed.
          </p>
          <button
            className="mt-3 text-[12px] font-semibold text-[color:var(--accent-primary)] hover:underline"
            onClick={restoreAll}
            type="button"
          >
            Restore all
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {activeGroups.map((group) => (
            <GroupedFlagCard
              dismissedIds={dismissedIds}
              group={group}
              key={group.flag_type}
              onDismissFlag={dismissFlag}
              onOpenFix={setFixModalFlag}
            />
          ))}
        </div>
      )}

      {dismissedCount > 0 ? (
        <div className="mt-4 flex items-center justify-between rounded-xl border border-[color:var(--bg-border)] bg-[color:var(--bg-surface)] px-4 py-3">
          <span className="text-[13px] text-[color:var(--text-tertiary)]">
            {dismissedCount} flag{dismissedCount !== 1 ? "s" : ""} dismissed as &quot;not a risk&quot;
          </span>
          <button
            className="text-[12px] font-semibold text-[color:var(--accent-primary)] hover:underline"
            onClick={restoreAll}
            type="button"
          >
            Restore all
          </button>
        </div>
      ) : null}

      {fixModalFlag ? (
        <FixModal flag={fixModalFlag} onClose={() => setFixModalFlag(null)} />
      ) : null}
    </div>
  );
}
