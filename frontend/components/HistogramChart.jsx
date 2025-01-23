import React from 'react';

export default function HistogramChart({ data = [], title, color = 'blue' }) {
  if (!data || data.length === 0) return null;
  
  const maxValue = Math.max(...data);
  
  return (
    <div className="w-full bg-white p-4 rounded-lg shadow-md">
      <h3 className="text-sm font-medium text-gray-700 mb-2">{title}</h3>
      <div className="relative h-40 bg-gray-50 rounded border border-gray-200">
        <div className="absolute inset-0 flex items-end">
          {data.map((value, index) => {
            const height = (value / maxValue) * 100;
            return (
              <div
                key={index}
                className="group relative flex-1 h-full"
              >
                <div
                  className={`absolute bottom-0 w-full transition-all duration-200 ${
                    color === 'blue' ? 'bg-blue-500 hover:bg-blue-600' : 'bg-red-500 hover:bg-red-600'
                  }`}
                  style={{
                    height: `${height}%`,
                  }}
                />
                <div className="opacity-0 group-hover:opacity-100 absolute bottom-full left-1/2 -translate-x-1/2 px-2 py-1 bg-black text-white text-xs rounded pointer-events-none whitespace-nowrap z-10">
                  Intensity: {index}<br />
                  Count: {Math.round(value)}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
} 