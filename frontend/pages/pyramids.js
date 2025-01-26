import { useState } from 'react';

function ImageDisplay({ imageUrl, title }) {
  if (!imageUrl) return null;

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">{title}</h2>
      <div className="bg-gray-50 rounded-lg p-4 flex items-center justify-center">
        <img
          src={imageUrl}
          alt={title}
          className="max-w-full h-auto object-contain rounded shadow-sm"
          style={{ maxHeight: '300px' }}
        />
      </div>
    </div>
  );
}

export default function PyramidsPage() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [levels, setLevels] = useState(3);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [processedData, setProcessedData] = useState(null);

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
      setProcessedData(null);
    }
  };

  const handleSubmit = async () => {
    if (!selectedImage) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('image', selectedImage);
    formData.append('levels', levels);

    try {
      const response = await fetch('http://localhost:8000/api/pyramids', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to process image');
      }

      const data = await response.json();
      setProcessedData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!processedData?.reconstructedImage) return;
    
    // Create temporary link and trigger download
    const link = document.createElement('a');
    link.href = processedData.reconstructedImage;
    link.download = 'reconstructed_image.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4 max-w-7xl">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Image Pyramids</h1>

        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <div className="space-y-6">
            {/* Image Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Image
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={handleImageSelect}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-full file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100"
              />
            </div>

            {/* Pyramid Levels */}
            {selectedImage && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Number of Pyramid Levels
                </label>
                <div className="flex items-center space-x-4">
                  <input
                    type="range"
                    min="3"
                    max="6"
                    value={levels}
                    onChange={(e) => setLevels(parseInt(e.target.value))}
                    className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                  />
                  <span className="text-sm text-gray-600 w-12 text-right">{levels}</span>
                </div>
              </div>
            )}

            {/* Process Button */}
            {selectedImage && (
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg font-medium
                  hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                  disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? 'Processing...' : 'Process Image'}
              </button>
            )}
          </div>
        </div>

        {/* Results Display */}
        {previewUrl && (
          <div className="space-y-8">
            <ImageDisplay
              imageUrl={previewUrl}
              title="Original Image"
            />

            {processedData && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Gaussian Pyramid Column */}
                <div className="space-y-6">
                  <h3 className="text-xl font-semibold text-gray-800">Gaussian Pyramid</h3>
                  {processedData.gaussianPyramid.map((img, i) => (
                    <ImageDisplay
                      key={`gaussian-${i}`}
                      imageUrl={img}
                      title={`Level ${i + 1}`}
                    />
                  ))}
                </div>

                {/* Laplacian Pyramid Column */}
                <div className="space-y-6">
                  <h3 className="text-xl font-semibold text-gray-800">Laplacian Pyramid</h3>
                  {processedData.laplacianPyramid.map((img, i) => (
                    <ImageDisplay
                      key={`laplacian-${i}`}
                      imageUrl={img}
                      title={`Level ${i + 1}`}
                    />
                  ))}
                </div>
              </div>
            )}

            {processedData && (
              <div className="mt-8">
                <ImageDisplay
                  imageUrl={processedData.reconstructedImage}
                  title="Reconstructed Image"
                />

                <div className="mt-4">
                  <button
                    onClick={handleDownload}
                    className="w-full bg-green-600 text-white px-4 py-2 rounded-lg font-medium
                      hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2
                      transition-all"
                  >
                    Download Reconstructed Image
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
            {error}
          </div>
        )}
      </div>
    </div>
  );
} 