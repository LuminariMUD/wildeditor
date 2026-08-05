import { createClient, type SupabaseClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL?.trim() || ''
const supabasePublishableKey =
  import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY?.trim() || ''

export const developmentAuthDisabled =
  import.meta.env.DEV && import.meta.env.VITE_DISABLE_AUTH === 'true'

const placeholderValues = ['your-project', 'your-development-project', 'replace-with']

const validateConfiguration = (): string | null => {
  if (developmentAuthDisabled) return null
  if (!supabaseUrl) return 'VITE_SUPABASE_URL is not configured.'
  if (!supabasePublishableKey) return 'VITE_SUPABASE_PUBLISHABLE_KEY is not configured.'
  if (placeholderValues.some(value => supabaseUrl.includes(value))) {
    return 'VITE_SUPABASE_URL still contains a placeholder.'
  }
  if (placeholderValues.some(value => supabasePublishableKey.includes(value))) {
    return 'VITE_SUPABASE_PUBLISHABLE_KEY still contains a placeholder.'
  }

  try {
    const url = new URL(supabaseUrl)
    if (!['http:', 'https:'].includes(url.protocol)) {
      return 'VITE_SUPABASE_URL must use HTTP or HTTPS.'
    }
    if (import.meta.env.PROD && url.protocol !== 'https:') {
      return 'VITE_SUPABASE_URL must use HTTPS in production.'
    }
  } catch {
    return 'VITE_SUPABASE_URL is not a valid URL.'
  }

  return null
}

export const authConfigurationError = validateConfiguration()

export const supabase: SupabaseClient | null =
  !developmentAuthDisabled && !authConfigurationError
    ? createClient(supabaseUrl, supabasePublishableKey, {
        auth: {
          autoRefreshToken: true,
          persistSession: true,
          detectSessionInUrl: true,
        },
      })
    : null
