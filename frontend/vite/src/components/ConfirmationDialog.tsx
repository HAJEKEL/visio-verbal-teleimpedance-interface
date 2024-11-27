import React from "react";

type ConfirmationDialogProps = {
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
};

const ConfirmationDialog: React.FC<ConfirmationDialogProps> = ({
  message,
  onConfirm,
  onCancel,
}) => {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
      <div className="bg-white p-6 rounded-md">
        <p>{message}</p>
        <div className="mt-4 flex justify-end">
          <button
            onClick={() => {
              onConfirm();
            }}
            className="px-4 py-2 bg-blue-500 text-white rounded-md mr-2"
          >
            Continue
          </button>
          <button
            onClick={onCancel}
            className="px-4 py-2 bg-gray-500 text-white rounded-md"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationDialog;
