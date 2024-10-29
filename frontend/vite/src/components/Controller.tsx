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

  const handleImageUpload = async (event: any) => {
    const file = event.target.files[0];
    if (file) {
      if (file.size > 1 * 1024 * 1024) {
        const resizedFile = await resizeImage(file);
        uploadImage(resizedFile);
      } else {
        uploadImage(file);
      }
    }
  };

  const resizeImage = (file: File) => {
    return new Promise<File>((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);

      reader.onload = (event) => {
        const img = new Image();
        img.src = event.target?.result as string;

        img.onload = () => {
          const canvas = document.createElement("canvas");
          let width = img.width;
          let height = img.height;
          let quality = 0.7;

          if (file.size > 5 * 1024 * 1024) quality = 0.5;
          if (file.size > 10 * 1024 * 1024) quality = 0.3;

          const maxSize = 1024;
          if (width > maxSize || height > maxSize) {
            if (width > height) {
              height = (height * maxSize) / width;
              width = maxSize;
            } else {
              width = (width * maxSize) / height;
              height = maxSize;
            }
          }

          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext("2d");

          if (ctx) {
            ctx.drawImage(img, 0, 0, width, height);
            canvas.toBlob(
              (blob) => {
                if (blob) {
                  const resizedFile = new File([blob], file.name, {
                    type: "image/jpeg",
                    lastModified: Date.now(),
                  });
                  resolve(resizedFile);
                } else {
                  reject(new Error("Image resizing failed."));
                }
              },
              "image/jpeg",
              quality
            );
          }
        };
      };

      reader.onerror = (error) => reject(error);
    });
  };

  const uploadImage = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("https://summary-sunbird-dashing.ngrok-free.app/upload_image", formData, {
        timeout: 10000,
      });
      const imageURL = response.data;
      setImageURL(imageURL);

      // Add image message to chat history
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "me", type: "image", imageUrl: imageURL },
      ]);

      console.log("Image URL being sent:", imageURL);
      alert("Image uploaded successfully!");
    } catch (err) {
      console.error("Error uploading image:", err);
      alert("Error uploading image. Please try again.");
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
          setImageURL(null);
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
                    <img src={message.imageUrl} alt="Uploaded" className="w-48 h-auto mt-2" />
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
              <input
                type="file"
                accept="image/*"
                onChange={handleImageUpload}
                className="mb-4"
              />

              {/* Record/Stop Button */}
              <button
                onClick={handleRecordButtonClick}
                className="px-4 py-2 bg-blue-500 text-white rounded-md"
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
