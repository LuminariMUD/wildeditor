import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || ''
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || ''
const authDisabled = import.meta.env.VITE_DISABLE_AUTH === 'true'

// ============================================
// AGGRESSIVE BROWSER CONSOLE ERROR DETECTION
// ============================================

// Create a very visible error message in console
const createErrorBlock = (title: string, messages: string[]) => {
  console.error(`
%c🔴🔴🔴 ${title} 🔴🔴🔴
%c
${messages.map(msg => `  ❌ ${msg}`).join('\n')}

%c🔥 THIS WILL BREAK AUTHENTICATION 🔥`, 
    'background: #ff0000; color: #ffffff; font-size: 20px; font-weight: bold; padding: 10px;',
    'background: #330000; color: #ff6666; font-size: 14px; padding: 10px;',
    'background: #ff0000; color: #ffffff; font-size: 16px; font-weight: bold; padding: 10px;'
  )
}

// Check for common misconfigurations
const configErrors: string[] = []

// Test if values are actually masked strings
if (!authDisabled && supabaseUrl && supabaseUrl.includes('*')) {
  configErrors.push(`VITE_SUPABASE_URL appears to be masked: "${supabaseUrl}"`)
}
if (!authDisabled && supabaseAnonKey && supabaseAnonKey.includes('*')) {
  configErrors.push(`VITE_SUPABASE_ANON_KEY appears to be masked: "${supabaseAnonKey}"`)
}

if (!authDisabled && !supabaseUrl) {
  configErrors.push('VITE_SUPABASE_URL is NOT SET')
} else if (!authDisabled && supabaseUrl === 'your_supabase_project_url') {
  configErrors.push('VITE_SUPABASE_URL still has placeholder value')
} else if (!authDisabled && !supabaseUrl.includes('supabase.co')) {
  configErrors.push("VITE_SUPABASE_URL doesn't look like a Supabase URL")
}

if (!authDisabled && !supabaseAnonKey) {
  configErrors.push('VITE_SUPABASE_ANON_KEY is NOT SET')
} else if (!authDisabled && supabaseAnonKey.length < 100) {
  configErrors.push(`VITE_SUPABASE_ANON_KEY looks too short (${supabaseAnonKey.length} chars)`)
}

// Show massive errors if config is wrong
if (configErrors.length > 0) {
  createErrorBlock('SUPABASE CONFIGURATION ERROR', configErrors)
  
  console.group('%c🔧 HOW TO FIX THIS', 'color: #00ff00; font-weight: bold; font-size: 16px;')
  console.log('%c1. Create or update apps/frontend/.env file:', 'color: #00ff00; font-weight: bold;')
  console.log(`%cVITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here`, 'background: #003300; color: #00ff00; padding: 5px; font-family: monospace;')
  console.log('%c2. Get these values from:', 'color: #00ff00; font-weight: bold;')
  console.log('   - Go to https://supabase.com/dashboard')
  console.log('   - Select your project')
  console.log('   - Go to Settings → API')
  console.log('   - Copy "Project URL" and "anon public" key')
  console.log('%c3. Restart your dev server after updating .env', 'color: #00ff00; font-weight: bold;')
  console.groupEnd()
  
  // Set a global flag for the auth form to check
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ;(window as any).__SUPABASE_CONFIG_ERROR__ = true
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ;(window as any).__SUPABASE_CONFIG_ERRORS__ = configErrors
}

if (!authDisabled && (!supabaseUrl || !supabaseAnonKey || supabaseUrl === 'your_supabase_project_url')) {
  console.warn('⚠️  Supabase environment variables not configured properly')
  console.warn('⚠️  Please update apps/frontend/.env with your actual Supabase credentials')
  console.warn('⚠️  Running in demo mode - authentication will not work')
}

// Validate URL before creating client
const isValidUrl = (url: string) => {
  try {
    new URL(url)
    return true
  } catch {
    return false
  }
}

// Create a dummy client if credentials are not set - this prevents runtime errors
export const supabase = (supabaseUrl && supabaseAnonKey && isValidUrl(supabaseUrl) && supabaseUrl !== 'your_supabase_project_url')
  ? createClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        autoRefreshToken: true,
        persistSession: true,
        detectSessionInUrl: true
      }
    })
  : null as unknown as ReturnType<typeof createClient>
