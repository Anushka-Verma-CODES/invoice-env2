import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api",
  timeout: 30000,
});

export const resetEnv = async (batchSize = 12) => {
  const response = await api.post("/reset", { batch_size: batchSize });
  return response.data;
};

export const stepEnv = async (action) => {
  const response = await api.post("/step", { action });
  return response.data;
};

export const getState = async () => {
  const response = await api.get("/state");
  return response.data;
};

export const runAgent = async (batchSize = 12, mode = "auto") => {
  const response = await api.post("/run-agent", { batch_size: batchSize, mode });
  return response.data;
};

export const getResults = async (limit = 20) => {
  const response = await api.get("/results", { params: { limit } });
  return response.data;
};

export default api;
