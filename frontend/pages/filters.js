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

export default function FiltersPage() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [processedImageUrl, setProcessedImageUrl] = useState(null);
  const [histogramData, setHistogramData] = useState(null);
  const [filterSequence, setFilterSequence] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [kernelSize, setKernelSize] = useState(3);
  const [filterType, setFilterType] = useState('min');

  const handleImageSelect = async (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
      setFilterSequence([]);
      setProcessedImageUrl(null);
      
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

  const addFilter = (filterType) => {
    setFilterSequence([...filterSequence, filterType]);
  };

  const removeLastFilter = () => {
    setFilterSequence(filterSequence.slice(0, -1));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedImage) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('image', selectedImage);
    formData.append('kernel_size', kernelSize);
    formData.append('filter_type', filterType);

    try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/image/filters`, {
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
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      const filterSummary = filterSequence.join('-');
      link.download = `filtered_${filterSummary}.png`;
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
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Min-Max Filters</h1>
        
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
                  hover:file:bg-blue-100
                  transition-all"
              />
            </div>

            {/* Filter Controls */}
            {selectedImage && (
              <div className="space-y-4">
                <div className="flex gap-2">
                  <button
                    onClick={() => addFilter('min')}
                    className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg font-medium
                      hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                      transition-all"
                  >
                    Add Min Filter
                  </button>
                  <button
                    onClick={() => addFilter('max')}
                    className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg font-medium
                      hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2
                      transition-all"
                  >
                    Add Max Filter
                  </button>
                </div>

                {filterSequence.length > 0 && (
                  <div className="space-y-2">
                    <div className="text-sm font-medium text-gray-700">
                      Filter Sequence:
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {filterSequence.map((filter, index) => (
                        <span
                          key={index}
                          className={`px-3 py-1 rounded-full text-sm font-medium
                            ${filter === 'min' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'}`}
                        >
                          {filter === 'min' ? 'Min' : 'Max'}
                        </span>
                      ))}
                    </div>
                    <button
                      onClick={removeLastFilter}
                      className="text-red-600 hover:text-red-700 text-sm font-medium"
                    >
                      Remove Last Filter
                    </button>
                  </div>
                )}

                <button
                  onClick={handleSubmit}
                  disabled={loading || filterSequence.length === 0}
                  className="w-full bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium
                    hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2
                    disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {loading ? 'Processing...' : 'Apply Filters'}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Results */}
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
                title="Filtered Image"
              />
            ) : (
              <div className="bg-white rounded-xl shadow-lg p-6 flex items-center justify-center">
                <p className="text-gray-500">Apply filters to see the result</p>
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
              Download Filtered Image
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