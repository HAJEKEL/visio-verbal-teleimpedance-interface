// MessageItem.tsx
import React from "react";
import MatrixDisplay from "./MatrixDisplay";

type MessageItemProps = {
  message: {
    sender: string;
    type: string;
    blobUrl?: string;
    imageUrl?: string;
    dataUrl?: string;
  };
};

const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
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
            src={message.imageUrl}
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
