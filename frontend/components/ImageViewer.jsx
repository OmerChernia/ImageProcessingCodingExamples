import React from 'react';

export default function ImageViewer({ src }) {
  if (!src) {
    return <div>No image selected.</div>;
  }
  return (
    <div className="border p-4">
      <img src={src} alt="Uploaded" className="max-w-full h-auto" />
    </div>
  );
} 