import { InternalConfig } from "@/types/internal-config";
import { Session } from "next-auth";
import { KeepApiError, KeepApiReadOnlyError } from "./KeepApiError";
import { getApiUrlFromConfig } from "@/shared/lib/getApiUrlFromConfig";
import { getApiURL } from "@/utils/apiUrl";

export class ApiClient {
  constructor(
    private readonly session: Session | null,
    private readonly config: InternalConfig | null,
    private readonly isServer: boolean
  ) {}

  isReady() {
    return !!this.session && !!this.config;
  }

  getHeaders() {
    if (!this.session || !this.session.accessToken) {
      throw new Error("No valid session or access token found");
    }
    return {
      Authorization: `Bearer ${this.session.accessToken}`,
    };
  }

  async handleResponse(response: Response, url: string) {
    // Ensure that the fetch was successful
    if (!response.ok) {
      // if the response has detail field, throw the detail field
      if (response.headers.get("content-type")?.includes("application/json")) {
        const data = await response.json();
        if (response.status === 401) {
          throw new KeepApiError(
            `${data.message || data.detail}`,
            url,
            `You probably just need to sign in again.`,
            data,
            response.status
          );
        }
        if (response.status === 403 && data.detail.includes("Read only")) {
          throw new KeepApiReadOnlyError(
            "Application is in read-only mode",
            url,
            "The application is currently in read-only mode. Modifications are not allowed.",
            { readOnly: true },
            403
          );
        } else {
          throw new KeepApiError(
            `${data.message || data.detail}`,
            url,
            `Please try again. If the problem persists, please contact support.`,
            data,
            response.status
          );
        }
      }
      throw new Error("An error occurred while fetching the data.");
    }

    try {
      return await response.json();
    } catch (error) {
      console.error(error);
      return response.text();
    }
  }

  async request<T = any>(
    url: string,
    requestInit: RequestInit = {}
  ): Promise<T> {
    if (!this.config) {
      throw new Error("No config found");
    }

    // Add read-only check for modification requests
    if (this.config.READ_ONLY && requestInit.method !== "GET") {
      throw new KeepApiReadOnlyError(
        "Application is in read-only mode",
        url,
        "The application is currently in read-only mode. Modifications are not allowed.",
        { readOnly: true },
        403
      );
    }

    const apiUrl = this.isServer
      ? getApiURL()
      : getApiUrlFromConfig(this.config);
    const fullUrl = apiUrl + url;

    const response = await fetch(fullUrl, {
      ...requestInit,
      headers: {
        ...this.getHeaders(),
        ...requestInit.headers,
      },
    });
    return this.handleResponse(response, url);
  }

  async get<T = any>(url: string, requestInit: RequestInit = {}) {
    return this.request<T>(url, { method: "GET", ...requestInit });
  }

  async post<T = any>(
    url: string,
    data?: any,
    { headers, ...requestInit }: RequestInit = {}
  ) {
    return this.request<T>(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...headers,
      },
      body: data ? JSON.stringify(data) : undefined,
      ...requestInit,
    });
  }

  async put<T = any>(
    url: string,
    data?: any,
    { headers, ...requestInit }: RequestInit = {}
  ) {
    return this.request<T>(url, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...headers,
      },
      body: data ? JSON.stringify(data) : undefined,
      ...requestInit,
    });
  }

  async patch<T = any>(
    url: string,
    data?: any,
    { headers, ...requestInit }: RequestInit = {}
  ) {
    return this.request<T>(url, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        ...headers,
      },
      body: data ? JSON.stringify(data) : undefined,
      ...requestInit,
    });
  }

  async delete<T = any>(
    url: string,
    data?: any,
    { headers, ...requestInit }: RequestInit = {}
  ) {
    return this.request<T>(url, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        ...headers,
      },
      body: data ? JSON.stringify(data) : undefined,
      ...requestInit,
    });
  }
}
