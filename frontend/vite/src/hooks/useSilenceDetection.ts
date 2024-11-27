import { useEffect, useRef } from "react";

type UseSilenceDetectionOptions = {
    analyserNode: AnalyserNode | null;
    isRecording: boolean;
    onSilence: () => void;
    silenceDelay?: number;
    threshold?: number;
};

const useSilenceDetection = ({
    analyserNode,
    isRecording,
    onSilence,
    silenceDelay = 3000,
    threshold = -50,
}: UseSilenceDetectionOptions) => {
    const silenceStartRef = useRef<number | null>(null);

    useEffect(() => {
        if (!analyserNode || !isRecording) {
            return;
        }

        const dataArray = new Uint8Array(analyserNode.fftSize);

        const checkSilence = () => {
            analyserNode.getByteFrequencyData(dataArray);
            let values = 0;
            for (let i = 0; i < dataArray.length; i++) {
                values += dataArray[i];
            }
            const average = values / dataArray.length;
            const avgDecibels = 20 * Math.log10(average / 255);

            if (avgDecibels < threshold) {
                if (!silenceStartRef.current) {
                    silenceStartRef.current = performance.now();
                } else {
                    const elapsed = performance.now() - silenceStartRef.current;
                    if (elapsed > silenceDelay) {
                        onSilence();
                        return; // Stop checking
                    }
                }
            } else {
                silenceStartRef.current = null;
            }

            if (isRecording) {
                requestAnimationFrame(checkSilence);
            }
        };

        checkSilence();

        // Clean up function
        return () => {
            silenceStartRef.current = null;
        };
    }, [analyserNode, isRecording, onSilence, silenceDelay, threshold]);
};

export default useSilenceDetection;
