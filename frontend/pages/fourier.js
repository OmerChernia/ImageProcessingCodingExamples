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

export default function FourierPage() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [centerSpectrum, setCenterSpectrum] = useState(false);
  const [applyLog, setApplyLog] = useState(false);
  const [magnitudeSpectrumUrl, setMagnitudeSpectrumUrl] = useState(null);
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
    formData.append('center_spectrum', centerSpectrum);
    formData.append('apply_log', applyLog);

    try {
      const response = await fetch('http://localhost:8000/api/fourier', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to process image');
      }

      const data = await response.json();
      setMagnitudeSpectrumUrl(data.magnitudeSpectrum);
      setHistogramData({
        original: {
          histogram: data.originalHistogram,
          cumulative: data.originalCumulative
        },
        spectrum: {
          histogram: data.spectrumHistogram,
          cumulative: data.spectrumCumulative
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
    if (!magnitudeSpectrumUrl || !selectedImage) return;

    try {
      // Get original filename without extension
      const originalName = selectedImage.name.replace(/\.[^/.]+$/, '');
      
      // Remove the data URL prefix to get just the base64 string
      const base64Data = magnitudeSpectrumUrl.replace('data:image/png;base64,', '');
      
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
      link.download = `${originalName}_magnitude_spectrum${centerSpectrum ? '_centered' : ''}${applyLog ? '_log' : ''}.png`;
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
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Fourier Transform</h1>
        
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <div className="space-y-6">
            {/* File Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Image
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={handleImageSelect}
                className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4
                  file:rounded-full file:border-0 file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
            </div>

            {selectedImage && (
              <>
                {/* Options */}
                <div className="space-y-4">
                  <div>
                    <label className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        checked={centerSpectrum}
                        onChange={(e) => setCenterSpectrum(e.target.checked)}
                        className="form-checkbox h-5 w-5 text-blue-600 rounded focus:ring-blue-500"
                      />
                      <span className="text-sm font-medium text-gray-700">
                        Center the spectrum
                      </span>
                    </label>
                  </div>

                  <div>
                    <label className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        checked={applyLog}
                        onChange={(e) => setApplyLog(e.target.checked)}
                        className="form-checkbox h-5 w-5 text-blue-600 rounded focus:ring-blue-500"
                      />
                      <span className="text-sm font-medium text-gray-700">
                        Apply log transform to magnitude spectrum
                      </span>
                    </label>
                  </div>
                </div>

                {/* Process Button */}
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

        {/* Results Display */}
        {previewUrl && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <ImageWithHistograms
              imageUrl={previewUrl}
              histogramData={histogramData?.original}
              title="Original Image"
            />
            {magnitudeSpectrumUrl && (
              <ImageWithHistograms
                imageUrl={magnitudeSpectrumUrl}
                histogramData={histogramData?.spectrum}
                title="Magnitude Spectrum"
              />
            )}
          </div>
        )}

        {/* Download Button */}
        {magnitudeSpectrumUrl && (
          <div className="mt-4">
            <button
              onClick={handleDownload}
              className="w-full bg-green-600 text-white px-4 py-2 rounded-lg font-medium
                hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2
                transition-all"
            >
              Download Magnitude Spectrum
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