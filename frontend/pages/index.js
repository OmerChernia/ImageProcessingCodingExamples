import Link from 'next/link';

export default function Home() {
  const tools = [
    { name: 'Brightness Adjustment', href: '/brightness' },
    { name: '2-Pointer Algorithm', href: '/2pointer' },
    { name: 'Contrast Stretching', href: '/contrast' },
    { name: 'Gamma Correction', href: '/gamma' },
    { name: 'Histogram Equalization', href: '/histogram' },
    { name: 'Transformations', href: '/transformations' },
  ];

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Image Processing Tools</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {tools.map((tool) => (
          <Link
            key={tool.href}
            href={tool.href}
            className="p-4 border rounded hover:bg-gray-50 transition-colors"
          >
            <h2 className="text-lg font-medium">{tool.name}</h2>
          </Link>
        ))}
      </div>
    </div>
  );
} 