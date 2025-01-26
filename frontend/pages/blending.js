import { useState } from 'react';

function ImageDisplay({ imageUrl, title }) {
  if (!imageUrl) return null;
  return (
    <div className="bg-white rounded-xl shadow-lg p-4">
      <h3 className="text-lg font-semibold text-gray-800 mb-2">{title}</h3>
      <div className="bg-gray-50 rounded-lg p-2 flex items-center justify-center">
        <img
          src={imageUrl}
          alt={title}
          className="max-w-full h-auto object-contain rounded"
          style={{ maxHeight: '200px' }}
        />
      </div>
    </div>
  );
}

function PyramidDisplay({ images, title }) {
  if (!images?.length) return null;
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold text-gray-800">{title}</h2>
      <div className="grid grid-cols-1 gap-4">
        {images.map((img, i) => (
          <ImageDisplay
            key={i}
            imageUrl={img}
            title={`Level ${i + 1}`}
          />
        ))}
      </div>
    </div>
  );
}

export default function BlendingPage() {
  const [image1, setImage1] = useState(null);
  const [image2, setImage2] = useState(null);
  const [preview1, setPreview1] = useState(null);
  const [preview2, setPreview2] = useState(null);
  const [levels, setLevels] = useState(4);
  const [blendPosition, setBlendPosition] = useState(0.5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [maxLevels, setMaxLevels] = useState(10);
  const [blendType, setBlendType] = useState("full");

  const calculateMaxLevels = (imageWidth, imageHeight) => {
    const minDimension = Math.min(imageWidth, imageHeight);
    const maxLevels = Math.floor(Math.log2(minDimension)) - 2;
    return Math.max(2, maxLevels);
  };

  const handleImage1Select = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage1(file);
      const img = new Image();
      img.onload = () => {
        const newMaxLevels = calculateMaxLevels(img.width, img.height);
        setMaxLevels(newMaxLevels);
        if (levels > newMaxLevels) {
          setLevels(newMaxLevels);
        }
        URL.revokeObjectURL(img.src);
      };
      const url = URL.createObjectURL(file);
      setPreview1(url);
      img.src = url;
      setResult(null);
    }
  };

  const handleImage2Select = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage2(file);
      setPreview2(URL.createObjectURL(file));
      setResult(null);
    }
  };

  const handleSubmit = async () => {
    if (!image1 || !image2) {
      setError("Please select both images");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('image1', image1);
      formData.append('image2', image2);
      formData.append('levels', Math.round(levels).toString());
      formData.append('blend_position', blendPosition.toString());
      formData.append('blend_type', blendType);

      const response = await fetch('http://localhost:8000/image/blend', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
          const errorData = await response.json();
          throw new Error(errorData.detail || errorData.error || 'Failed to process images');
        } else {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
      }

      const contentType = response.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        throw new Error("Received non-JSON response from server");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error('Error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!result?.result) return;
    
    const link = document.createElement('a');
    link.href = result.result;
    link.download = 'blended_image.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4 max-w-7xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Multi-Band Blending</h1>
          <p className="text-xl text-gray-600">
            Blend two images smoothly using Laplacian pyramids
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Image Upload Controls */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                First Image
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={handleImage1Select}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-full file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100"
              />
              {preview1 && (
                <div className="mt-2">
                  <img
                    src={preview1}
                    alt="Preview 1"
                    className="max-h-40 rounded"
                  />
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Second Image
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={handleImage2Select}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-full file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100"
              />
              {preview2 && (
                <div className="mt-2">
                  <img
                    src={preview2}
                    alt="Preview 2"
                    className="max-h-40 rounded"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Controls */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            {/* Blend Type Selector */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Blend Type
              </label>
              <select
                value={blendType}
                onChange={(e) => setBlendType(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm
                  focus:border-blue-500 focus:ring-blue-500"
              >
                <option value="full">Gaussian Blend</option>
                <option value="half">Left-Right Split</option>
              </select>
              <span className="text-sm text-gray-500">
                {blendType === "full" 
                  ? "Smooth transition between images" 
                  : "Sharp split between left and right"}
              </span>
            </div>

            {/* Levels Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Pyramid Levels (2-{maxLevels})
              </label>
              <input
                type="number"
                min="2"
                max={maxLevels}
                value={levels}
                onChange={(e) => setLevels(Math.min(parseInt(e.target.value), maxLevels))}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm
                  focus:border-blue-500 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-500">
                Maximum levels possible: {maxLevels}
              </span>
            </div>

            {/* Position Slider */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {blendType === "full" ? "Blend Position" : "Split Position"} (0-1)
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={blendPosition}
                onChange={(e) => setBlendPosition(parseFloat(e.target.value))}
                className="mt-1 block w-full"
              />
              <span className="text-sm text-gray-500">
                {blendType === "full" 
                  ? `Center of blend: ${blendPosition}` 
                  : `Split at position: ${blendPosition}`}
              </span>
            </div>
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading || !image1 || !image2}
            className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg font-medium
              hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
              disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {loading ? 'Processing...' : 'Blend Images'}
          </button>

          {error && (
            <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
              {error}
            </div>
          )}
        </div>

        {/* Results */}
        {result && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <PyramidDisplay
                images={result.pyramid1}
                title="First Image Pyramid"
              />
              <PyramidDisplay
                images={result.pyramid2}
                title="Second Image Pyramid"
              />
              <PyramidDisplay
                images={result.blendedPyramid}
                title="Blended Pyramid"
              />
            </div>

            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Final Result</h2>
              <div className="bg-gray-50 rounded-lg p-4 flex items-center justify-center">
                <img
                  src={result.result}
                  alt="Blended Result"
                  className="max-w-full h-auto object-contain rounded shadow-sm"
                  style={{ maxHeight: '400px' }}
                />
              </div>
              <button
                onClick={handleDownload}
                className="mt-4 w-full bg-green-600 text-white px-4 py-2 rounded-lg font-medium
                  hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2
                  transition-all"
              >
                Download Result
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 