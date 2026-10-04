import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Keep the app root explicit when running inside a sandbox with other tooling.
  turbopack: { root: process.cwd() },
};

export default nextConfig;
