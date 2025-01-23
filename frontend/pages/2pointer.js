import { useState } from 'react';
import HistogramChart from '../components/HistogramChart';
import MappingPlot from '../components/MappingPlot';

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

export default function TwoPointerPage() {
  const [selectedImageA, setSelectedImageA] = useState(null);
  const [selectedImageB, setSelectedImageB] = useState(null);
  const [previewUrlA, setPreviewUrlA] = useState(null);
  const [previewUrlB, setPreviewUrlB] = useState(null);
  const [histogramData, setHistogramData] = useState(null);
  const [mapping, setMapping] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleImageSelect = (e, isImageA) => {
    const file = e.target.files[0];
    if (file) {
      if (isImageA) {
        setSelectedImageA(file);
        setPreviewUrlA(URL.createObjectURL(file));
      } else {
        setSelectedImageB(file);
        setPreviewUrlB(URL.createObjectURL(file));
      }
    }
  };

  const handleSubmit = async () => {
    if (!selectedImageA || !selectedImageB) return;
    
    setError(null);
    setLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('image_a', selectedImageA);
      formData.append('image_b', selectedImageB);

      const response = await fetch('http://localhost:8000/api/2pointer', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to process images');
      }

      const data = await response.json();
      setHistogramData({
        imageA: {
          histogram: data.histogramA,
          cumulative: data.cumulativeA
        },
        imageB: {
          histogram: data.histogramB,
          cumulative: data.cumulativeB
        }
      });
      setMapping(data.mapping);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Two-Pointer Algorithm Analysis</h1>
      
      <div className="space-y-8">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Image A Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload Image A
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => handleImageSelect(e, true)}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100"
              />
            </div>

            {/* Image B Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload Image B
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => handleImageSelect(e, false)}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100"
              />
            </div>
          </div>

          {/* Process Button */}
          {selectedImageA && selectedImageB && (
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="mt-4 w-full bg-blue-600 text-white px-4 py-2 rounded-lg font-medium
                hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2
                disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Processing...' : 'Analyze Images'}
            </button>
          )}
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
            {error}
          </div>
        )}

        {/* Results */}
        {previewUrlA && previewUrlB && (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <ImageWithHistograms
                imageUrl={previewUrlA}
                histogramData={histogramData?.imageA}
                title="Image A"
              />
              <ImageWithHistograms
                imageUrl={previewUrlB}
                histogramData={histogramData?.imageB}
                title="Image B"
              />
            </div>

            {mapping && (
              <div className="mt-8">
                <MappingPlot mapping={mapping} />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
} 