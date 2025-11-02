/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost'],
    unoptimized: true
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:3100/api/:path*',
      },
      {
        source: '/static/:path*',
        destination: 'http://localhost:3100/static/:path*',
      },
    ]
  },
}

module.exports = nextConfig
