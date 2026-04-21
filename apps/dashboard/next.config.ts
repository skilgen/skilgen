import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@skillayer/config", "@skillayer/types", "@skillayer/ui"],
  output: "standalone",
};

export default nextConfig;
