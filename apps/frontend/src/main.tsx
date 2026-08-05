/* eslint-disable react-refresh/only-export-components */
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import { AuthProvider } from './contexts/AuthContext.tsx';
import { AuthCallback } from './components/AuthCallback.tsx';
import { PasswordRecovery } from './components/PasswordRecovery.tsx';

const pathname = window.location.pathname;
const RootComponent = pathname === '/auth/callback'
  ? AuthCallback
  : pathname === '/reset-password'
    ? PasswordRecovery
    : App;

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <RootComponent />
    </AuthProvider>
  </StrictMode>
);
