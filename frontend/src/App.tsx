import { AuthProvider } from './providers/AuthProvider';
import { AppRoutes } from './routes';
import './styles/global.css';

/**
 * Main application component that ties everything together
 */
function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}

export default App;
