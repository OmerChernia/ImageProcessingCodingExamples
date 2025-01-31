import { useState } from 'react';
import { useRouter } from 'next/router';

export default function CannyPage() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [processedImageUrl, setProcessedImageUrl] = useState(null);
  const [lowThreshold, setLowThreshold] = useState(50);
  const [highThreshold, setHighThreshold] = useState(150);
  const [sigma, setSigma] = useState(1.0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedImage) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('image', selectedImage);
    formData.append('low_threshold', lowThreshold.toString());
    formData.append('high_threshold', highThreshold.toString());
    formData.append('sigma', sigma.toString());

    try {
      const response = await fetch('http://localhost:8000/api/canny-edge', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to process image');
      }

      const data = await response.json();
      setProcessedImageUrl(data.processedImage);
    } catch (err) {
      setError(err.message);
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 py-8">
      <div className="container mx-auto px-4 max-w-7xl">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Canny Edge Detection</h1>
        
        {/* Controls Panel */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <div className="space-y-6">
            {/* File Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload Image
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={handleImageSelect}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100"
              />
            </div>

            {selectedImage && (
              <>
                {/* Low Threshold */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Low Threshold: {lowThreshold}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={lowThreshold}
                    onChange={(e) => setLowThreshold(parseInt(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                </div>

                {/* High Threshold */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    High Threshold: {highThreshold}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="200"
                    value={highThreshold}
                    onChange={(e) => setHighThreshold(parseInt(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                </div>

                {/* Sigma */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sigma: {sigma.toFixed(1)}
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="5.0"
                    step="0.1"
                    value={sigma}
                    onChange={(e) => setSigma(parseFloat(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                </div>

                {/* Process Button */}
                <button
                  onClick={handleSubmit}
                  disabled={loading}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg font-medium
                    hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                    disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Processing...' : 'Apply Edge Detection'}
                </button>
              </>
            )}
          </div>
        </div>

        {/* Results Display */}
        {previewUrl && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Original Image */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Original Image</h2>
              <div className="bg-gray-50 rounded-lg p-4">
                <img
                  src={previewUrl}
                  alt="Original"
                  className="max-w-full h-auto"
                />
              </div>
            </div>

            {/* Processed Image */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">Edge Detection Result</h2>
              <div className="bg-gray-50 rounded-lg p-4">
                {processedImageUrl ? (
                  <img
                    src={processedImageUrl}
                    alt="Processed"
                    className="max-w-full h-auto"
                  />
                ) : (
                  <div className="flex items-center justify-center h-48 text-gray-500">
                    Process an image to see the result
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-lg">
            {error}
          </div>
        )}
      </div>
    </div>
  );
} 