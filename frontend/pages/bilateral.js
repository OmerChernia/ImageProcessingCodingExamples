import { useState } from 'react';
import HistogramChart from '../components/HistogramChart';

function ImageWithHistograms({ imageUrl, histogramData, title }) {
  if (!imageUrl) return null;

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">{title}</h2>
      <div className="flex flex-col">
        <div className="bg-gray-50 rounded-lg p-4 flex items-center justify-center">
          <img
            src={imageUrl}
            alt={title}
            className="max-w-full h-auto object-contain rounded shadow-sm"
            style={{ maxHeight: '350px' }}
          />
        </div>
        
        {histogramData && (
          <div className="mt-4 grid grid-cols-1 gap-4">
            <HistogramChart 
              data={histogramData.histogram}
              title="Intensity Distribution"
              color="blue"
            />
            <HistogramChart 
              data={histogramData.cumulative}
              title="Cumulative Distribution"
              color="red"
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default function BilateralPage() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [diameter, setDiameter] = useState(9);
  const [sigmaColor, setSigmaColor] = useState(75);
  const [sigmaSpace, setSigmaSpace] = useState(75);
  const [processedImageUrl, setProcessedImageUrl] = useState(null);
  const [histogramData, setHistogramData] = useState(null);
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
    formData.append('d', diameter);
    formData.append('sigma_color', sigmaColor);
    formData.append('sigma_space', sigmaSpace);

    try {
      const response = await fetch('http://localhost:8000/api/bilateral', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to process image');
      }

      const data = await response.json();
      setProcessedImageUrl(data.processedImage);
      setHistogramData({
        original: {
          histogram: data.originalHistogram,
          cumulative: data.originalCumulative
        },
        processed: {
          histogram: data.processedHistogram,
          cumulative: data.processedCumulative
        }
      });
    } catch (err) {
      setError(err.message);
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!processedImageUrl || !selectedImage) return;

    try {
      const base64Data = processedImageUrl.replace('data:image/png;base64,', '');
      const byteCharacters = atob(base64Data);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'image/png' });
      
      const originalName = selectedImage.name.replace(/\.[^/.]+$/, '');
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${originalName}_bilateral.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading:', error);
      alert('Failed to download image');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 py-8">
      <div className="container mx-auto px-4 max-w-7xl">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Bilateral Filter</h1>
        
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <div className="space-y-6">
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
                  hover:file:bg-blue-100
                  transition-all"
              />
            </div>

            {selectedImage && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Diameter (d)
                  </label>
                  <div className="flex items-center gap-4">
                    <input
                      type="range"
                      min="3"
                      max="15"
                      step="2"
                      value={diameter}
                      onChange={(e) => setDiameter(parseInt(e.target.value))}
                      className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                    />
                    <span className="text-sm text-gray-600 w-12 text-right">{diameter}</span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sigma Color
                  </label>
                  <div className="flex items-center gap-4">
                    <input
                      type="range"
                      min="10"
                      max="150"
                      step="5"
                      value={sigmaColor}
                      onChange={(e) => setSigmaColor(parseInt(e.target.value))}
                      className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                    />
                    <span className="text-sm text-gray-600 w-12 text-right">{sigmaColor}</span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sigma Space
                  </label>
                  <div className="flex items-center gap-4">
                    <input
                      type="range"
                      min="10"
                      max="150"
                      step="5"
                      value={sigmaSpace}
                      onChange={(e) => setSigmaSpace(parseInt(e.target.value))}
                      className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                    />
                    <span className="text-sm text-gray-600 w-12 text-right">{sigmaSpace}</span>
                  </div>
                </div>

                <button
                  onClick={handleSubmit}
                  disabled={loading}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg font-medium
                    hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                    disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {loading ? 'Processing...' : 'Process Image'}
                </button>
              </>
            )}
          </div>
        </div>

        {previewUrl && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <ImageWithHistograms
              imageUrl={previewUrl}
              histogramData={histogramData?.original}
              title="Original Image"
            />
            
            {processedImageUrl ? (
              <ImageWithHistograms
                imageUrl={processedImageUrl}
                histogramData={histogramData?.processed}
                title="Processed Image"
              />
            ) : (
              <div className="bg-white rounded-xl shadow-lg p-6 flex items-center justify-center">
                <p className="text-gray-500">Process the image to see the result</p>
              </div>
            )}
          </div>
        )}

        {processedImageUrl && (
          <div className="mt-4">
            <button
              onClick={handleDownload}
              className="w-full bg-green-600 text-white px-4 py-2 rounded-lg font-medium
                hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2
                transition-all"
            >
              Download Processed Image
            </button>
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