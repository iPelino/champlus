import { useAuth as useAuthContext } from '../providers/AuthProvider';

// Re-export the useAuth hook from AuthProvider for convenience
export const useAuth = useAuthContext;
