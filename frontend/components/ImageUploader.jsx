import React, { useState } from 'react';

export default function ImageUploader({ onUpload }) {
  const [file, setFile] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (file && onUpload) {
      onUpload(file);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 border rounded">
      <input type="file" accept="image/*" onChange={handleFileChange} />
      <button type="submit" className="ml-2 px-4 py-2 bg-blue-500 text-white rounded">
        Upload
      </button>
    </form>
  );
} 