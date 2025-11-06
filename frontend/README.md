# CharmPlus Frontend

React + TypeScript frontend for the CharmPlus application - a group-based financial management system.

## Project Structure

```
champlus-frontend/
├── .env                  # Environment variables (VITE_API_BASE_URL, etc.)
├── .eslintrc.cjs         # ESLint configuration
├── .gitignore            # Git ignore file
├── index.html            # HTML entry point for the SPA
├── package.json          # Dependencies and scripts
├── README.md             # This file
├── tsconfig.json         # TypeScript compiler configuration
├── tsconfig.node.json    # TypeScript config for Node-specific files
├── vite.config.ts        # Vite build tool configuration
│
└── src/                  # Source code directory
    ├── @types/           # Custom global TypeScript type declarations
    │   └── index.d.ts
    │
    ├── assets/           # Static assets (images, icons, fonts)
    │
    ├── components/       # Global, shared, reusable UI components
    │   ├── layout/       # Layout components (Navbar.tsx, Sidebar.tsx)
    │   └── ui/           # UI primitives (Button.tsx, Card.tsx, Input.tsx)
    │
    ├── features/         # Feature-based architecture (self-contained modules)
    │   ├── authentication/
    │   │   ├── api/      # authAPI.ts - Backend endpoint calls
    │   │   ├── components/ # LoginForm.tsx - Feature-specific components
    │   │   ├── types/    # index.ts - TypeScript types for auth
    │   │   └── LoginPage.tsx
    │   │
    │   └── dashboard/
    │       ├── api/      # dashboardAPI.ts
    │       ├── components/ # LedgerTable.tsx, StatsCard.tsx
    │       ├── hooks/    # useLedger.ts - Custom hooks
    │       ├── types/    # index.ts - Types for dashboard
    │       └── DashboardPage.tsx
    │
    ├── hooks/            # Global custom hooks
    │   ├── useAuth.ts
    │   └── useLocalStorage.ts
    │
    ├── lib/              # Library configurations and helper instances
    │   └── axios.ts      # Pre-configured Axios with interceptors
    │
    ├── providers/        # React Context providers
    │   └── AuthProvider.tsx
    │
    ├── routes/           # Centralized route configuration
    │   ├── index.tsx     # Route definitions
    │   └── ProtectedRoute.tsx
    │
    ├── styles/           # Global styles and theme
    │   └── global.css
    │
    ├── types/            # Global TypeScript interfaces
    │   ├── api.ts        # API response types
    │   └── index.ts      # User, Group, Transaction types
    │
    ├── App.tsx           # Main application component
    └── main.tsx          # Entry point of the React application
```

## Technology Stack

- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client

## Setup Instructions

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

1. **Navigate to frontend directory**
   ```bash
   cd champlus-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   Edit `.env` and update `VITE_API_BASE_URL` if needed.

4. **Start the development server**
   ```bash
   npm run dev
   ```

The application will be available at `http://localhost:5173/`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Environment Variables

- `VITE_API_BASE_URL` - Backend API base URL (default: `http://localhost:8000/api/v1`)

## License

[Your License Here]
