import type { Org, OrgStats, Repo, User } from "@skillayer/types";

export const mockUser: User = {
  id: "user_01",
  email: "ravi@skillayer.com",
  firstName: "Ravi",
  lastName: "Chandu",
  avatarUrl: null,
  role: "owner",
};

export const mockOrg: Org = {
  id: "org_01",
  name: "Skillayer",
  slug: "skillayer",
  plan: "business",
  repoCount: 12,
  seatCount: 8,
};

export const mockRepo: Repo = {
  id: "repo_01",
  name: "skillayer-web",
  fullName: "skillayer/skillayer-web",
  score: {
    total: 84,
    groundedness: 22,
    coverage: 20,
    freshness: 21,
    structure: 21,
  },
  scoreDelta: 4,
  lastAnalysed: "2026-04-19T12:00:00.000Z",
  skillCount: 18,
  ownerId: "org_01",
  ownerLogin: "skillayer",
  language: "TypeScript",
  isMonorepo: true,
};

export const mockOrgStats: OrgStats = {
  repoCount: 12,
  avgScore: 84,
  skillCount: 186,
  activeAgentSessions: 9,
  scoreTrend: [
    { date: "2026-04-13", score: 72 },
    { date: "2026-04-14", score: 74 },
    { date: "2026-04-15", score: 76 },
    { date: "2026-04-16", score: 79 },
    { date: "2026-04-17", score: 81 },
    { date: "2026-04-18", score: 83 },
    { date: "2026-04-19", score: 84 },
  ],
  topRepo: mockRepo,
  worstRepo: mockRepo,
};

export const dashboardNavItems = [
  { href: "/dashboard", label: "Overview", icon: "LayoutDashboard" as const },
  { href: "/dashboard/repos", label: "Repos", icon: "GitBranch" as const },
  { href: "/dashboard/skills", label: "Skills", icon: "BookOpen" as const },
  { href: "/dashboard/registry", label: "Registry", icon: "Package" as const },
  { href: "/dashboard/settings", label: "Settings", icon: "Settings" as const },
];
