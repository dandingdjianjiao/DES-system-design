/**
 * API client configuration using Axios
 * Base URL: http://localhost:8000 (configurable via VITE_API_BASE_URL)
 */

import axios, { AxiosError } from 'axios';
import type { AxiosInstance } from 'axios';
import { message } from 'antd';
import type { ErrorResponse } from '../types';

// Create axios instance with default config
const api: AxiosInstance = axios.create({
  // Use empty string for nginx proxy, or full URL for direct backend access
  // Note: undefined check prevents empty string from falling back to default
  baseURL: import.meta.env.VITE_API_BASE_URL !== undefined
    ? import.meta.env.VITE_API_BASE_URL
    : 'http://localhost:8000',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if needed in the future
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError<ErrorResponse>) => {
    // Handle different error status codes
    if (error.response) {
      const { status, data } = error.response;

      switch (status) {
        case 400:
          message.error(data.message || 'Invalid request parameters');
          break;
        case 404:
          message.error(data.message || 'Resource not found');
          break;
        case 500:
          message.error(data.message || 'Internal server error');
          break;
        default:
          message.error(data.message || 'An error occurred');
      }
    } else if (error.request) {
      // Request was made but no response received
      message.error('Cannot connect to server. Please check if the backend is running.');
    } else {
      // Something happened in setting up the request
      message.error(`Error: ${error.message}`);
    }

    return Promise.reject(error);
  }
);

export default api;
