/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'shared.cloudflare.steamstatic.com',
      },
      {
        protocol: 'https',
        hostname: 'cdn.cloudflare.steamstatic.com',
      },
      {
        protocol: 'https',
        hostname: 'images.igdb.com',
      }
    ],
  },
  async rewrites() {
    const internalApi = process.env.INTERNAL_API_URL || 'http://127.0.0.1:8000';
    return [
      {
        source: '/api/v1/:path*',
        destination: `${internalApi}/api/v1/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
