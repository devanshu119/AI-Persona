/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    BACKEND_URL: process.env.BACKEND_URL || "http://localhost:8000",
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000",
    NEXT_PUBLIC_CALCOM_USERNAME: process.env.NEXT_PUBLIC_CALCOM_USERNAME || "devanshu",
  },
};

export default nextConfig;
