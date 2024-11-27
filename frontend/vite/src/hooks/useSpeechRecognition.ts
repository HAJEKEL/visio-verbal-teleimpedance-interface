// useSpeechRecognition.ts
import { useEffect, useRef } from "react";

type UseSpeechRecognitionOptions = {
  onResult: (transcript: string) => void;
  isHandsfree: boolean;
};

const useSpeechRecognition = ({
  onResult,
  isHandsfree,
}: UseSpeechRecognitionOptions) => {
  const recognitionRef = useRef<any>(null);
  const onResultRef = useRef(onResult);

  // Update the ref whenever onResult changes
  useEffect(() => {
    onResultRef.current = onResult;
  }, [onResult]);

  useEffect(() => {
    if (isHandsfree) {
      const SpeechRecognition =
        (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition) {
        const recognitionInstance = new SpeechRecognition();
        recognitionInstance.continuous = true;
        recognitionInstance.lang = "en-US";
        recognitionInstance.interimResults = false;
        recognitionInstance.maxAlternatives = 1;

        recognitionInstance.onresult = (event: any) => {
          const last = event.results.length - 1;
          const transcript = event.results[last][0].transcript.trim().toLowerCase();
          console.log("Recognized speech:", transcript);

          onResultRef.current(transcript);
        };

        recognitionInstance.onerror = (event: any) => {
          console.error("Speech recognition error:", event.error);
          // Restart the recognition instance
          recognitionInstance.stop();
          recognitionInstance.start();
        };

        recognitionInstance.start();
        recognitionRef.current = recognitionInstance;
      } else {
        console.warn("Speech recognition not supported in this browser.");
      }
    }

    // Cleanup when isHandsfree is false or on unmount
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
        recognitionRef.current = null;
      }
    };
  }, [isHandsfree]);

  return recognitionRef.current;
};

export default useSpeechRecognition;
