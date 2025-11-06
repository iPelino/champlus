import axiosInstance from '../../../lib/axios';
import type { TokenPair } from '../../../types/api';
import type { LoginCredentials, RegisterData } from '../types';
import type { User } from '../../../types';

/**
 * Authenticate user and obtain JWT tokens
 */
export const loginUser = async (credentials: LoginCredentials): Promise<TokenPair> => {
  const response = await axiosInstance.post<TokenPair>('/auth/token/', credentials);
  return response.data;
};

/**
 * Refresh the access token
 */
export const refreshAccessToken = async (refreshToken: string): Promise<{ access: string }> => {
  const response = await axiosInstance.post<{ access: string }>('/auth/token/refresh/', {
    refresh: refreshToken,
  });
  return response.data;
};

/**
 * Register a new user
 */
export const registerUser = async (data: RegisterData): Promise<User> => {
  const response = await axiosInstance.post<User>('/users/register/', data);
  return response.data;
};

/**
 * Get current authenticated user's profile
 */
export const getCurrentUser = async (): Promise<User> => {
  const response = await axiosInstance.get<User>('/users/me/');
  return response.data;
};

/**
 * Logout user (clear tokens)
 */
export const logoutUser = (): void => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};
