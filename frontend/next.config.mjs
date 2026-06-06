/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    BACKEND_URL: process.env.BACKEND_URL || "https://ai-persona-cr8c.onrender.com",
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || "https://ai-persona-cr8c.onrender.com",
    NEXT_PUBLIC_CALCOM_USERNAME: process.env.NEXT_PUBLIC_CALCOM_USERNAME || "devanshu09",
  },
};

export default nextConfig;
