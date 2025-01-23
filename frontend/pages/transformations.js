import { useState } from 'react';

function ImageWithMatrix({ imageUrl, matrixData, title }) {
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
        
        {matrixData && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Current Transformation Matrix:</h3>
            <div className="grid grid-cols-3 gap-2 font-mono text-sm">
              {matrixData.map((row, i) => (
                row.map((val, j) => (
                  <div key={`${i}-${j}`} className="bg-white p-2 rounded text-center">
                    {val.toFixed(3)}
                  </div>
                ))
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function MatrixFormat({ type }) {
  const formats = {
    rotation: (
      <pre className="text-sm font-mono whitespace-pre">
{`Rotation Matrix (θ = angle in degrees):
┌                      ┐
│  cos(θ)  -sin(θ)  0  │
│  sin(θ)   cos(θ)  0  │
│    0       0      1  │
└                      ┘`}
      </pre>
    ),
    translation: (
      <pre className="text-sm font-mono whitespace-pre">
{`Translation Matrix (tx, ty):
┌              ┐
│  1   0   tx  │
│  0   1   ty  │
│  0   0   1   │
└              ┘`}
      </pre>
    ),
    scaling: (
      <pre className="text-sm font-mono whitespace-pre">
{`Scaling Matrix (sx, sy):
┌              ┐
│  sx  0   0   │
│  0   sy  0   │
│  0   0   1   │
└              ┘`}
      </pre>
    ),
    shearing: (
      <pre className="text-sm font-mono whitespace-pre">
{`Shear Matrix (shx, shy):
┌                 ┐
│  1    shx   0   │
│  shy   1    0   │
│  0     0    1   │
└                 ┘`}
      </pre>
    )
  };

  return (
    <div className="bg-gray-50 p-4 rounded-lg mt-4">
      <h3 className="font-medium mb-2">Matrix Format:</h3>
      <div className="bg-white p-4 rounded-lg overflow-x-auto">
        {formats[type]}
      </div>
    </div>
  );
}

export default function TransformationsPage() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [processedImageUrl, setProcessedImageUrl] = useState(null);
  const [transformationType, setTransformationType] = useState('rotation');
  const [matrixData, setMatrixData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Parameters for different transformations
  const [rotationAngle, setRotationAngle] = useState(0);
  const [scaleX, setScaleX] = useState(1);
  const [scaleY, setScaleY] = useState(1);
  const [shearX, setShearX] = useState(0);
  const [shearY, setShearY] = useState(0);
  const [tx, setTx] = useState(0);
  const [ty, setTy] = useState(0);

  const handleImageSelect = async (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
      setProcessedImageUrl(null);
      setMatrixData(null);
    }
  };

  const handleSubmit = async () => {
    if (!selectedImage) return;

    setError(null);
    setLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('image', selectedImage);
      formData.append('type', transformationType);

      // Add parameters based on transformation type
      switch (transformationType) {
        case 'rotation':
          formData.append('angle', rotationAngle);
          break;
        case 'translation':
          formData.append('tx', tx);
          formData.append('ty', ty);
          break;
        case 'scaling':
          formData.append('scale_x', scaleX);
          formData.append('scale_y', scaleY);
          break;
        case 'shearing':
          formData.append('shear_x', shearX);
          formData.append('shear_y', shearY);
          break;
      }

      const response = await fetch('http://localhost:8000/api/transform', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to process image');
      }

      const data = await response.json();
      setProcessedImageUrl(data.processedImage);
      setMatrixData(data.transformationMatrix);
    } catch (err) {
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
      link.download = `${originalName}_${transformationType}.png`;
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
    <div className="min-h-screen bg-gradient-to-b from-gray-100 to-gray-200 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Image Transformations</h1>
          
          {/* Image Upload */}
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
                  file:rounded-full file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100"
              />
            </div>

            {selectedImage && (
              <div className="space-y-6">
                {/* Transformation Type Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Transformation Type
                  </label>
                  <select
                    value={transformationType}
                    onChange={(e) => setTransformationType(e.target.value)}
                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 
                      focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm 
                      rounded-md"
                  >
                    <option value="rotation">Rotation</option>
                    <option value="translation">Translation</option>
                    <option value="scaling">Scaling</option>
                    <option value="shearing">Shearing</option>
                  </select>

                  {/* Show Matrix Format */}
                  <MatrixFormat type={transformationType} />
                </div>

                {/* Transformation Parameters */}
                <div className="space-y-4">
                  {transformationType === 'rotation' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Rotation Angle (degrees)
                      </label>
                      <div className="flex items-center gap-4">
                        <input
                          type="range"
                          min="-180"
                          max="180"
                          value={rotationAngle}
                          onChange={(e) => setRotationAngle(parseFloat(e.target.value))}
                          className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                        />
                        <span className="text-sm text-gray-600 w-12 text-right">
                          {rotationAngle}°
                        </span>
                      </div>
                    </div>
                  )}

                  {transformationType === 'translation' && (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Translation X
                        </label>
                        <div className="flex items-center gap-4">
                          <input
                            type="range"
                            min="-100"
                            max="100"
                            value={tx}
                            onChange={(e) => setTx(parseFloat(e.target.value))}
                            className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                          />
                          <span className="text-sm text-gray-600 w-12 text-right">
                            {tx}
                          </span>
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Translation Y
                        </label>
                        <div className="flex items-center gap-4">
                          <input
                            type="range"
                            min="-100"
                            max="100"
                            value={ty}
                            onChange={(e) => setTy(parseFloat(e.target.value))}
                            className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                          />
                          <span className="text-sm text-gray-600 w-12 text-right">
                            {ty}
                          </span>
                        </div>
                      </div>
                    </>
                  )}

                  {transformationType === 'scaling' && (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Scale X
                        </label>
                        <div className="flex items-center gap-4">
                          <input
                            type="range"
                            min="0.1"
                            max="3"
                            step="0.1"
                            value={scaleX}
                            onChange={(e) => setScaleX(parseFloat(e.target.value))}
                            className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                          />
                          <span className="text-sm text-gray-600 w-12 text-right">
                            {scaleX.toFixed(1)}
                          </span>
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Scale Y
                        </label>
                        <div className="flex items-center gap-4">
                          <input
                            type="range"
                            min="0.1"
                            max="3"
                            step="0.1"
                            value={scaleY}
                            onChange={(e) => setScaleY(parseFloat(e.target.value))}
                            className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                          />
                          <span className="text-sm text-gray-600 w-12 text-right">
                            {scaleY.toFixed(1)}
                          </span>
                        </div>
                      </div>
                    </>
                  )}

                  {transformationType === 'shearing' && (
                    <>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Shear X
                        </label>
                        <div className="flex items-center gap-4">
                          <input
                            type="range"
                            min="-2"
                            max="2"
                            step="0.1"
                            value={shearX}
                            onChange={(e) => setShearX(parseFloat(e.target.value))}
                            className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                          />
                          <span className="text-sm text-gray-600 w-12 text-right">
                            {shearX.toFixed(1)}
                          </span>
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Shear Y
                        </label>
                        <div className="flex items-center gap-4">
                          <input
                            type="range"
                            min="-2"
                            max="2"
                            step="0.1"
                            value={shearY}
                            onChange={(e) => setShearY(parseFloat(e.target.value))}
                            className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                          />
                          <span className="text-sm text-gray-600 w-12 text-right">
                            {shearY.toFixed(1)}
                          </span>
                        </div>
                      </div>
                    </>
                  )}

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
                      'Apply Transformation'
                    )}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Results - Side by Side */}
        {previewUrl && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <ImageWithMatrix
              imageUrl={previewUrl}
              title="Original Image"
            />

            {processedImageUrl ? (
              <ImageWithMatrix
                imageUrl={processedImageUrl}
                matrixData={matrixData}
                title="Transformed Image"
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