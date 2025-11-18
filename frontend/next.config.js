/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone', // Enable standalone output for Docker
  images: {
    domains: ['localhost', 'backend'],
    unoptimized: true
  },
  async rewrites() {
    // Use environment variable for backend URL, fallback to localhost for dev
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3100'
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
      {
        source: '/static/:path*',
        destination: `${backendUrl}/static/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
