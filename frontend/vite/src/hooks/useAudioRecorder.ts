import { useState, useRef } from "react";
import useSilenceDetection from "./useSilenceDetection";

type UseAudioRecorderOptions = {
    onStop: (
        blobUrl: string,
        imageURL: string | null,
        setImageURL: React.Dispatch<React.SetStateAction<string | null>>
    ) => void;
    imageURL: string | null;
    setImageURL: React.Dispatch<React.SetStateAction<string | null>>;
    setMessages: React.Dispatch<React.SetStateAction<any[]>>;
    createBlobURL: (data: any) => string;
    setIsLoading: React.Dispatch<React.SetStateAction<boolean>>;

    /**
     * If true, silence detection is used to automatically
     * stop the recording upon silence.
     */
    isHandsfree: boolean;
};

const useAudioRecorder = ({
    onStop,
    isHandsfree,
    imageURL,
    setImageURL,
    setMessages,
    createBlobURL,
    setIsLoading,
}: UseAudioRecorderOptions) => {
    const [isRecording, setIsRecording] = useState(false);
    const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
    const [audioContext, setAudioContext] = useState<AudioContext | null>(null);
    const [analyser, setAnalyser] = useState<AnalyserNode | null>(null);

    /**
     * Flag to detect if we're deliberately stopping the recording
     * (manual click or handsfree silence detection).
     */
    const isManualStopRef = useRef(false);

    const audioConstraints = {
        audio: {
            channelCount: 1,
            sampleRate: 16000,
        },
    };

    // Safer approach: use e.data.type if available
    const createSafeBlobURL = (data: Blob) => {
        const mimeType = data.type || "audio/webm"; // default fallback
        const blob = new Blob([data], { type: mimeType });
        return window.URL.createObjectURL(blob);
    };

    const startRecording = () => {
        // Prevent starting a new recording if one is already in progress
        if (isRecording) {
            console.warn("Recording is already in progress.");
            return;
        }

        navigator.mediaDevices
            .getUserMedia(audioConstraints)
            .then((stream) => {
                const recorder = new MediaRecorder(stream);
                recorder.start();
                setMediaRecorder(recorder);
                setIsRecording(true);

                // Reset the manual stop flag
                isManualStopRef.current = false;

                // Create AudioContext & AnalyserNode only if needed
                const audioCtx = new AudioContext();
                const source = audioCtx.createMediaStreamSource(stream);
                const analyserNode = audioCtx.createAnalyser();
                analyserNode.fftSize = 2048;
                source.connect(analyserNode);
                setAudioContext(audioCtx);
                setAnalyser(analyserNode);

                // When recording is fully stopped (manually or unexpectedly),
                // ondataavailable fires once with the recorded Blob.
                recorder.ondataavailable = (e: BlobEvent) => {
                    if (e.data.size > 0) {
                        const audioUrl = createSafeBlobURL(e.data);
                        onStop(audioUrl, imageURL, setImageURL);
                    } else {
                        console.error("No audio data available.");
                    }
                };

                // Onstop is triggered for ANY reason (manual or unexpected).
                // We'll check our manualStopRef to see if it was expected.
                recorder.onstop = () => {
                    if (!isManualStopRef.current) {
                        console.log("Recording stopped unexpectedly.");
                        handleUnexpectedStopCleanup();
                    }
                };
            })
            .catch((error) => {
                console.error("Error accessing microphone:", error);
            });
    };

    /**
     * Cleanup after an unexpected stop (mic disconnected, etc.)
     * or a scenario that is not triggered by manual stop.
     */
    const handleUnexpectedStopCleanup = () => {
        setIsRecording(false);

        if (audioContext && audioContext.state !== "closed") {
            audioContext.close();
        }
        setAudioContext(null);
        setAnalyser(null);

        setMediaRecorder(null);
        console.log("Cleaned up after unexpected stop.");
    };

    /**
     * Called for a deliberate stop (button click or silence detection).
     */
    const stopRecording = () => {
        if (!isRecording) {
            console.warn("No active recording to stop.");
            return;
        }

        // Mark this as a manual stop (including silence detection in handsfree).
        isManualStopRef.current = true;
        setIsRecording(false);

        if (mediaRecorder && mediaRecorder.state === "recording") {
            mediaRecorder.stop();
        }

        // Clean up audio context
        if (audioContext && audioContext.state !== "closed") {
            audioContext.close();
        }
        setAudioContext(null);
        setAnalyser(null);

        setMediaRecorder(null);

        console.log("Recording stopped and resources cleaned up (manual stop).");
    };

    // -------------------------------------------------------------
    // Only activate silence detection if we're in "handsfree" mode
    // -------------------------------------------------------------
    useSilenceDetection({
        analyserNode: isHandsfree ? analyser : null,
        isRecording: isHandsfree ? isRecording : false,
        onSilence: stopRecording,
        // Optionally tweak these to avoid immediate stops if user
        // takes a second to speak:
        // threshold: -60,
        // silenceDelay: 5000,
    });

    return { isRecording, startRecording, stopRecording };
};

export default useAudioRecorder;
