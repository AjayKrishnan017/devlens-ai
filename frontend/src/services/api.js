import axios from "axios";

const API = axios.create({
    baseURL: "https://devlens-ai-xrnz.onrender.com",
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