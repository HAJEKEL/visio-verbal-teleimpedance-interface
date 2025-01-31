import React from "react";
import Title from "./Title";
import MessageList from "./MessageList";
import BottomBar from "./BottomBar";
import ConfirmationDialog from "./ConfirmationDialog";

type LayoutProps = {
  messages: any[];
  isLoading: boolean;
  isCalibrating: boolean;
  messagesEndRef: React.RefObject<HTMLDivElement>;
  confirmationDialog: {
    message: string;
    onConfirm: () => void;
  } | null;
  setConfirmationDialog: React.Dispatch<
    React.SetStateAction<{
      message: string;
      onConfirm: () => void;
    } | null>
  >;
  isRecording: boolean;
  handleCalibration: () => void;
  handleCaptureImage: () => void;
  handleRecordButtonClick: () => void;
  handleReset: () => void;
  handleHandsfreeToggle: () => void;
  isHandsfree: boolean;
  setMessages: React.Dispatch<React.SetStateAction<any[]>>;
  handleStartSigma: () => void; // New handler for Sigma7 start
  handleStopSigma: () => void;  // New handler for Sigma7 stop
  handleSetZeroSigma: () => void;  // New handler for Sigma7 set zero
  handleAutoinitSigma: () => void;  // New handler for Sigma7 autoinit
  handleInitializeSigma: () => void;  // New handler for Sigma7 initialize
};

const Layout: React.FC<LayoutProps> = ({
  messages,
  isLoading,
  isCalibrating,
  messagesEndRef,
  confirmationDialog,
  setConfirmationDialog,
  isRecording,
  handleCalibration,
  handleCaptureImage,
  handleRecordButtonClick,
  handleReset,
  handleHandsfreeToggle,
  isHandsfree,
  setMessages,
  handleStartSigma,
  handleStopSigma,
  handleSetZeroSigma,
  handleAutoinitSigma,
  handleInitializeSigma
}) => {
  return (
    <div className="h-screen w-screen overflow-hidden flex flex-col">
      <Title setMessages={setMessages} />

      {/* Messages container */}
      <div className="flex-1 overflow-y-auto">
        <div className="mt-5 px-5">
          <MessageList
            messages={messages}
            isLoading={isLoading}
            isCalibrating={isCalibrating}
            messagesEndRef={messagesEndRef}
          />
        </div>
      </div>

      {/* Bottom bar */}
      <BottomBar
        isRecording={isRecording}
        handleCalibration={handleCalibration}
        handleCaptureImage={handleCaptureImage}
        handleRecordButtonClick={handleRecordButtonClick}
        handleReset={handleReset}
        handleHandsfreeToggle={handleHandsfreeToggle}
        isHandsfree={isHandsfree}
        handleStartSigma={handleStartSigma} // Pass handler for start
        handleStopSigma={handleStopSigma}   // Pass handler for stop
        handleSetZeroSigma={handleSetZeroSigma} // Pass handler for set zero
        handleAutoinitSigma={handleAutoinitSigma} // Pass handler for autoinit
        handleInitializeSigma={handleInitializeSigma} // Pass handler for
      />

      {/* Confirmation Dialog */}
      {confirmationDialog && (
        <ConfirmationDialog
          message={confirmationDialog.message}
          onConfirm={confirmationDialog.onConfirm}
          onCancel={() => setConfirmationDialog(null)}
        />
      )}
    </div>
  );
};

export default Layout;

