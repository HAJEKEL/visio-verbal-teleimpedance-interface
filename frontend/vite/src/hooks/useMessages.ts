import { useState } from "react";
import {
    resetConversation,
    postAudio,
    startSigma,
    stopSigma,
    setZeroSigma,
    autoinitSigma,
    initializeSigma,
} from "../services/apiService";

type UseMessagesOptions = {
    setIsLoading: React.Dispatch<React.SetStateAction<boolean>>;
    setConfirmationDialog: React.Dispatch<
        React.SetStateAction<{
            message: string;
            onConfirm: () => void;
        } | null>
    >;
};

const useMessages = ({ setIsLoading, setConfirmationDialog }: UseMessagesOptions) => {
    const [messages, setMessages] = useState<any[]>([]);

    const createBlobURL = (data: any) => {
        const blob = new Blob([data], { type: "audio/mpeg" });
        return window.URL.createObjectURL(blob);
    };

    const handleStop = async (
        blobUrl: string,
        imageURL: string | null,
        setImageURL: React.Dispatch<React.SetStateAction<string | null>>
    ) => {
        setIsLoading(true);

        const myMessage = { sender: "me", type: "audio", blobUrl };
        setMessages((prevMessages) => [...prevMessages, myMessage]);
        console.log("Blob URL:", blobUrl); // Log the audio blob URL
        console.log("Image URL before adding to formData:", imageURL); // Log the image URL

        fetch(blobUrl)
            .then((res) => res.blob())
            .then(async (blob) => {
                const formData = new FormData();
                formData.append("file", blob, "myFile.wav");

                // Ensure imageURL is properly appended as a string
                if (imageURL) {
                    const extractedUrl = typeof imageURL === "object" && "file_url" in imageURL ? imageURL.file_url : imageURL;
                    console.log("Adding image URL to formData:", extractedUrl); // Log the extracted image URL
                    formData.append("image_url", extractedUrl);
                    setImageURL(null);
                } else {
                    console.warn("No image URL provided for this audio message.");
                }

                try {
                    const { data, headers } = await postAudio(formData);
                    const audioUrl = createBlobURL(data);

                    const newMessages: Array<{ sender: string; type: string; blobUrl?: string; dataUrl?: string; imageUrl?: string }> = [];

                    const matriceMessage = {
                        sender: "matrice",
                        type: "audio",
                        blobUrl: audioUrl,
                    };
                    newMessages.push(matriceMessage);

                    const matrixUrl = headers["x-matrix-url"];
                    const ellipsoidUrl = headers["x-ellipsoid-url"];

                    if (matrixUrl) {
                        newMessages.push({
                            sender: "matrice",
                            type: "matrix",
                            dataUrl: matrixUrl,
                        });
                    }

                    if (ellipsoidUrl) {
                        newMessages.push({
                            sender: "matrice",
                            type: "image",
                            imageUrl: ellipsoidUrl,
                        });
                    }

                    setMessages((prevMessages) => [...prevMessages, ...newMessages]);
                    setIsLoading(false);

                    const audio = new Audio(audioUrl);
                    audio.play();
                } catch (err) {
                    console.error(err);
                    setIsLoading(false);
                }
            });
    };

    const handleReset = async () => {
        const message = "Are you sure you want to reset the conversation history?";
        const onConfirm = async () => {
            try {
                await resetConversation();
                setMessages([]);
                setConfirmationDialog(null); // Close the dialog explicitly
                window.alert("Conversation history has been reset.");
            } catch (error: any) {
                console.error("Failed to reset conversation history:", error);
                setConfirmationDialog(null); // Close the dialog even if the reset fails
                window.alert("Failed to reset conversation history. Please try again.");
            }
        };

        setConfirmationDialog({ message, onConfirm });
    };

    // Sigma7 action handlers
    const handleStartSigma = async () => {
        setIsLoading(true);
        try {
            await startSigma();
            setMessages((prevMessages) => [
                ...prevMessages,
                { sender: "system", type: "text", content: "Sigma7 server started successfully." },
            ]);
        } catch (error) {
            console.error("Failed to start Sigma7 server:", error);
            setMessages((prevMessages) => [
                ...prevMessages,
                { sender: "system", type: "text", content: "Failed to start Sigma7 server." },
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleStopSigma = async () => {
        setIsLoading(true);
        try {
            await stopSigma();
            setMessages((prevMessages) => [
                ...prevMessages,
                { sender: "system", type: "text", content: "Sigma7 server stopped successfully." },
            ]);
        } catch (error) {
            console.error("Failed to stop Sigma7 server:", error);
            setMessages((prevMessages) => [
                ...prevMessages,
                { sender: "system", type: "text", content: "Failed to stop Sigma7 server." },
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSetZeroSigma = async () => {
        setIsLoading(true);
        try {
            await setZeroSigma();
            setMessages((prevMessages) => [
                ...prevMessages,
                { sender: "system", type: "text", content: "Sigma7 server set to zero successfully." },
            ]);
        } catch (error) {
            console.error("Failed to set Sigma7 server zero position:", error);
            setMessages((prevMessages) => [
                ...prevMessages,
                { sender: "system", type: "text", content: "Failed to set Sigma7 server zero position." },
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleAutoinitSigma = async () => {
        setIsLoading(true);
        try {
            await autoinitSigma();
            setMessages((prevMessages) => [
                ...prevMessages,
                { sender: "system", type: "text", content: "Sigma7 server autoinit completed successfully." },
            ]);
        } catch (error) {
            console.error("Failed to autoinit Sigma7 server:", error);
            setMessages((prevMessages) => [
                ...prevMessages,
                { sender: "system", type: "text", content: "Failed to autoinit Sigma7 server." },
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleInitializeSigma = async () => {
        setIsLoading(true);
        try {
            await initializeSigma();
            setMessages((prevMessages) => [
                ...prevMessages,
                { sender: "system", type: "text", content: "Sigma7 initialized successfully." },
            ]);
        } catch (error) {
            console.error("Failed to initialize Sigma7:", error);
            setMessages((prevMessages) => [
                ...prevMessages,
                { sender: "system", type: "text", content: "Failed to initialize Sigma7." },
            ]);
        } finally {
            setIsLoading(false);
        }
    };


    return {
        messages,
        setMessages,
        handleReset,
        handleStop,
        handleStartSigma,
        handleStopSigma,
        handleSetZeroSigma,
        handleAutoinitSigma,
        handleInitializeSigma,
        createBlobURL,
    };
};

export default useMessages;
