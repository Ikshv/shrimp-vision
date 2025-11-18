/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone', // Enable standalone output for Docker
  images: {
    domains: ['localhost', 'backend'],
    unoptimized: true
  },
  webpack: (config, { isServer }) => {
    // Ensure path aliases work in Docker build
    const path = require('path')
    const rootPath = path.resolve(__dirname)
    
    // Override alias resolution to match tsconfig.json paths
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': rootPath,
      '@/lib': path.join(rootPath, 'lib'),
    }
    
    // Ensure modules are resolved from the project root
    config.resolve.modules = [
      ...(config.resolve.modules || []),
      rootPath,
    ]
    
    // Ensure extensions are resolved
    config.resolve.extensions = [
      ...config.resolve.extensions,
      '.ts',
      '.tsx',
    ]
    
    return config
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
