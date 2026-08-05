import { useState, type FormEvent } from 'react'
import { AlertCircle, CheckCircle, Lock, MapPin } from 'lucide-react'

import { useAuth } from '../hooks/useAuth'

export const PasswordRecovery = () => {
  const { loading: authLoading, session, updatePassword } = useAuth()
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [complete, setComplete] = useState(false)

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    const result = await updatePassword(password)
    setSubmitting(false)
    if (result.error) {
      setError(result.error.message)
      return
    }
    setComplete(true)
  }

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-gray-800 rounded-lg shadow-xl p-8">
        <div className="text-center mb-8">
          <div className="mx-auto w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mb-4">
            <MapPin className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white">Set a new password</h1>
        </div>

        {complete ? (
          <div className="text-center">
            <CheckCircle className="w-12 h-12 text-green-400 mx-auto mb-3" />
            <p className="text-gray-200 mb-5">Your password has been updated.</p>
            <a className="text-blue-400 hover:text-blue-300" href="/">Return to the editor</a>
          </div>
        ) : authLoading ? (
          <p className="text-gray-300 text-center">Validating the recovery link…</p>
        ) : !session ? (
          <div className="text-center">
            <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
            <p className="text-red-300">This recovery link is invalid or expired.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {error ? <p className="text-red-300 text-sm">{error}</p> : null}
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="password"
                value={password}
                onChange={event => setPassword(event.target.value)}
                minLength={8}
                required
                autoComplete="new-password"
                placeholder="New password"
                className="w-full pl-10 pr-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white"
              />
            </div>
            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white py-3 rounded-lg"
            >
              {submitting ? 'Updating…' : 'Update password'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
