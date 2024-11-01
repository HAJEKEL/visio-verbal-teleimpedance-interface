import { useState } from "react";
import Title from "./Title";
import axios from "axios";
import RecordMessage from "./RecordMessage";

const Controller = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  const [imageURL, setImageURL] = useState<string | null>(null);
  const [mediaRecorder, setMediaRecorder] = useState<any>(null);

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

  const handleCaptureImage = async () => {
    try {
      // Capture the snapshot as a blob from the eye tracker
      const response = await axios.get("https://eye-tracker-sunbird-dashing.ngrok-free.app/capture_snapshot", {
        responseType: "blob",
      });
      const blob = response.data;

      // Convert the blob into a File to send to the backend
      const file = new File([blob], "snapshot.jpg", { type: "image/jpeg" });
      const formData = new FormData();
      formData.append("file", file);

      // Send the image file to the backend's upload endpoint
      const uploadResponse = await axios.post("https://summary-sunbird-dashing.ngrok-free.app/upload_image", formData, {
        timeout: 10000,
      });
      const uploadedImageURL = uploadResponse.data;
      setImageURL(uploadedImageURL); // Store the backend URL for future use

      // Add the image message to the chat history
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
    const messagesArr = [...messages, myMessage];

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
          .post("https://summary-sunbird-dashing.ngrok-free.app/post_audio", formData, {
            responseType: "arraybuffer",
          })
          .then((res: any) => {
            const blob = res.data;
            const audio = new Audio();
            audio.src = createBlobURL(blob);

            const rachelMessage = { sender: "rachel", type: "audio", blobUrl: audio.src };
            messagesArr.push(rachelMessage);
            setMessages(messagesArr);

            setIsLoading(false);
            audio.play();
          })
          .catch((err: any) => {
            console.error(err);
            setIsLoading(false);
          });
      });
  };

  return (
    <div className="h-screen overflow-y-hidden">
      <Title setMessages={setMessages} />

      <div className="flex flex-col justify-between h-full overflow-y-scroll pb-96">
        <div className="mt-5 px-5">
          {messages?.map((message, index) => {
            return (
              <div
                key={index + message.sender}
                className={
                  "flex flex-col " +
                  (message.sender === "rachel" && "flex items-end")
                }
              >
                <div className="mt-4 ">
                  <p
                    className={
                      message.sender === "rachel"
                        ? "text-right mr-2 italic text-green-500"
                        : "ml-2 italic text-blue-500"
                    }
                  >
                    {message.sender}
                  </p>
                  
                  {/* Display audio or image based on message type */}
                  {message.type === "audio" ? (
                    <audio src={message.blobUrl} className="appearance-none" controls />
                  ) : message.type === "image" ? (
                    <img src={message.imageUrl} alt="Captured Snapshot" className="w-48 h-auto mt-2" />
                  ) : null}
                </div>
              </div>
            );
          })}

          {messages.length === 0 && !isLoading && (
            <div className="text-center font-light italic mt-10">
              Send Rachel a message...
            </div>
          )}

          {isLoading && (
            <div className="text-center font-light italic mt-10 animate-pulse">
              Gimme a few seconds...
            </div>
          )}
        </div>

        <div className="fixed bottom-0 w-full py-6 border-t text-center bg-gradient-to-r from-sky-500 to-green-500">
          <div className="flex justify-center items-center w-full">
            <div>
              {/* Capture Button (replaces file upload button) */}
              <button
                onClick={handleCaptureImage}
                className="px-4 py-2 bg-green-500 text-white rounded-md"
              >
                Capture
              </button>

              {/* Record/Stop Button */}
              <button
                onClick={handleRecordButtonClick}
                className="px-4 py-2 bg-blue-500 text-white rounded-md ml-4"
              >
                {isRecording ? "Stop Recording" : "Start Recording"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Controller;