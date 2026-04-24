import type { NextConfig } from "next";

// "standalone" is needed for Docker/self-hosted deployments only.
// Vercel handles its own bundling and must NOT receive a standalone build
// (standalone embeds absolute node_modules paths in trace files that break
// Vercel's prebuilt deployment runner).  Set BUILD_STANDALONE=1 in the
// Docker build environment to opt in.
const nextConfig: NextConfig = {
  transpilePackages: ["@skillayer/config", "@skillayer/types", "@skillayer/ui"],
  ...(process.env.BUILD_STANDALONE === "1" ? { output: "standalone" } : {}),
};

export default nextConfig;
