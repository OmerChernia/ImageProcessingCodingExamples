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

export default function HistogramPage() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [processedImageUrl, setProcessedImageUrl] = useState(null);
  const [histogramData, setHistogramData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleImageSelect = async (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
      
      // Compute histogram for the original image
      const formData = new FormData();
      formData.append('image', file);
      
      try {
        const response = await fetch('http://localhost:8000/api/compute-histogram', {
          method: 'POST',
          body: formData,
        });
        
        if (!response.ok) throw new Error('Failed to compute histogram');
        
        const data = await response.json();
        setHistogramData({
          original: {
            histogram: data.data.histogram,
            cumulative: data.data.cumulative
          }
        });
      } catch (error) {
        console.error('Error computing histogram:', error);
      }
    }
  };

  const handleImageUpload = async (file) => {
    setError(null);
    setLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('image', file);

      const response = await fetch('http://localhost:8000/api/equalize', {
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedImage) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('image', selectedImage);

    try {
        console.log('Sending request to:', `${process.env.NEXT_PUBLIC_API_URL}/image/histogram`);
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/image/histogram`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to process image');
        }

        const data = await response.json();
        console.log('Received data:', data);
        setProcessedImageUrl(data.processedImage);
        setHistogramData(data.histogramData);
    } catch (err) {
        console.error('Error:', err);
        setError(err.message);
    } finally {
        setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!processedImageUrl || !selectedImage) return;

    try {
      // Get original filename without extension
      const originalName = selectedImage.name.replace(/\.[^/.]+$/, '');
      
      // Remove the data URL prefix to get just the base64 string
      const base64Data = processedImageUrl.replace('data:image/png;base64,', '');
      
      // Convert base64 to blob
      const byteCharacters = atob(base64Data);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: 'image/png' });

      // Create download link with meaningful filename
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${originalName}_equalized.png`;
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
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Histogram Equalization</h1>
        
        {/* Controls Panel */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <div className="space-y-6">
            {/* File Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload Image
              </label>
              <div className="mt-1 flex items-center">
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
            </div>

            {/* Process Button */}
            {selectedImage && (
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg font-medium
                  hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                  disabled:opacity-50 disabled:cursor-not-allowed transition-all"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing...
                  </span>
                ) : (
                  'Equalize Histogram'
                )}
              </button>
            )}
          </div>
        </div>

        {/* Results - Side by Side */}
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
                histogramData={{
                  histogram: histogramData?.processed?.histogram,
                  cumulative: histogramData?.processed?.cumulative
                }}
                title="Equalized Image"
              />
            ) : (
              <div className="bg-white rounded-xl shadow-lg p-6 flex items-center justify-center">
                <p className="text-gray-500">Process the image to see the result</p>
              </div>
            )}
          </div>
        )}

        {/* Download Button */}
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
      </div>
    </div>
  );
} 