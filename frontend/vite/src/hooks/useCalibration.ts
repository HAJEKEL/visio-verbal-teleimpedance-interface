import { useState } from "react";
import { calibrate } from "../services/apiService";

type UseCalibrationOptions = {
    setIsCalibrating: React.Dispatch<React.SetStateAction<boolean>>;
    setConfirmationDialog: React.Dispatch<
        React.SetStateAction<{
            message: string;
            onConfirm: () => void;
        } | null>
    >;
};

const useCalibration = ({
    setIsCalibrating,
    setConfirmationDialog,
}: UseCalibrationOptions) => {
    // -----------------------------------------------------------------
    // 1. Local state to store ephemeral notifications (non-blocking)
    // -----------------------------------------------------------------
    const [notifications, setNotifications] = useState<
        { id: string; message: string }[]
    >([]);

    /**
     * Helper: Show a notification and remove it automatically after 3 seconds.
     */
    const showEphemeralNotification = (msg: string) => {
        const id = Date.now().toString();
        setNotifications((prev) => [...prev, { id, message: msg }]);
        setTimeout(() => {
            setNotifications((prev) => prev.filter((n) => n.id !== id));
        }, 3000);
    };

    const handleCalibration = async () => {
        const message =
            "Place the calibration sticker on the display screen and make sure you look at the center before you say OK.";

        const onConfirm = async () => {
            setIsCalibrating(true);
            let attempts = 3;

            while (attempts > 0) {
                try {
                    const response = await calibrate();
                    const successMessage = response.data?.status || "Calibration successful!";
                    // Show success ephemeral notification
                    showEphemeralNotification(successMessage);
                    break;
                } catch (error: any) {
                    console.error("Calibration failed:", error);
                    attempts -= 1;

                    if (attempts === 0) {
                        const errorMessage =
                            error?.response?.data?.detail ||
                            "Calibration failed! Please try again.";
                        // Show error ephemeral notification
                        showEphemeralNotification(errorMessage);
                    }
                }
            }

            setIsCalibrating(false);
            setConfirmationDialog(null); // Clear the confirmation dialog after completion
        };

        setConfirmationDialog({ message, onConfirm });
    };

    return {
        handleCalibration,
        notifications, // Expose these if you need to render the ephemeral notifications in your UI
    };
};

export default useCalibration;
