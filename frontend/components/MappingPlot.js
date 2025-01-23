import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default function MappingPlot({ mapping }) {
  if (!mapping) return null;

  const data = {
    labels: Array.from({ length: 256 }, (_, i) => i),
    datasets: [{
      label: 'Intensity Mapping',
      data: mapping.map((y, x) => ({ x, y })),
      borderColor: 'rgb(75, 192, 192)',
      backgroundColor: 'rgba(75, 192, 192, 0.5)',
      pointRadius: 1,
      showLine: true,
      fill: false
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        title: {
          display: true,
          text: 'Intensity in Image A'
        }
      },
      y: {
        title: {
          display: true,
          text: 'Intensity in Image B'
        }
      }
    },
    plugins: {
      title: {
        display: true,
        text: 'Monotonic Intensity Mapping'
      },
      legend: {
        display: false
      }
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Intensity Mapping</h2>
      <div className="h-96">
        <Line data={data} options={options} />
      </div>
    </div>
  );
} 