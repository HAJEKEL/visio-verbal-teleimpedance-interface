// MessageList.tsx
import React from "react";
import MessageItem from "./MessageItem";

type MessageListProps = {
  messages: any[];
  isLoading: boolean;
  isCalibrating: boolean;
  messagesEndRef: React.RefObject<HTMLDivElement>;
};

const MessageList: React.FC<MessageListProps> = ({
  messages,
  isLoading,
  isCalibrating,
  messagesEndRef,
}) => {
  return (
    <>
      {messages?.map((message, index) => (
        <MessageItem key={index + message.sender} message={message} />
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
    </>
  );
};

export default MessageList;
