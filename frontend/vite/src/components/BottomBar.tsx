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
  handleStartSigma: () => void;
  handleStopSigma: () => void;
  handleSetZeroSigma: () => void;
  handleAutoinitSigma: () => void;
  handleInitializeSigma: () => void;
};

const BottomBar: React.FC<BottomBarProps> = ({
  isRecording,
  handleCalibration,
  handleCaptureImage,
  handleRecordButtonClick,
  handleReset,
  handleHandsfreeToggle,
  isHandsfree,
  handleStartSigma,
  handleStopSigma,
  handleSetZeroSigma,
  handleAutoinitSigma,
  handleInitializeSigma
}) => {
  return (
    <div className="py-6 border-t text-center bg-gradient-to-r from-sky-500 to-green-500">
      {/* Existing controls */}
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

      {/* Sigma7 controls */}
      <div className="flex justify-center items-center w-full mt-4">
        <div>
          <button
            onClick={handleStartSigma}
            className="px-4 py-2 bg-green-700 text-white rounded-md mr-4"
          >
            Start Sigma7
          </button>

          <button
            onClick={handleStopSigma}
            className="px-4 py-2 bg-red-700 text-white rounded-md"
          >
            Stop Sigma7
          </button>

          <button
            onClick={handleSetZeroSigma}
            className="px-4 py-2 bg-yellow-700 text-white rounded-md ml-4"
          >
            Set Zero Position
          </button>

          <button
            onClick={handleAutoinitSigma}
            className="px-4 py-2 bg-blue-700 text-white rounded-md ml-4"
          >
            Run Autoinit
          </button>

          <button 
            onClick={handleInitializeSigma}
            className="px-4 py-2 bg-purple-700 text-white rounded-md ml-4"
            >
            Initialize Sigma7
          </button>
        </div>
      </div>
    </div>
  );
};

export default BottomBar;
