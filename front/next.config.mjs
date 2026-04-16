/** @type {import('next').NextConfig} */
const isStaticExport = process.env.STATIC_EXPORT === "1";

const nextConfig = isStaticExport
  ? {
      output: "export",
    }
  : {
      async headers() {
        return [
          {
            source: "/data/:path*",
            headers: [
              {
                key: "Cache-Control",
                value: "public, max-age=0, s-maxage=86400, stale-while-revalidate=604800",
              },
            ],
          },
        ];
      },
    };

export default nextConfig;
