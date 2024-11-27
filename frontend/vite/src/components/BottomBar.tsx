// BottomBar.tsx
import React from "react";

type BottomBarProps = {
  isRecording: boolean;
  handleCalibration: () => void;
  handleCaptureImage: () => void;
  handleRecordButtonClick: () => void;
  handleReset: () => void;
  handleHandsfreeToggle: () => void;
  isHandsfree: boolean;
};

const BottomBar: React.FC<BottomBarProps> = ({
  isRecording,
  handleCalibration,
  handleCaptureImage,
  handleRecordButtonClick,
  handleReset,
  handleHandsfreeToggle,
  isHandsfree,
}) => {
  return (
    <div className="py-6 border-t text-center bg-gradient-to-r from-sky-500 to-green-500">
      <div className="flex justify-center items-center w-full">
        <div>
          <button
            onClick={handleCalibration}
            className="px-4 py-2 bg-yellow-500 text-white rounded-md mr-4"
          >
            Calibrate
          </button>

          <button
            onClick={handleCaptureImage}
            className="px-4 py-2 bg-green-500 text-white rounded-md"
          >
            Capture
          </button>

          <button
            onClick={handleRecordButtonClick}
            className="px-4 py-2 bg-blue-500 text-white rounded-md ml-4"
          >
            {isRecording ? "Stop Recording" : "Start Recording"}
          </button>

          <button
            onClick={handleReset}
            className="px-4 py-2 bg-red-500 text-white rounded-md ml-4"
          >
            Reset
          </button>

          <button
            onClick={handleHandsfreeToggle}
            className="px-4 py-2 bg-purple-500 text-white rounded-md ml-4"
          >
            {isHandsfree ? "Disable Handsfree" : "Enable Handsfree"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default BottomBar;
