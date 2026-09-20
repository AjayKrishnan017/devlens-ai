import axios from "axios";

const API = axios.create({
    baseURL: "https://devlens-ai-xrnz.onrender.com/api/v1",

    headers: {
        "Content-Type": "application/json",
    },

    timeout: 120000,
});


export const analyzeCode = async (code) => {

    const response = await API.post(
        "/analyze",
        {
            code: code,
        }
    );

    return response.data;
};


export default API;