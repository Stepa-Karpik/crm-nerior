/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  experimental: {},
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8300/api/v1',
    NEXT_PUBLIC_ADMIN_URL: process.env.NEXT_PUBLIC_ADMIN_URL || 'https://admin.nerior.ru',
    NEXT_PUBLIC_PLANNER_URL: process.env.NEXT_PUBLIC_PLANNER_URL || 'https://planner.nerior.ru',
    NEXT_PUBLIC_DOCUMENTS_URL: process.env.NEXT_PUBLIC_DOCUMENTS_URL || 'https://documents.nerior.ru'
  }
}
export default nextConfig
