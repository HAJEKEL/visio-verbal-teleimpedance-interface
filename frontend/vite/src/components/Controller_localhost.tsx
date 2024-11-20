import { useState, useEffect, useRef } from "react";
import Title from "./Title";
import axios from "axios";
import MatrixDisplay from "./MatrixDisplay";

const Controller = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isCalibrating, setIsCalibrating] = useState(false); // For calibration
  const [messages, setMessages] = useState<any[]>([]);
  const [imageURL, setImageURL] = useState<string | null>(null);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);

  // Ref to track the end of the messages for auto-scrolling
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Speech Recognition
  const [recognition, setRecognition] = useState<any>(null);
  const [confirmationDialog, setConfirmationDialog] = useState<{
    message: string;
    onConfirm: () => void;
  } | null>(null);

  // Silence detection
  const [audioContext, setAudioContext] = useState<AudioContext | null>(null);
  const [analyser, setAnalyser] = useState<AnalyserNode | null>(null);
  const silenceTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Handsfree mode state
  const [isHandsfree, setIsHandsfree] = useState(false);

  // Scroll to the bottom whenever messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Set up speech recognition (runs once on mount)
  useEffect(() => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognitionInstance = new SpeechRecognition();
      recognitionInstance.continuous = true;
      recognitionInstance.lang = "en-US";
      recognitionInstance.interimResults = false;
      recognitionInstance.maxAlternatives = 1;

      recognitionInstance.onresult = (event: any) => {
        const last = event.results.length - 1;
        const transcript = event.results[last][0].transcript.trim().toLowerCase();
        console.log("Recognized speech:", transcript);

        handleVoiceCommand(transcript);
      };

      recognitionInstance.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error);
        // Restart the recognition instance
        recognitionInstance.stop();
        recognitionInstance.start();
      };

      setRecognition(recognitionInstance);
    } else {
      console.warn("Speech recognition not supported in this browser.");
    }
  }, []); // Empty dependency array to run once on mount

  // Start or stop speech recognition based on handsfree mode
  useEffect(() => {
    if (recognition) {
      if (isHandsfree) {
        recognition.start();
      } else {
        recognition.stop();
      }
    }
  }, [isHandsfree, recognition]);

  const handleVoiceCommand = (command: string) => {
    if (command === "start") {
      if (!isRecording) {
        recognition.stop(); // Stop wakeword detection
        handleRecordButtonClick(); // Start recording
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

  function createBlobURL(data: any) {
    const blob = new Blob([data], { type: "audio/mpeg" });
    return window.URL.createObjectURL(blob);
  }

  const audioConstraints = {
    audio: {
      channelCount: 1,
      sampleRate: 16000,
    },
  };

  const handleCalibration = async () => {
    const message =
      "Place the calibration sticker on the display screen and make sure you look at the center before you say OK.";
    const onConfirm = async () => {
      setIsCalibrating(true);
      let attempts = 3; // Retry limit
      while (attempts > 0) {
        try {
          const response = await axios.get(
            "http://127.0.0.1:8011/calibrate"
          );
          window.alert(response.data.status || "Calibration successful!");
          break; // Exit loop if successful
        } catch (error: any) {
          console.error("Calibration failed:", error);
          attempts -= 1;
          if (attempts === 0) {
            const errorMessage =
              error.response?.data?.detail || "Calibration failed! Please try again.";
            window.alert(errorMessage);
          }
        }
      }
      setIsCalibrating(false);
    };

    setConfirmationDialog({ message, onConfirm });
  };

  const handleCaptureImage = async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8011/capture_snapshot",
        {
          responseType: "blob",
        }
      );
      const blob = response.data;

      const file = new File([blob], "snapshot.jpg", { type: "image/jpeg" });
      const formData = new FormData();
      formData.append("file", file);

      const uploadResponse = await axios.post(
        "http://127.0.0.1:8000/upload_image",
        formData,
        {
          timeout: 10000,
        }
      );
      const uploadedImageURL = uploadResponse.data;
      setImageURL(uploadedImageURL);

      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "me", type: "image", imageUrl: uploadedImageURL },
      ]);

      alert("Snapshot captured and uploaded successfully!");
    } catch (err) {
      console.error("Error capturing or uploading snapshot:", err);
      alert("Failed to capture or upload snapshot. Please try again.");
    }
  };

  const startRecording = () => {
    navigator.mediaDevices.getUserMedia(audioConstraints).then((stream) => {
      const recorder = new MediaRecorder(stream);
      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);

      // Set up audio context and analyser for silence detection
      const audioCtx = new AudioContext();
      const source = audioCtx.createMediaStreamSource(stream);
      const analyserNode = audioCtx.createAnalyser();
      analyserNode.fftSize = 2048;
      source.connect(analyserNode);
      setAudioContext(audioCtx);
      setAnalyser(analyserNode);

      detectSilence(analyserNode, () => {
        // Silence detected for 3 seconds, stop recording
        stopRecording();
      });

      recorder.ondataavailable = (e: any) => {
        const audioBlob = e.data;
        const audioUrl = createBlobURL(audioBlob);
        handleStop(audioUrl);
      };
    });
  };

  const stopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setIsRecording(false);
      if (audioContext) {
        audioContext.close();
        setAudioContext(null);
        setAnalyser(null);
      }
      if (silenceTimeoutRef.current) {
        clearTimeout(silenceTimeoutRef.current);
        silenceTimeoutRef.current = null;
      }
    }
  };

  const handleRecordButtonClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const handleStop = async (blobUrl: string) => {
    setIsLoading(true);

    const myMessage = { sender: "me", type: "audio", blobUrl };
    // Display user's message immediately
    setMessages((prevMessages) => [...prevMessages, myMessage]);

    fetch(blobUrl)
      .then((res) => res.blob())
      .then(async (blob) => {
        const formData = new FormData();
        formData.append("file", blob, "myFile.wav");

        if (imageURL) {
          formData.append("image_url", imageURL);
          setImageURL(null); // Clear imageURL after use
        }

        await axios
          .post("http://127.0.0.1:8000/post_audio", formData, {
            responseType: "blob",
          })
          .then((res: any) => {
            const blob = res.data;
            const audio = new Audio();
            audio.src = createBlobURL(blob);

            const newMessages = [];

            const matriceMessage = {
              sender: "matrice",
              type: "audio",
              blobUrl: audio.src,
            };
            newMessages.push(matriceMessage);

            const matrixUrl = res.headers["x-matrix-url"];
            const ellipsoidUrl = res.headers["x-ellipsoid-url"];

            if (matrixUrl) {
              const matrixMessage = {
                sender: "matrice",
                type: "matrix",
                dataUrl: matrixUrl,
              };
              newMessages.push(matrixMessage);
            }

            if (ellipsoidUrl) {
              const ellipsoidMessage = {
                sender: "matrice",
                type: "image",
                imageUrl: ellipsoidUrl,
              };
              newMessages.push(ellipsoidMessage);
            }

            // Append response messages
            setMessages((prevMessages) => [...prevMessages, ...newMessages]);
            setIsLoading(false);
            audio.play();
          })
          .catch((err: any) => {
            console.error(err);
            setIsLoading(false);
          });
      });
  };

  const handleReset = async () => {
    const message = "Are you sure you want to reset the conversation history?";
    const onConfirm = async () => {
      try {
        await axios.get("http://127.0.0.1:8000/reset");

        // Clear the messages in the frontend
        setMessages([]);

        window.alert("Conversation history has been reset.");
      } catch (error: any) {
        console.error("Failed to reset conversation history:", error);
        window.alert("Failed to reset conversation history. Please try again.");
      }
    };

    setConfirmationDialog({ message, onConfirm });
  };

  // Silence detection function
  const detectSilence = (
    analyserNode: AnalyserNode,
    onSilence: () => void,
    silenceDelay = 3000,
    threshold = -50
  ) => {
    const dataArray = new Uint8Array(analyserNode.fftSize);
    let silenceStart: number | null = null;

    const checkSilence = () => {
      analyserNode.getByteFrequencyData(dataArray);
      let values = 0;
      for (let i = 0; i < dataArray.length; i++) {
        values += dataArray[i];
      }
      const average = values / dataArray.length;
      const avgDecibels = 20 * Math.log10(average / 255);

      if (avgDecibels < threshold) {
        if (!silenceStart) {
          silenceStart = performance.now();
        } else {
          const elapsed = performance.now() - silenceStart;
          if (elapsed > silenceDelay) {
            onSilence();
            return; // Stop checking
          }
        }
      } else {
        silenceStart = null;
      }

      if (isRecording) {
        requestAnimationFrame(checkSilence);
      }
    };

    checkSilence();
  };

  // Handle Handsfree mode toggle
  const handleHandsfreeToggle = () => {
    if (!isHandsfree) {
      // Show confirmation dialog when enabling handsfree mode
      const message = "Are you sure you want to enter handsfree mode?";
      const onConfirm = () => {
        setIsHandsfree(true);
        setConfirmationDialog(null);
      };
      setConfirmationDialog({ message, onConfirm });
    } else {
      // Disable handsfree mode directly
      setIsHandsfree(false);
    }
  };

  return (
    <div className="h-screen w-screen overflow-hidden flex flex-col">
      <Title setMessages={setMessages} />

      {/* Messages container now fills available space */}
      <div className="flex-1 overflow-y-auto">
        <div className="mt-5 px-5">
          {messages?.map((message, index) => (
            <div
              key={index + message.sender}
              className={
                "flex flex-col " +
                (message.sender === "matrice" ? "items-end" : "items-start")
              }
            >
              <div className="mt-4 ">
                <p
                  className={
                    message.sender === "matrice"
                      ? "text-right mr-2 italic text-green-500"
                      : "ml-2 italic text-blue-500"
                  }
                >
                  {message.sender}
                </p>

                {message.type === "audio" ? (
                  <audio
                    src={message.blobUrl}
                    className="appearance-none"
                    controls
                  />
                ) : message.type === "image" ? (
                  <img
                    src={message.imageUrl}
                    alt="Image"
                    className="w-full max-w-2xl h-auto mt-2"
                  />
                ) : message.type === "matrix" ? (
                  <MatrixDisplay dataUrl={message.dataUrl} />
                ) : null}
              </div>
            </div>
          ))}

          {messages.length === 0 && !isLoading && (
            <div className="text-center font-light italic mt-10">
              Send matrice a message...
            </div>
          )}

          {isLoading && (
            <div className="text-center font-light italic mt-10 animate-pulse">
              Give me a moment, I'm thinking...
            </div>
          )}

          {isCalibrating && (
            <div className="text-center font-light italic mt-10 animate-pulse">
              Calibrating... Please wait.
            </div>
          )}

          {/* Div to scroll into view */}
          <div ref={messagesEndRef}></div>
        </div>
      </div>

      {/* Bottom bar stays at the bottom */}
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

            {/* Add the Reset button */}
            <button
              onClick={handleReset}
              className="px-4 py-2 bg-red-500 text-white rounded-md ml-4"
            >
              Reset
            </button>

            {/* Add the Handsfree button */}
            <button
              onClick={handleHandsfreeToggle}
              className="px-4 py-2 bg-purple-500 text-white rounded-md ml-4"
            >
              {isHandsfree ? "Disable Handsfree" : "Enable Handsfree"}
            </button>
          </div>
        </div>
      </div>

      {/* Confirmation Dialog */}
      {confirmationDialog && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-white p-6 rounded-md">
            <p>{confirmationDialog.message}</p>
            <div className="mt-4 flex justify-end">
              <button
                onClick={() => {
                  confirmationDialog.onConfirm();
                  setConfirmationDialog(null); // Ensure the dialog closes
                }}
                className="px-4 py-2 bg-blue-500 text-white rounded-md mr-2"
              >
                Continue
              </button>
              <button
                onClick={() => setConfirmationDialog(null)}
                className="px-4 py-2 bg-gray-500 text-white rounded-md"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Controller;
