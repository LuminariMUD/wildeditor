import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import type { Session, User } from '@supabase/supabase-js'

import {
  authConfigurationError,
  developmentAuthDisabled,
  supabase,
} from '../lib/supabase'
import { apiClient } from '../services/api'
import { chatAPI } from '../services/chatAPI'
import {
  AuthContext,
  type AuthContextValue,
  type AuthDataResult,
  type AuthOperationResult,
} from './auth-context'

const mockUser = {
  id: 'dev-user',
  email: 'dev@localhost',
  aud: 'authenticated',
  role: 'authenticated',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  app_metadata: { app_role: 'admin' },
  user_metadata: {},
} as User

const mockSession = {
  access_token: 'dev-token',
  refresh_token: 'dev-refresh',
  expires_in: 3600,
  expires_at: Math.floor(Date.now() / 1000) + 3600,
  token_type: 'bearer',
  user: mockUser,
} as Session

const synchronizeServiceClients = (nextSession: Session | null) => {
  apiClient.setToken(nextSession?.access_token)
  chatAPI.setToken(nextSession?.access_token)
}

// Development bypass renders the editor immediately, so initialize its
// clients before any child effect can issue a request.
if (developmentAuthDisabled) {
  synchronizeServiceClients(mockSession)
}

const authCallbackUrl =
  import.meta.env.VITE_AUTH_CALLBACK_URL || `${window.location.origin}/auth/callback`
const passwordRecoveryUrl =
  import.meta.env.VITE_PASSWORD_RECOVERY_URL || `${window.location.origin}/reset-password`

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(
    developmentAuthDisabled ? mockUser : null,
  )
  const [session, setSession] = useState<Session | null>(
    developmentAuthDisabled ? mockSession : null,
  )
  const [loading, setLoading] = useState(
    !developmentAuthDisabled && supabase !== null,
  )
  const signupEnabled = import.meta.env.VITE_AUTH_SIGNUP_ENABLED === 'true'

  const applySession = useCallback((nextSession: Session | null) => {
    // Update the request clients before publishing the session to children.
    // Otherwise a child session effect can race the provider effect and send
    // its first protected request without the freshly issued access token.
    synchronizeServiceClients(nextSession)
    setSession(nextSession)
    setUser(nextSession?.user ?? null)
  }, [])

  useEffect(() => {
    if (developmentAuthDisabled || !supabase) {
      return
    }

    let active = true
    void supabase.auth.getSession().then(({ data, error }) => {
      if (!active) return
      if (error) {
        applySession(null)
      } else {
        applySession(data.session)
      }
      setLoading(false)
    })

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      if (!active) return
      applySession(nextSession)
      setLoading(false)
    })

    return () => {
      active = false
      subscription.unsubscribe()
    }
  }, [applySession])

  const signUp = useCallback(
    async (email: string, password: string): Promise<AuthDataResult> => {
      if (developmentAuthDisabled) {
        return { data: { user: mockUser, session: mockSession }, error: null }
      }
      if (!signupEnabled) {
        return {
          data: null,
          error: new Error('New accounts are invite-only. Contact an administrator.'),
        }
      }
      if (!supabase) return { data: null, error: new Error('Authentication is not configured.') }

      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: { emailRedirectTo: authCallbackUrl },
      })
      if (!error) applySession(data.session)
      return { data, error }
    },
    [applySession, signupEnabled],
  )

  const signIn = useCallback(
    async (email: string, password: string): Promise<AuthDataResult> => {
      if (developmentAuthDisabled) {
        return { data: { user: mockUser, session: mockSession }, error: null }
      }
      if (!supabase) return { data: null, error: new Error('Authentication is not configured.') }
      const { data, error } = await supabase.auth.signInWithPassword({ email, password })
      if (!error) applySession(data.session)
      return { data, error }
    },
    [applySession],
  )

  const signOut = useCallback(async (): Promise<AuthOperationResult> => {
    if (developmentAuthDisabled) return { error: null }
    if (!supabase) return { error: new Error('Authentication is not configured.') }
    const { error } = await supabase.auth.signOut()
    if (!error) applySession(null)
    return { error }
  }, [applySession])

  const resetPassword = useCallback(
    async (email: string): Promise<AuthOperationResult> => {
      if (developmentAuthDisabled) return { error: null }
      if (!supabase) return { error: new Error('Authentication is not configured.') }
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: passwordRecoveryUrl,
      })
      return { error }
    },
    [],
  )

  const updatePassword = useCallback(
    async (password: string): Promise<AuthOperationResult> => {
      if (developmentAuthDisabled) return { error: null }
      if (!supabase) return { error: new Error('Authentication is not configured.') }
      const { error } = await supabase.auth.updateUser({ password })
      return { error }
    },
    [],
  )

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      session,
      loading,
      signupEnabled,
      configurationError: authConfigurationError,
      signUp,
      signIn,
      signOut,
      resetPassword,
      updatePassword,
    }),
    [
      user,
      session,
      loading,
      signupEnabled,
      signUp,
      signIn,
      signOut,
      resetPassword,
      updatePassword,
    ],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
