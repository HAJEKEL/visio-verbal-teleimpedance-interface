import { useState } from "react";
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
};

const useAudioRecorder = ({ onStop }: UseAudioRecorderOptions) => {
    const [isRecording, setIsRecording] = useState(false);
    const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
    const [audioContext, setAudioContext] = useState<AudioContext | null>(null);
    const [analyser, setAnalyser] = useState<AnalyserNode | null>(null);

    const audioConstraints = {
        audio: {
            channelCount: 1,
            sampleRate: 16000,
        },
    };

    const createBlobURL = (data: any) => {
        const blob = new Blob([data], { type: "audio/mpeg" });
        return window.URL.createObjectURL(blob);
    };

    const startRecording = () => {
        navigator.mediaDevices.getUserMedia(audioConstraints).then((stream) => {
            const recorder = new MediaRecorder(stream);
            recorder.start();
            setMediaRecorder(recorder);
            setIsRecording(true);

            // Set up audio context and analyser for silence detection
            const audioCtx = new AudioContext();
            const source = audioCtx.createMediaStreamSource(stream);
            const analyserNode = audioCtx.createAnalyser();
            analyserNode.fftSize = 2048;
            source.connect(analyserNode);
            setAudioContext(audioCtx);
            setAnalyser(analyserNode);

            recorder.ondataavailable = (e: any) => {
                const audioBlob = e.data;
                const audioUrl = createBlobURL(audioBlob);
                onStop(audioUrl);
            };
        });
    };

    const stopRecording = () => {
        if (mediaRecorder) {
            mediaRecorder.stop();
            setIsRecording(false);
            if (audioContext) {
                audioContext.close();
                setAudioContext(null);
                setAnalyser(null);
            }
        }
    };

    useSilenceDetection({
        analyserNode: analyser,
        isRecording,
        onSilence: stopRecording,
    });

    return { isRecording, startRecording, stopRecording };
};

export default useAudioRecorder;
