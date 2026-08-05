/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string
  readonly VITE_CHAT_API_URL?: string
  readonly VITE_SUPABASE_URL?: string
  readonly VITE_SUPABASE_PUBLISHABLE_KEY?: string
  readonly VITE_AUTH_CALLBACK_URL?: string
  readonly VITE_PASSWORD_RECOVERY_URL?: string
  readonly VITE_AUTH_SIGNUP_ENABLED?: string
  readonly VITE_DISABLE_AUTH?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
