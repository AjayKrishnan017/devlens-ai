import axios from "axios";

const API = axios.create({
    baseURL: "http://127.0.0.1:8000/api/v1",
    headers: {
        "Content-Type": "application/json",
    },
});

export const analyzeCode = async (code) => {
    const response = await API.post("/analyze", {
        code,
    });

    return response.data;
};

export default API;