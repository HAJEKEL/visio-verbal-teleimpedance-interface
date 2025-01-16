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
     * We'll keep the mic open for continuous speech recognition.
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

    // Distinguish manual vs. unexpected stops
    const isManualStopRef = useRef(false);

    const audioConstraints = {
        audio: {
            channelCount: 1,
            sampleRate: 16000,
        },
    };

    const createSafeBlobURL = (data: Blob) => {
        const mimeType = data.type || "audio/webm";
        const blob = new Blob([data], { type: mimeType });
        return window.URL.createObjectURL(blob);
    };

    const startRecording = () => {
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

                isManualStopRef.current = false;

                // Create AudioContext for the recorder (separate from speech recognition)
                const audioCtx = new AudioContext();
                const source = audioCtx.createMediaStreamSource(stream);
                const analyserNode = audioCtx.createAnalyser();
                analyserNode.fftSize = 2048;
                source.connect(analyserNode);
                setAudioContext(audioCtx);
                setAnalyser(analyserNode);

                recorder.ondataavailable = (e: BlobEvent) => {
                    if (e.data.size > 0) {
                        const audioUrl = createSafeBlobURL(e.data);
                        onStop(audioUrl, imageURL, setImageURL);
                    } else {
                        console.error("No audio data available.");
                    }
                };

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

    const handleUnexpectedStopCleanup = () => {
        setIsRecording(false);
        setMediaRecorder(null);

        // If it's unexpected, we can still close the AudioContext
        // or you can check isHandsfree if you want to keep it open.
        if (audioContext && audioContext.state !== "closed") {
            audioContext.close();
        }
        setAudioContext(null);
        setAnalyser(null);

        console.log("Cleaned up after unexpected stop.");
    };

    const stopRecording = () => {
        if (!isRecording) {
            console.warn("No active recording to stop.");
            return;
        }

        isManualStopRef.current = true;
        setIsRecording(false);

        if (mediaRecorder && mediaRecorder.state === "recording") {
            mediaRecorder.stop();
        }

        // Only close the audio context if NOT in handsfree mode
        // so we don't kill the mic for speech recognition.
        if (!isHandsfree) {
            if (audioContext && audioContext.state !== "closed") {
                audioContext.close();
            }
            setAudioContext(null);
            setAnalyser(null);
        }

        setMediaRecorder(null);

        console.log("Recording stopped and resources cleaned up (manual stop).");
    };

    useSilenceDetection({
        analyserNode: isHandsfree ? analyser : null,
        isRecording: isHandsfree ? isRecording : false,
        onSilence: stopRecording,
        threshold: -60,
        silenceDelay: 5000,
    });

    return { isRecording, startRecording, stopRecording };
};

export default useAudioRecorder;
