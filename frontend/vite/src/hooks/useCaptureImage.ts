import { useState } from "react";
import { captureSnapshot, uploadImage } from "../services/apiService";

type UseCaptureImageOptions = {
    setMessages: React.Dispatch<React.SetStateAction<any[]>>;
};

const useCaptureImage = ({ setMessages }: UseCaptureImageOptions) => {
    const [imageURL, setImageURL] = useState<string | null>(null);

    /**
     * Helper function to show a temporary (ephemeral) message.
     * This will be automatically removed from the message list after 3 seconds.
     */
    const showEphemeralMessage = (content: string) => {
        // Create a unique ID so we can remove this message later
        const ephemeralId = Date.now().toString();

        // 1. Add the ephemeral message to the messages list
        setMessages((prev) => [
            ...prev,
            { sender: "system", type: "text", content, ephemeralId },
        ]);

        // 2. Remove the ephemeral message after 3 seconds
        setTimeout(() => {
            setMessages((prev) => prev.filter((msg) => msg.ephemeralId !== ephemeralId));
        }, 3000);
    };

    const handleCaptureImage = async () => {
        try {
            const blob = await captureSnapshot();

            const file = new File([blob], "snapshot.jpg", { type: "image/jpeg" });
            const formData = new FormData();
            formData.append("file", file);

            const uploadedImageResponse = await uploadImage(formData);
            const uploadedImageURL = uploadedImageResponse.file_url; // Extract the file_url
            setImageURL(uploadedImageURL);

            console.log("Uploaded Image URL:", uploadedImageURL);
            setMessages((prevMessages) => [
                ...prevMessages,
                { sender: "me", type: "image", imageUrl: uploadedImageURL },
            ]);

            // Show ephemeral success message
            showEphemeralMessage("Snapshot captured and uploaded successfully!");
        } catch (err) {
            console.error("Error capturing or uploading snapshot:", err);

            // Show ephemeral error message
            showEphemeralMessage("Failed to capture or upload snapshot. Please try again.");
        }
    };

    return { handleCaptureImage, imageURL, setImageURL };
};

export default useCaptureImage;
