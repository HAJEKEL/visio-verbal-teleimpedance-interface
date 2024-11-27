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
    createBlobURL,
  } = useMessages({ setIsLoading, setConfirmationDialog });

  const { handleCalibration } = useCalibration({
    setIsCalibrating,
    setConfirmationDialog,
  });

  const { handleCaptureImage, imageURL, setImageURL } = useCaptureImage({
    setMessages,
  });

  const handleVoiceCommand = (command: string) => {
    if (command === "start") {
      if (!isRecording) {
        handleRecordButtonClick();
      }
    } else if (command === "stop") {
      if (isRecording) {
        handleRecordButtonClick();
      }
    } else if (command === "calibrate") {
      handleCalibration();
    } else if (command === "capture") {
      handleCaptureImage();
    } else if (command === "reset") {
      handleReset();
    } else if (command === "continue") {
      if (confirmationDialog) {
        confirmationDialog.onConfirm();
        setConfirmationDialog(null);
      }
    } else {
      console.log("Unrecognized command:", command);
    }
  };

  useSpeechRecognition({ onResult: handleVoiceCommand, isHandsfree });
  
  const { isRecording, startRecording, stopRecording } = useAudioRecorder({
    onStop: handleStop,
    imageURL,
    setImageURL,
    setMessages,
    createBlobURL,
    setIsLoading,
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
    />
  );
};

export default Controller;
