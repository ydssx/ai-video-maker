import axios from "axios";

const TOKEN_KEY = "avm_token";

export const api = axios.create({
  baseURL: "",
  timeout: 60000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export function saveToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export type User = {
  id: number;
  username: string;
  email?: string | null;
  is_active: boolean;
};

export type Scene = {
  text: string;
  duration: number;
  image_keywords: string[];
  transition: string;
};

export type Script = {
  title: string;
  scenes: Scene[];
  total_duration: number;
  style: string;
  source?: string;
};

export type VideoJob = {
  id: string;
  title: string;
  status: string;
  progress: number;
  message: string;
  download_url?: string | null;
  duration: number;
  error?: string | null;
};

export type Project = {
  id: number;
  title: string;
  description?: string | null;
  script: Script | Record<string, unknown>;
  config: Record<string, unknown>;
  status: string;
};

export async function login(username: string, password: string) {
  const body = new URLSearchParams();
  body.set("username", username);
  body.set("password", password);
  const { data } = await api.post("/api/auth/login", body, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  saveToken(data.access_token);
  return data;
}

export async function register(username: string, password: string, email?: string) {
  const { data } = await api.post("/api/auth/register", { username, password, email });
  return data as User;
}

export async function fetchMe() {
  const { data } = await api.get("/api/auth/me");
  return data as User;
}

export async function generateScript(payload: {
  topic: string;
  style: string;
  duration: string;
}) {
  const { data } = await api.post("/api/script/generate", payload);
  return data as Script;
}

export async function createVideo(payload: {
  script: Script;
  background_color?: string;
  export_config?: { resolution: string; fps: number; format: string };
}) {
  const { data } = await api.post("/api/video/create", payload);
  return data as VideoJob;
}

export async function getVideo(id: string) {
  const { data } = await api.get(`/api/video/${id}`);
  return data as VideoJob;
}

export async function listProjects() {
  const { data } = await api.get("/api/projects/");
  return data as Project[];
}

export async function saveProject(payload: {
  title: string;
  description?: string;
  script: Script;
  config?: Record<string, unknown>;
}) {
  const { data } = await api.post("/api/projects/", payload);
  return data as Project;
}
