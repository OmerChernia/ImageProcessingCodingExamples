/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    loader: 'custom',
    unoptimized: true
  },
  swcMinify: false
}

module.exports = nextConfig 