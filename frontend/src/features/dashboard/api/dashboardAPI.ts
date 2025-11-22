import axiosInstance from '../../../lib/axios';
import type { Group, Transaction } from '../../../types';
import type { PaginatedResponse } from '../../../types/api';

/**
 * Fetch all groups for the current user
 */
export const fetchGroups = async (): Promise<Group[]> => {
  const response = await axiosInstance.get<PaginatedResponse<Group>>('/groups/');
  return response.data.results;
};

/**
 * Fetch a single group by ID
 */
export const fetchGroupById = async (groupId: number): Promise<Group> => {
  const response = await axiosInstance.get<Group>(`/groups/${groupId}/`);
  return response.data;
};

/**
 * Create a new group
 */
export const createGroup = async (data: Partial<Group>): Promise<Group> => {
  const response = await axiosInstance.post<Group>('/groups/', data);
  return response.data;
};

/**
 * Fetch transactions for a group
 */
export const fetchTransactions = async (groupId?: number): Promise<Transaction[]> => {
  const url = groupId ? `/transactions/?group_id=${groupId}` : '/transactions/';
  const response = await axiosInstance.get<PaginatedResponse<Transaction>>(url);
  return response.data.results;
};

/**
 * Create a new transaction
 */
export const createTransaction = async (data: Partial<Transaction>): Promise<Transaction> => {
  const response = await axiosInstance.post<Transaction>('/transactions/', data);
  return response.data;
};
