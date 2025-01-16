// Controller.tsx
import { useState, useEffect, useRef } from "react";
import Layout from "./Layout";
import useSpeechRecognition from "../hooks/useSpeechRecognition";
import useAudioRecorder from "../hooks/useAudioRecorder";
import useMessages from "../hooks/useMessages";
import useCalibration from "../hooks/useCalibration";
import useCaptureImage from "../hooks/useCaptureImage";

const Controller = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [isCalibrating, setIsCalibrating] = useState(false);
  const [confirmationDialog, setConfirmationDialog] = useState<{
    message: string;
    onConfirm: () => void;
  } | null>(null);
  const [isHandsfree, setIsHandsfree] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Custom hooks
  const {
    messages,
    setMessages,
    handleReset,
    handleStop,
    handleStartSigma,
    handleStopSigma,
    handleSetZeroSigma,
    handleAutoinitSigma,
    handleInitializeSigma, 
    createBlobURL,
  } = useMessages({ setIsLoading, setConfirmationDialog });

  const { handleCalibration } = useCalibration({
    setIsCalibrating,
    setConfirmationDialog,
  });

  const { handleCaptureImage, imageURL, setImageURL } = useCaptureImage({
    setMessages,
  });

  const { isRecording, startRecording, stopRecording } = useAudioRecorder({
    onStop: handleStop,
    imageURL,
    setImageURL,
    setMessages,
    createBlobURL,
    setIsLoading,
    isHandsfree, // Add this prop
  });
  

  const handleRecordButtonClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const handleHandsfreeToggle = () => {
    if (!isHandsfree) {
      const message = "Are you sure you want to enter handsfree mode?";
      const onConfirm = () => {
        setIsHandsfree(true);
        setConfirmationDialog(null);
      };
      setConfirmationDialog({ message, onConfirm });
    } else {
      setIsHandsfree(false);
    }
  };

  const handleVoiceCommand = (command: string) => {
    switch (command.toLowerCase()) {
      case "start sigma":
        handleStartSigma();
        break;
      case "stop sigma":
        handleStopSigma();
        break;
      case "set zero sigma":
        handleSetZeroSigma();
        break;
      case "calibrate sigma":
        handleAutoinitSigma();
        break;
      case "initialize sigma":
        handleInitializeSigma();
        break;
      case "start recording":
        if (!isRecording) handleRecordButtonClick();
        break;
      case "stop recording":
        if (isRecording) handleRecordButtonClick();
        break;
      case "calibrate":
        handleCalibration();
        break;
      case "capture":
        handleCaptureImage();
        break;
      case "reset":
        handleReset();
        break;
      case "enable handsfree":
        if (!isHandsfree) handleHandsfreeToggle();
        break;
      case "disable":
        if (isHandsfree) handleHandsfreeToggle();
        break;
      default:
        console.log("Unrecognized command:", command);
    }
  };

  useSpeechRecognition({ onResult: handleVoiceCommand, isHandsfree });

  // Scroll to the bottom whenever messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <Layout
      messages={messages}
      isLoading={isLoading}
      isCalibrating={isCalibrating}
      messagesEndRef={messagesEndRef}
      confirmationDialog={confirmationDialog}
      setConfirmationDialog={setConfirmationDialog}
      isRecording={isRecording}
      handleCalibration={handleCalibration}
      handleCaptureImage={handleCaptureImage}
      handleRecordButtonClick={handleRecordButtonClick}
      handleReset={handleReset}
      handleHandsfreeToggle={handleHandsfreeToggle}
      isHandsfree={isHandsfree}
      setMessages={setMessages}
      handleStartSigma={handleStartSigma}
      handleStopSigma={handleStopSigma}
      handleSetZeroSigma={handleSetZeroSigma}
      handleInitializeSigma={handleInitializeSigma}
      handleAutoinitSigma={handleAutoinitSigma}
    />
  );
};

export default Controller;
