import { useState } from "react";
import { captureSnapshot, uploadImage } from "../services/apiService";

type UseCaptureImageOptions = {
    setMessages: React.Dispatch<React.SetStateAction<any[]>>;
};

const useCaptureImage = ({ setMessages }: UseCaptureImageOptions) => {
    const [imageURL, setImageURL] = useState<string | null>(null);

    const handleCaptureImage = async () => {
        try {
            const blob = await captureSnapshot();

            const file = new File([blob], "snapshot.jpg", { type: "image/jpeg" });
            const formData = new FormData();
            formData.append("file", file);

            const uploadedImageURL = await uploadImage(formData);
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

    return { handleCaptureImage, imageURL, setImageURL };
};

export default useCaptureImage;
