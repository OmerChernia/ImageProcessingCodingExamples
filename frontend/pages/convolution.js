import { useState, useEffect } from 'react';
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

function MaskInput({ kernelSize, mask, onChange, disabled }) {
  const rows = Array(kernelSize).fill(0);
  const cols = Array(kernelSize).fill(0);
  const [displayValues, setDisplayValues] = useState(
    Array(kernelSize).fill().map(() => Array(kernelSize).fill('0'))
  );

  const handleInputChange = (i, j, value) => {
    // Update display value
    const newDisplayValues = displayValues.map(row => [...row]);
    newDisplayValues[i][j] = value;
    setDisplayValues(newDisplayValues);

    // Update actual mask value with the string
    const newMask = mask.map(row => [...row]);
    newMask[i][j] = value === '' ? '0' : value;
    onChange(newMask);
  };

  // Update display values when mask changes externally (e.g., preset masks)
  useEffect(() => {
    setDisplayValues(mask.map(row => 
      row.map(val => val.toString())
    ));
  }, [mask]);

  return (
    <div className="grid gap-2">
      {rows.map((_, i) => (
        <div key={i} className="flex gap-2">
          {cols.map((_, j) => (
            <input
              key={j}
              type="text"
              value={displayValues[i][j]}
              onChange={(e) => handleInputChange(i, j, e.target.value)}
              onBlur={(e) => {
                if (e.target.value === '') {
                  handleInputChange(i, j, '0');
                }
              }}
              disabled={disabled}
              className={`w-16 p-1 text-center border rounded ${
                disabled ? 'bg-gray-50' : ''
              }`}
            />
          ))}
        </div>
      ))}
    </div>
  );
}

export default function ConvolutionPage() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [kernelSize, setKernelSize] = useState(3);
  const [maskType, setMaskType] = useState('identity');
  const [customMask, setCustomMask] = useState(Array(3).fill().map(() => Array(3).fill(0)));
  const [isCustomMask, setIsCustomMask] = useState(false);
  const [processedImageUrl, setProcessedImageUrl] = useState(null);
  const [histogramData, setHistogramData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentMask, setCurrentMask] = useState(Array(3).fill().map(() => Array(3).fill(0)));
  const [add128, setAdd128] = useState(false);

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
      updateMaskValues('identity');
    }
  };

  const handleKernelSizeChange = (size) => {
    const newSize = size % 2 === 0 ? size + 1 : size;
    setKernelSize(newSize);
    setCustomMask(Array(newSize).fill().map(() => Array(newSize).fill(0)));
    setCurrentMask(Array(newSize).fill().map(() => Array(newSize).fill(0)));
  };

  const updateMaskValues = async (type) => {
    if (type === 'custom') {
      setCurrentMask(customMask);
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/get-mask?type=${type}&size=${kernelSize}`);
      if (!response.ok) {
        throw new Error('Failed to fetch mask values');
      }
      const data = await response.json();
      setCurrentMask(data.mask);
    } catch (error) {
      console.error('Error fetching mask:', error);
    }
  };

  const handleMaskTypeChange = (value) => {
    setIsCustomMask(value === 'custom');
    if (value !== 'custom') {
      setMaskType(value);
      updateMaskValues(value);
    } else {
      setCurrentMask(customMask);
    }
  };

  const handleCustomMaskChange = (newMask) => {
    setCustomMask(newMask);
    setCurrentMask(newMask);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedImage) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('image', selectedImage);
    formData.append('kernel_size', kernelSize);
    formData.append('mask_type', isCustomMask ? 'custom' : maskType);
    formData.append('add_128', add128);
    
    if (isCustomMask) {
      try {
        const numericMask = customMask.map(row => 
          row.map(val => {
            if (typeof val === 'string' && val.includes('/')) {
              const [num, den] = val.split('/');
              return parseFloat(num) / parseFloat(den);
            }
            return typeof val === 'string' ? parseFloat(val) : val;
          })
        );
        formData.append('custom_mask', JSON.stringify(numericMask));
      } catch (err) {
        console.error('Error processing mask:', err);
        setError('Error processing mask values');
        setLoading(false);
        return;
      }
    }

    try {
      const response = await fetch('http://localhost:8000/api/convolution', {
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
      console.error('Error details:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!processedImageUrl || !selectedImage) return;

    try {
      const originalName = selectedImage.name.replace(/\.[^/.]+$/, '');
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
      link.download = `${originalName}_convolution.png`;
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
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Convolution Masks</h1>
        
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

            {selectedImage && (
              <>
                {/* Kernel Size */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Kernel Size
                  </label>
                  <select
                    value={kernelSize}
                    onChange={(e) => handleKernelSizeChange(parseInt(e.target.value))}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                  >
                    {[3, 5, 7, 9].map(size => (
                      <option key={size} value={size}>{size}x{size}</option>
                    ))}
                  </select>
                </div>

                {/* Mask Type Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Mask Type
                  </label>
                  <div className="space-y-2">
                    <select
                      value={isCustomMask ? 'custom' : maskType}
                      onChange={(e) => handleMaskTypeChange(e.target.value)}
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    >
                      <option value="identity">Identity Mask</option>
                      <option value="shift">Shift Mask</option>
                      <option value="gaussian">Gaussian Mask</option>
                      <option value="sharpen">Sharpen Mask</option>
                      <option value="custom">Custom Mask</option>
                    </select>

                    {/* Display current mask values */}
                    <div className="mt-4">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        {isCustomMask ? 'Custom Mask Values' : 'Current Mask Values'}
                      </label>
                      <MaskInput
                        kernelSize={kernelSize}
                        mask={currentMask}
                        onChange={handleCustomMaskChange}
                        disabled={!isCustomMask}
                      />
                    </div>
                  </div>
                </div>

                {/* Add 128 Toggle */}
                <div className="mt-4">
                  <label className="flex items-center space-x-3">
                    <input
                      type="checkbox"
                      checked={add128}
                      onChange={(e) => setAdd128(e.target.checked)}
                      className="form-checkbox h-5 w-5 text-blue-600 rounded focus:ring-blue-500"
                    />
                    <span className="text-sm font-medium text-gray-700">
                      Add 128 to result (for edge detection)
                    </span>
                  </label>
                </div>

                {/* Process Button */}
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
                    'Process Image'
                  )}
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

        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
            {error}
          </div>
        )}
      </div>
    </div>
  );
} 