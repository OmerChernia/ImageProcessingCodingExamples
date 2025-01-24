# Image Processing Web Application

A web-based application for performing various image processing operations using React, Next.js, and Python backend.

## Features

- Brightness Adjustment
- Two-Pointer Algorithm Analysis
- Contrast Stretching
- Gamma Correction
- Histogram Equalization
- Image Transformations (Rotation, Scaling, Shearing, Translation)
- Real-time Histogram Visualization
- Interactive Controls
- Image Download Support

## Project Structure

📦 image-processing-web-app
├── 📂 frontend
│ ├── 📂 components
│ │ ├── HistogramChart.jsx # Histogram visualization
│ │ ├── ImageUploader.jsx # Image upload handling
│ │ ├── ImageViewer.jsx # Image display
│ │ ├── MappingPlot.js # Intensity mapping
│ │ └── Sliders.jsx # Interactive controls
│ ├── 📂 pages
│ │ ├── app.js # Next.js config
│ │ ├── index.js # Home page
│ │ ├── 2pointer.js # Two-pointer algorithm
│ │ ├── brightness.js # Brightness adjustment
│ │ ├── contrast.js # Contrast stretching
│ │ ├── gamma.js # Gamma correction
│ │ ├── histogram.js # Histogram equalization
│ │ ├── scripts.js # Backend scripts
│ │ └── transformations.js # Image transformations
│ └── 📂 styles
│ └── globals.css # Global styles
└── 📂 backend
├── 📂 routers
├── 📂 scripts
└── main.py

## Prerequisites

- Node.js (v14 or higher)
- Python 3.8+
- npm or yarn

## Installation

1. Clone the repository:
   bash
   git clone <repository-url>
   cd image-processing-web-app

2. Install frontend dependencies:
   bash
   cd frontend
   npm install

3. Install backend dependencies:
   bash
   cd backend
   pip install -r requirements.txt

## Running the Application

1. Start the frontend development server:
   bash
   cd frontend
   npm run dev

2. Start the backend server:
   bash
   cd backend
   python main.py

The application will be available at `http://localhost:3000`

## Technologies Used

### Frontend

- React.js
- Next.js
- Tailwind CSS
- Chart.js
- React Chart.js 2

### Backend

- Python
- FastAPI (assumed based on API endpoints)
- NumPy (for image processing)
- OpenCV (for image transformations)

## API Endpoints

- `/api/compute-histogram` - Compute image histograms
- `/api/brightness` - Adjust image brightness
- `/api/contrast` - Apply contrast stretching
- `/api/gamma` - Apply gamma correction
- `/api/histogram` - Perform histogram equalization
- `/api/transformations` - Apply geometric transformations

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- React.js documentation
- Next.js documentation
- Tailwind CSS documentation
- Chart.js documentation
- Python image processing libraries
