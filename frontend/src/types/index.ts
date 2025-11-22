// Global application-wide TypeScript interfaces and types

export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  date_joined: string;
}

export interface Group {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  member_count?: number;
}

export interface Transaction {
  id: number;
  group: number;
  created_by: number;
  amount: number;
  description: string;
  transaction_type: 'income' | 'expense' | 'transfer';
  created_at: string;
}

export interface GroupMember {
  id: number;
  user: number;
  group: number;
  role: 'admin' | 'member';
  joined_at: string;
}
