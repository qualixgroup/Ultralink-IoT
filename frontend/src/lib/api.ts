import { getToken } from "./auth";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

type ApiOptions = RequestInit & {
  authenticated?: boolean;
};

export async function apiRequest<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");

  if (options.authenticated !== false) {
    const token = getToken();
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Falha na comunicação com a API");
  }

  return response.json() as Promise<T>;
}
