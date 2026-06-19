export type RiskLevel = "high" | "med" | "low";

export type SkilgenScore = {
  total: number;
  groundedness: number;
  coverage: number;
  freshness: number;
  structure: number;
};

export type Repo = {
  id: string;
  name: string;
  fullName: string;
  score: SkilgenScore;
  scoreDelta: number;
  lastAnalysed: string;
  skillCount: number;
  ownerId: string;
  ownerLogin: string;
  language: string;
  isMonorepo: boolean;
};

export type Skill = {
  id: string;
  repoId: string;
  domain: string;
  path: string;
  score: SkilgenScore;
  loadCount30d: number;
  lastLoadedAt: string | null;
  stale: boolean;
  inCycle: boolean;
  criticalityScore: number;
};

export type OrgStats = {
  repoCount: number;
  avgScore: number;
  skillCount: number;
  activeAgentSessions: number;
  scoreTrend: { date: string; score: number }[];
  topRepo: Repo | null;
  worstRepo: Repo | null;
};

export type User = {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  avatarUrl: string | null;
  role: "owner" | "admin" | "member";
};

export type Org = {
  id: string;
  name: string;
  slug: string;
  plan: "free" | "team" | "business" | "enterprise";
  repoCount: number;
  seatCount: number;
};
