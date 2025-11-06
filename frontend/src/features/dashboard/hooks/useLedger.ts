import { useState, useEffect } from 'react';
import { fetchTransactions } from '../api/dashboardAPI';
import type { Transaction } from '../../../types';

/**
 * Custom hook for managing ledger/transactions data
 */
export const useLedger = (groupId?: number) => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const loadTransactions = async () => {
      try {
        setIsLoading(true);
        const data = await fetchTransactions(groupId);
        setTransactions(data);
        setError(null);
      } catch (err) {
        setError(err as Error);
        console.error('Failed to load transactions:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadTransactions();
  }, [groupId]);

  const refetch = async () => {
    try {
      setIsLoading(true);
      const data = await fetchTransactions(groupId);
      setTransactions(data);
      setError(null);
    } catch (err) {
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    transactions,
    isLoading,
    error,
    refetch,
  };
};
