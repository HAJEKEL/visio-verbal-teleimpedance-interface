import axios from "axios";

// Get the backend URL from the environment variable
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

if (!BACKEND_URL) {
    console.error("Backend URL is not defined in the environment variables.");
}

export const calibrate = () => {
    return axios.get(`${BACKEND_URL}/calibrate`);
};

export const captureSnapshot = async () => {
    const response = await axios.get(`${BACKEND_URL}/capture_snapshot`, {
        responseType: "blob",
    });
    return response.data;
};

export const uploadImage = async (formData: FormData) => {
    const response = await axios.post(`${BACKEND_URL}/upload_image`, formData, {
        timeout: 10000,
    });
    return response.data;
};

export const postAudio = (formData: FormData) => {
    return axios.post(`${BACKEND_URL}/post_audio`, formData, {
        responseType: "blob",
    });
};

export const resetConversation = () => {
    return axios.get(`${BACKEND_URL}/reset`);
};

export const startSigma = () => {
    return axios.get(`${BACKEND_URL}/sigma/start`);
};

export const stopSigma = () => {
    return axios.get(`${BACKEND_URL}/sigma/stop`);
};

export const setZeroSigma = () => {
    return axios.get(`${BACKEND_URL}/sigma/set_zero`);
};

export const autoinitSigma = () => {
    return axios.get(`${BACKEND_URL}/sigma/autoinit`);
};

export const initializeSigma = () => {
    return axios.get(`${BACKEND_URL}/sigma/initialize`);
};
