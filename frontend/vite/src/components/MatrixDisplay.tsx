import React, { useEffect, useState } from 'react';

interface MatrixDisplayProps {
  dataUrl: string;
}

const MatrixDisplay: React.FC<MatrixDisplayProps> = ({ dataUrl }) => {
  const [matrixData, setMatrixData] = useState<number[][] | null>(null);

  useEffect(() => {
    const fetchMatrixData = async () => {
      try {
        const response = await fetch(dataUrl);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setMatrixData(data);
      } catch (error) {
        console.error('Error fetching matrix data:', error);
      }
    };
    fetchMatrixData();
  }, [dataUrl]);

  if (!matrixData) {
    return <p>Loading matrix data...</p>;
  }

  return (
    <div className="mt-2">
      <p>Stiffness Matrix:</p>
      <table className="table-auto border-collapse border border-gray-400">
        <tbody>
          {matrixData.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((value, colIndex) => (
                <td key={colIndex} className="border border-gray-400 px-2 py-1">
                  {value}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default MatrixDisplay;
