// MessageItem.tsx
import React from "react";
import MatrixDisplay from "./MatrixDisplay";

type MessageItemProps = {
  message: {
    sender: string;
    type: string;
    blobUrl?: string;
    imageUrl?: string | { file_url: string }; // Allow imageUrl to be either a string or an object
    dataUrl?: string;
  };
};

const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
  console.log("Rendering MessageItem with message:", message);

  return (
    <div
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
          <audio src={message.blobUrl} className="appearance-none" controls />
        ) : message.type === "image" ? (
          <img
          src={
            typeof message.imageUrl === "object" && message.imageUrl !== null
              ? message.imageUrl.file_url
              : message.imageUrl
          }
          alt="Image"
          className="w-full max-w-2xl h-auto mt-2"
        />
        
        ) : message.type === "matrix" ? (
          <MatrixDisplay dataUrl={message.dataUrl!} />
        ) : null}
      </div>
    </div>
  );
};

export default MessageItem;
