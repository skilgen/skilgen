import type { Config } from "tailwindcss";
import baseConfig from "@skillayer/config/tailwind";

const config: Config = {
  ...baseConfig,
  content: ["./app/**/*.{ts,tsx}", "./src/**/*.{ts,tsx}", "../../packages/ui/src/**/*.{ts,tsx}"],
};

export default config;
