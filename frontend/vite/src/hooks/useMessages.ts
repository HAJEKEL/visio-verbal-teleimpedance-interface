import { useState } from "react";
import { resetConversation, postAudio } from "../services/apiService";

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

        fetch(blobUrl)
            .then((res) => res.blob())
            .then(async (blob) => {
                const formData = new FormData();
                formData.append("file", blob, "myFile.wav");

                if (imageURL) {
                    formData.append("image_url", imageURL);
                    setImageURL(null);
                }

                try {
                    const { data, headers } = await postAudio(formData);
                    const audioUrl = createBlobURL(data);

                    const newMessages = [];

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
                window.alert("Conversation history has been reset.");
            } catch (error: any) {
                console.error("Failed to reset conversation history:", error);
                window.alert("Failed to reset conversation history. Please try again.");
            }
        };

        setConfirmationDialog({ message, onConfirm });
    };

    return { messages, setMessages, handleReset, handleStop, createBlobURL };
};

export default useMessages;
