// TypeScript types specific to dashboard feature

import type { Transaction, Group, GroupMember } from '../../../types';

export interface LedgerStats {
  totalIncome: number;
  totalExpenses: number;
  balance: number;
  transactionCount: number;
}

export interface DashboardData {
  groups: Group[];
  recentTransactions: Transaction[];
  stats: LedgerStats;
}

export type { Transaction, Group, GroupMember };
