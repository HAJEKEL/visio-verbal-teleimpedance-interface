import { useState } from "react";
import Title from "./Title";
import axios from "axios";

const Controller = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);
  const [imageURL, setImageURL] = useState<string | null>(null);
  const [ellipsoidImageUrl, setEllipsoidImageUrl] = useState<string | null>(null);
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
      const response = await axios.get("https://eye-tracker-sunbird-dashing.ngrok-free.app/capture_snapshot", {
        responseType: "blob",
      });
      const blob = response.data;

      const file = new File([blob], "snapshot.jpg", { type: "image/jpeg" });
      const formData = new FormData();
      formData.append("file", file);

      const uploadResponse = await axios.post("https://summary-sunbird-dashing.ngrok-free.app/upload_image", formData, {
        timeout: 10000,
      });
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
    setMessages(messagesArr);
  
    try {
      const blob = await fetch(blobUrl).then((res) => res.blob());
  
      const formData = new FormData();
      formData.append("file", blob, "myFile.wav");
  
      if (imageURL) {
        formData.append("image_url", imageURL);
        setImageURL(null); // Clear imageURL after use
      }
  
      // Single axios call to post_audio endpoint
      const audioResponse = await axios.post("https://summary-sunbird-dashing.ngrok-free.app/post_audio", formData, {
        responseType: "json",
      });
  
      // Process the audio if available
      if (audioResponse.data.audio) {
        const audioBlob = new Blob([audioResponse.data.audio], { type: "audio/mpeg" });
        const audioUrl = createBlobURL(audioBlob);
  
        const rachelMessage = { sender: "rachel", type: "audio", blobUrl: audioUrl };
        messagesArr.push(rachelMessage);
        setMessages(messagesArr);
  
        const audio = new Audio(audioUrl);
        audio.play();
      }
  
      // If a stiffness matrix is included, make a second request to generate the ellipsoid
      if (audioResponse.data.stiffness_matrix) {
        const ellipsoidResponse = await axios.post(
          "https://summary-sunbird-dashing.ngrok-free.app/generate_ellipsoid",
          { stiffness_matrix: audioResponse.data.stiffness_matrix }
        );
  
        if (ellipsoidResponse.data.ellipsoid_url) {
          setEllipsoidImageUrl(ellipsoidResponse.data.ellipsoid_url);
        }
      }
  
      setIsLoading(false);
    } catch (err) {
      console.error("Error processing audio or retrieving response:", err);
      setIsLoading(false);
    }
  };
  

  return (
    <div className="flex h-screen overflow-y-hidden">
      <div className="flex-grow">
        <Title setMessages={setMessages} />

        <div className="flex flex-col justify-between h-full overflow-y-scroll pb-96">
          <div className="mt-5 px-5">
            {messages?.map((message, index) => (
              <div
                key={index + message.sender}
                className={"flex flex-col " + (message.sender === "rachel" && "items-end")}
              >
                <div className="mt-4">
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
            ))}

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
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Ellipsoid display section on the right */}
      <div className="w-1/3 p-4 border-l border-gray-300">
        {ellipsoidImageUrl ? (
          <img src={ellipsoidImageUrl} alt="Stiffness Ellipsoid" className="w-full h-auto" />
        ) : (
          <div className="text-center italic">Stiffness ellipsoid will appear here...</div>
        )}
      </div>
    </div>
  );
};

export default Controller;
