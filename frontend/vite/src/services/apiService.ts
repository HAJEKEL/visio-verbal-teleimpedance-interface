import axios from "axios";

const BACKEND_URL = "http://localhost:8000";

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
