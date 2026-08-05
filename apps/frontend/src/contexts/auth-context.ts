import { createContext } from 'react'
import type { AuthError, Session, User } from '@supabase/supabase-js'

type OperationError = AuthError | Error | null

export interface AuthDataResult {
  data: { user: User | null; session: Session | null } | null
  error: OperationError
}

export interface AuthOperationResult {
  error: OperationError
}

export interface AuthContextValue {
  user: User | null
  session: Session | null
  loading: boolean
  signupEnabled: boolean
  configurationError: string | null
  signUp: (email: string, password: string) => Promise<AuthDataResult>
  signIn: (email: string, password: string) => Promise<AuthDataResult>
  signOut: () => Promise<AuthOperationResult>
  resetPassword: (email: string) => Promise<AuthOperationResult>
  updatePassword: (password: string) => Promise<AuthOperationResult>
}

export const AuthContext = createContext<AuthContextValue | null>(null)
