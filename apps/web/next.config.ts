import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@skillayer/config", "@skillayer/types", "@skillayer/ui"],
};

export default nextConfig;
