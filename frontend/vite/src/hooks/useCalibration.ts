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
    const handleCalibration = async () => {
        const message =
            "Place the calibration sticker on the display screen and make sure you look at the center before you say OK.";
        const onConfirm = async () => {
            setIsCalibrating(true);
            let attempts = 3;

            while (attempts > 0) {
                try {
                    const response = await calibrate();
                    window.alert(response.data.status || "Calibration successful!");
                    break;
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
            setConfirmationDialog(null); // Clear the confirmation dialog after completion
        };

        setConfirmationDialog({ message, onConfirm });
    };

    return { handleCalibration };
};

export default useCalibration;
