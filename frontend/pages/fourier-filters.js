import { useState } from 'react';
import HistogramChart from '../components/HistogramChart';

function ImageWithSpectrum({ imageUrl, spectrumUrl, title }) {
  if (!imageUrl) return null;

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">{title}</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-gray-50 rounded-lg p-4 flex items-center justify-center">
          <img
            src={imageUrl}
            alt="Image"
            className="max-w-full h-auto object-contain rounded shadow-sm"
            style={{ maxHeight: '300px' }}
          />
        </div>
        {spectrumUrl && (
          <div className="bg-gray-50 rounded-lg p-4 flex items-center justify-center">
            <img
              src={spectrumUrl}
              alt="Spectrum"
              className="max-w-full h-auto object-contain rounded shadow-sm"
              style={{ maxHeight: '300px' }}
            />
          </div>
        )}
      </div>
    </div>
  );
}

export default function FourierFiltersPage() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [filterType, setFilterType] = useState('low_pass');
  const [radius, setRadius] = useState(30);
  const [innerRadius, setInnerRadius] = useState(20);
  const [outerRadius, setOuterRadius] = useState(40);
  const [useGaussian, setUseGaussian] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [processedData, setProcessedData] = useState(null);
  const [addDC, setAddDC] = useState(false);

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
    formData.append('filter_type', filterType);
    formData.append('gaussian', useGaussian);
    formData.append('add_dc', addDC);

    if (filterType === 'band_pass') {
      formData.append('inner_radius', innerRadius);
      formData.append('outer_radius', outerRadius);
    } else {
      formData.append('radius', radius);
    }

    try {
      const response = await fetch('http://localhost:8000/api/fourier-filter', {
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
    if (!processedData?.filteredImage) return;
    
    const link = document.createElement('a');
    link.href = processedData.filteredImage;
    link.download = 'filtered_image.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4 max-w-6xl">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Fourier Domain Filtering</h1>

        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <div className="space-y-6">
            {/* Image Input */}
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
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100"
              />
            </div>

            {/* Filter Controls */}
            {selectedImage && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Filter Type
                  </label>
                  <select
                    value={filterType}
                    onChange={(e) => setFilterType(e.target.value)}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                  >
                    <option value="low_pass">Low Pass</option>
                    <option value="high_pass">High Pass</option>
                    <option value="band_pass">Band Pass</option>
                  </select>
                </div>

                {filterType === 'band_pass' ? (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Inner Radius
                      </label>
                      <input
                        type="range"
                        min="10"
                        max="100"
                        value={innerRadius}
                        onChange={(e) => setInnerRadius(Number(e.target.value))}
                        className="w-full"
                      />
                      <span className="text-sm text-gray-500">{innerRadius}</span>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Outer Radius
                      </label>
                      <input
                        type="range"
                        min={innerRadius}
                        max="100"
                        value={outerRadius}
                        onChange={(e) => setOuterRadius(Number(e.target.value))}
                        className="w-full"
                      />
                      <span className="text-sm text-gray-500">{outerRadius}</span>
                    </div>
                  </div>
                ) : (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Radius
                    </label>
                    <input
                      type="range"
                      min="10"
                      max="100"
                      value={radius}
                      onChange={(e) => setRadius(Number(e.target.value))}
                      className="w-full"
                    />
                    <span className="text-sm text-gray-500">{radius}</span>
                  </div>
                )}

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="gaussian"
                    checked={useGaussian}
                    onChange={(e) => setUseGaussian(e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="gaussian" className="ml-2 block text-sm text-gray-900">
                    Use Gaussian Smoothing
                  </label>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="addDC"
                    checked={addDC}
                    onChange={(e) => setAddDC(e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="addDC" className="ml-2 block text-sm text-gray-900">
                    Add DC Component (128)
                  </label>
                </div>

                <button
                  onClick={handleSubmit}
                  disabled={loading}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-lg font-medium
                    hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                    disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {loading ? 'Processing...' : 'Apply Filter'}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Results Display */}
        {previewUrl && (
          <div className="space-y-8">
            <ImageWithSpectrum
              imageUrl={previewUrl}
              spectrumUrl={processedData?.originalSpectrum}
              title="Original"
            />

            {processedData && (
              <>
                <ImageWithSpectrum
                  imageUrl={processedData.filteredImage}
                  spectrumUrl={processedData.filteredSpectrum}
                  title="Filtered Result"
                />

                <div className="mt-4">
                  <button
                    onClick={handleDownload}
                    className="w-full bg-green-600 text-white px-4 py-2 rounded-lg font-medium
                      hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2
                      transition-all"
                  >
                    Download Filtered Image
                  </button>
                </div>
              </>
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